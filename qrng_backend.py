# app.py
import os, base64, math, logging, random, hmac, hashlib, json, time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Any

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
try:
    # Optional hardening extras (safe to omit in local dev)
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    HARDENING_AVAILABLE = True
except Exception:
    HARDENING_AVAILABLE = False

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Project-specific quantum core (as in original)
from quantum_core import QuantumRandomNumberGenerator, E91Protocol, BB84Protocol

# Optional Qiskit import for circuit drawing/sampling (as in original)
try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except Exception:
    QISKIT_AVAILABLE = False

# -----------------------------------------------------------------------------
# Configuration and logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("qrng-backend")

app = Flask(__name__)
# Restrict CORS to the local dashboard origin by default
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:8050", "http://localhost:8050"]}})

if HARDENING_AVAILABLE:
    # Lightweight rate limiting defaults; tune per deployment
    limiter = Limiter(get_remote_address, app=app, default_limits=["120 per minute"])

qrng = QuantumRandomNumberGenerator()
e91_protocol = E91Protocol()
bb84_protocol = BB84Protocol()

# Policy thresholds (set from 90B estimator reports during commissioning)
ENTROPY_THRESHOLD = 0.90     # UI threshold only
QBER_THRESHOLD = 0.11        # abort threshold typical of BB84-class analysis bands
MIN_ENTROPY_PER_BIT = 0.80   # conservative floor until lab 90B report refines

SESSION_KEY_BYTES = None

# Local store for dataset captures (hashes/paths) and sustainability measurements
CAPTURE_DIR = os.path.abspath("./captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)
DATASET_HASHES = {"raw": None, "cond": None, "restart": None}
SUSTAIN = {"window_start": None, "window_end": None, "kwh": 0.0,
           "ef_loc": None, "ef_mkt": None, "co2_loc": None, "co2_mkt": None}

# -----------------------------------------------------------------------------
# 90B online health tests (policy-oriented RCT/AP)
# -----------------------------------------------------------------------------
@dataclass
class HealthState:
    ok: bool = True
    reason: str = ""
    rct_cutoff: int = 0
    ap_window: int = 1024
    ap_cutoff: int = 0

health = HealthState()

def repetition_count_test(bits: str, cutoff: int) -> bool:
    if not bits:
        return False
    run = 1
    maxrun = 1
    for i in range(1, len(bits)):
        if bits[i] == bits[i-1]:
            run += 1
            if run > maxrun:
                maxrun = run
                if maxrun >= cutoff:
                    return False
        else:
            run = 1
    return True

def adaptive_proportion_test(bits: str, window: int, cutoff: int) -> bool:
    if len(bits) < window or window <= 0:
        return True
    # Reference bit can be policy-chosen; here use '0' to be conservative in imbalance checks
    ref = '0'
    for i in range(0, len(bits) - window + 1, window):
        block = bits[i:i+window]
        if block.count(ref) >= cutoff:
            return False
    return True

def set_health_from_bits(bits: str, min_entropy_per_bit: float) -> bool:
    # Illustrative mapping; in deployment set from lab-derived 90B estimator and tuning tables
    rct_cutoff = max(6, int(1 + 30 / max(min_entropy_per_bit, 0.05)))
    ap_window  = 1024
    # Cutoff = max allowed count of a reference symbol in a window; tune from 90B analysis
    ap_cutoff  = max(40, int(1024 * (0.5 + (0.5 - min_entropy_per_bit/2.0))))
    ok_rct = repetition_count_test(bits, rct_cutoff)
    ok_ap  = adaptive_proportion_test(bits, ap_window, ap_cutoff)
    health.ok = bool(ok_rct and ok_ap)
    health.reason = "" if health.ok else f"RCT/AP violation (rct_cutoff={rct_cutoff}, ap_cutoff={ap_cutoff})"
    health.rct_cutoff = rct_cutoff
    health.ap_window = ap_window
    health.ap_cutoff = ap_cutoff
    return health.ok

# -----------------------------------------------------------------------------
# Extractor-based key derivation (HKDF per RFC 5869)
# -----------------------------------------------------------------------------
def hkdf_sha256_extract_expand(ikm_bits: str, out_len: int, salt: bytes = None, info: bytes = b"QRNG-KEY") -> bytes:
    # HKDF-Extract then HKDF-Expand (RFC 5869)
    if salt is None:
        salt = os.urandom(16)
    pad = (-len(ikm_bits)) % 8
    ikm_bits_padded = ikm_bits + ("0" * pad)
    ikm = int(ikm_bits_padded, 2).to_bytes(len(ikm_bits_padded)//8, "big")
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    okm = b""
    t = b""
    counter = 1
    while len(okm) < out_len:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        okm += t
        counter += 1
    return okm[:out_len]

# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------
def _clean_series(seq):
    out = []
    for v in (seq or []):
        try:
            fv = float(v)
            if math.isfinite(fv):
                out.append(fv)
        except Exception:
            continue
    return out

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# -----------------------------------------------------------------------------
# Anomaly detection (unchanged logic; thresholds wired to policy)
# -----------------------------------------------------------------------------
def detect_anomalies(entropy_history: list, qber_history: list) -> dict:
    ent = _clean_series(entropy_history)
    qbr = _clean_series(qber_history)
    alerts = []
    recent_entropy = ent[-1] if ent else None
    recent_qber = qbr[-1] if qbr else None
    if ent:
        if recent_entropy is not None and recent_entropy < ENTROPY_THRESHOLD:
            alerts.append(f"Low entropy detected: {float(recent_entropy):.3f} (expected >{ENTROPY_THRESHOLD})")
        window = ent[-min(5, len(ent)):]
        if len(window) >= 2:
            try:
                y = np.asarray(window, dtype=float).ravel()
                if np.isfinite(y).all() and y.size >= 2:
                    x = np.arange(y.size, dtype=float)
                    slope = float(np.polyfit(x, y, 1))
                    if slope < -0.01:
                        alerts.append("Declining entropy trend - possible hardware degradation")
            except Exception as e:
                log.debug(f"polyfit skipped in anomaly detection: {e}")
    if qbr and recent_qber is not None:
        if recent_qber > QBER_THRESHOLD:
            alerts.append(f"High QBER detected: {float(recent_qber):.3f} (threshold: {QBER_THRESHOLD})")
            alerts.append("Possible eavesdropping attempt or channel noise")
    return {
        "alerts": alerts,
        "status": "ALERT" if alerts else "NORMAL",
        "entropy_level": recent_entropy,
        "qber_level": recent_qber,
        "security_assessment": "COMPROMISED" if alerts else "SECURE",
    }

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route('/qrng/circuit', methods=['GET'])
def qrng_circuit():
    try:
        shots = int(request.args.get('shots', 32))
        if QISKIT_AVAILABLE:
            qc = QuantumCircuit(1, 1)
            qc.h(0)
            qc.measure(0, 0)
            ascii_circ = str(qc.draw(output='text'))
            sim = AerSimulator()
            result = sim.run(qc, shots=shots, memory=True).result()
            try:
                memory = result.get_memory()
            except Exception:
                memory = result.get_memory(0)
            if memory is None:
                counts = result.get_counts()
                z, o = counts.get('0', 0), counts.get('1', 0)
                total = max(z + o, 1)
                p0, p1 = z / total, o / total
                rng = np.random.default_rng()
                memory = rng.choice(['0', '1'], size=shots, p=[p0, p1]).tolist()
            bits = ''.join(str(b) for b in memory)
        else:
            ascii_circ = "     ┌───┐┌─┐\nq:  ─┤ H ├┤M├\n     └───┘└╥┘\nc: 1/══════╩═\n           0"
            bits = ''.join(random.choice('01') for _ in range(shots))
        return jsonify({"ascii_circuit": ascii_circ, "bits": bits})
    except Exception as e:
        log.error(f"Circuit endpoint error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "OK",
        "service": "QRNG Defense System",
        "version": "2.0.0",
        "foundation": "Quantum Random Number Generator",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        "backend": type(qrng.backend).__name__,
        "ready_for": ["Military Communications", "Satellite Links", "Naval Systems", "AI Monitoring"]
    })

@app.route('/rng', methods=['GET'])
def generate_random_bits():
    try:
        shots = int(request.args.get('shots', 1024))
        num_bits = int(request.args.get('bits', 32))
        bits, counts = qrng.generate_random_bits(num_bits=num_bits, shots=shots)
        # Online health gate on the produced bitstring
        set_health_from_bits(bits, MIN_ENTROPY_PER_BIT)
        entropy = qrng.calculate_entropy(counts)
        randomness_tests = qrng.test_randomness(bits)

        perf = qrng.get_performance_metrics()
        # Sustainability is now handled by a dedicated endpoint; keep demo numbers minimal here
        classical_energy = num_bits * 0.001
        quantum_energy = num_bits * 0.0001
        energy_savings = max(0.0, classical_energy - quantum_energy)
        co2_reduction = energy_savings * 0.5

        return jsonify({
            "status": "SUCCESS",
            "foundation": "Quantum Random Number Generator",
            "bits": bits,
            "bit_count": len(bits),
            "distribution": {"0": counts.get("0", 0), "1": counts.get("1", 0)},
            "entropy": entropy,
            "online_health": {"ok": health.ok, "reason": health.reason,
                              "rct_cutoff": health.rct_cutoff,
                              "ap_window": health.ap_window,
                              "ap_cutoff": health.ap_cutoff},
            "randomness_quality": {
                "defense_grade": randomness_tests.get("defense_grade", False),
                "frequency_balance": randomness_tests.get("frequency"),
                "complexity": randomness_tests.get("complexity"),
                "max_run_length": randomness_tests.get("max_run_length"),
            },
            "performance": {
                "shots_used": shots,
                "generation_time": perf.get("average_time_per_bit", 0) * num_bits,
                "total_generated": perf.get("total_bits_generated", 0),
            },
            "environmental_impact": {
                "energy_saved_kwh": energy_savings,
                "co2_reduced_kg": co2_reduction,
                "efficiency_advantage": "Illustrative; see /sustainability/report for auditable data"
            },
            "applications": ["Military Cryptography", "Secure Communications", "AI Monitoring", "Protocol Validation"]
        })
    except Exception as e:
        log.error(f"QRNG generation error: {e}", exc_info=True)
        return jsonify({"error": str(e), "foundation": "QRNG service unavailable"}), 500

@app.route('/rng/bytes', methods=['POST'])
def rng_bytes():
    try:
        req = request.get_json(silent=True) or {}
        nbytes = int(req.get("nbytes", 32))
        nbits = max(8, nbytes * 8)
        bits, _ = qrng.generate_random_bits(num_bits=nbits, shots=max(1024, nbits*2))
        # Health check
        if not set_health_from_bits(bits, MIN_ENTROPY_PER_BIT):
            return jsonify({"error": "Entropy source health alarm", "reason": health.reason}), 503
        # Expand via HKDF to byte-oriented output
        okm = hkdf_sha256_extract_expand(bits, nbytes, info=b"QRNG-RNG-BYTES")
        return jsonify({"status": "SUCCESS", "nbytes": nbytes,
                        "bytes_b64": base64.b64encode(okm).decode("utf-8"),
                        "online_health": {"ok": health.ok, "reason": health.reason}})
    except Exception as e:
        log.error(f"/rng/bytes error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/qkd', methods=['GET'])
def quantum_key_distribution():
    try:
        shots = int(request.args.get('shots', 1024))
        protocol = request.args.get('protocol', 'e91').lower()
        if protocol == 'e91':
            result = e91_protocol.run_e91_protocol(num_rounds=shots // 20)
            return jsonify({
                "protocol": "E91 (Recommended for Defense)",
                "foundation": "QRNG-enabled quantum entanglement",
                "shared_key_preview": result["shared_key"][:32],
                "key_length": result["sifted_key_length"],
                "qber": result["qber"],
                "secure": result["qber"] < QBER_THRESHOLD,
                "protocol_time": result["protocol_time"],
                "efficiency": result["efficiency"],
                "advantages": [
                    "Built-in eavesdropping detection via Bell tests",
                    "Quantum entanglement security",
                    "Resilience to intercept-resend attacks",
                    "Continuous QBER monitoring"
                ],
                "use_cases": ["Satellite Communications", "Naval Command Links", "Airborne Secure Links"],
                "rounds": result["total_rounds"]
            })
        else:
            result = bb84_protocol.run_bb84_protocol(num_bits=shots // 10)
            return jsonify({
                "protocol": "BB84",
                "foundation": "QRNG-enabled photon polarization",
                "key_preview": result.get("key_preview", "")[:32],
                "key_length": result["sifted_key_length"],
                "qber": result["qber"],
                "secure": result["qber"] < QBER_THRESHOLD,
                "efficiency": result["efficiency"]
            })
    except Exception as e:
        log.error(f"QKD protocol error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/e91/chsh', methods=['GET'])
def e91_bell_test():
    try:
        shots = int(request.args.get('shots', 4096))
        result = e91_protocol.bell_test_chsh(shots=shots)
        # Minimal CI proxy (placeholder; refine with binomial propagation on correlations)
        S = float(result["S"])
        S_ci = [S - 0.05, S + 0.05]
        alarm = S < 2.1
        return jsonify({
            "test": "CHSH Bell Inequality",
            "foundation": "Quantum entanglement validation",
            "shots": shots,
            "S_parameter": S,
            "S_ci95": S_ci,
            "bell_violation": result["bell_violation"],
            "classical_limit": result["classical_limit"],
            "quantum_limit": result["quantum_limit"],
            "security_level": result["security_level"],
            "security_margin": result["security_margin"],
            "alarm": alarm,
            "correlations": result["correlations"],
            "status": "QUANTUM_SECURITY_VALIDATED" if result["bell_violation"] else "CLASSICAL_ONLY"
        })
    except Exception as e:
        log.error(f"Bell test error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/e91/key', methods=['GET'])
def e91_key_generation():
    try:
        shots = int(request.args.get('shots', 2048))
        noise = float(request.args.get('noise', 0.0))
        result = e91_protocol.run_e91_protocol(num_rounds=shots // 20)
        if noise > 0:
            key_bits = list(result["shared_key"])
            for i in range(len(key_bits)):
                if np.random.random() < noise:
                    key_bits[i] = "1" if key_bits[i] == "0" else "0"
            result["shared_key"] = "".join(key_bits)
            result["qber"] = min(result["qber"] + noise, 1.0)
        secure = result["qber"] < QBER_THRESHOLD
        return jsonify({
            "protocol": "E91 Quantum Key Generation",
            "foundation": "QRNG-powered entanglement",
            "key_length": result["sifted_key_length"],
            "key_preview": result["shared_key"][:64],
            "qber": result["qber"],
            "secure": secure,
            "noise_simulation": noise,
            "security_assessment": "MILITARY_GRADE" if secure else "COMPROMISED",
            "recommended_use": "Classified Communications" if secure else "Training Only"
        })
    except Exception as e:
        log.error(f"E91 key generation error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/ai/anomaly', methods=['POST'])
def anomaly_detection():
    try:
        data = request.get_json(silent=True) or {}
        entropy_hist = data.get('entropy', [])
        qber_hist = data.get('qber', [])
        result = detect_anomalies(entropy_hist, qber_hist)
        return jsonify({
            "service": "AI Anomaly Detection",
            "foundation": "QRNG pattern analysis",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            "alerts": result["alerts"],
            "status": result["status"],
            "security_assessment": result["security_assessment"],
            "metrics": {
                "entropy_level": result["entropy_level"],
                "qber_level": result["qber_level"]
            }
        })
    except Exception as e:
        log.error(f"Anomaly detection error: {e}", exc_info=True)
        return jsonify({
            "service": "AI Anomaly Detection",
            "status": "ERROR",
            "alerts": [f"Anomaly module encountered an error: {str(e)}"],
            "metrics": {"entropy_level": None, "qber_level": None}
        })

# ---- Key management with HKDF and health gate --------------------------------
@app.route('/crypto/set_key', methods=['POST'])
def set_encryption_key():
    global SESSION_KEY_BYTES
    try:
        data = request.get_json(silent=True) or {}
        bitstring = data.get("bitstring", "")
        if not bitstring:
            return jsonify({"error": "No quantum bitstring provided"}), 400
        # Enforce online health gate and policy min-entropy
        if not set_health_from_bits(bitstring, MIN_ENTROPY_PER_BIT):
            return jsonify({"error": "Entropy source health alarm", "reason": health.reason}), 503
        # HKDF-based key derivation; no entropy-diluting zero padding beyond byte packing
        SESSION_KEY_BYTES = hkdf_sha256_extract_expand(bitstring, 32, info=b"QRNG-SESSION-KEY")
        return jsonify({
            "status": "SUCCESS",
            "foundation": "Quantum-derived cryptographic key",
            "key_source": "QRNG-generated random bits",
            "kdf": "HKDF-SHA256 (RFC5869)",
            "key_length_bytes": len(SESSION_KEY_BYTES),
            "key_length_bits": len(SESSION_KEY_BYTES) * 8,
            "online_health": {"ok": health.ok, "reason": health.reason},
            "security_level": "AES-256-GCM with quantum entropy",
            "applications": ["Classified messaging", "Satellite communications", "Naval command links"]
        })
    except Exception as e:
        log.error(f"Key setting error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/crypto/encrypt', methods=['POST'])
def encrypt_message():
    global SESSION_KEY_BYTES
    try:
        if SESSION_KEY_BYTES is None:
            return jsonify({"error": "No quantum key set. Call /crypto/set_key first."}), 400
        data = request.get_json(silent=True) or {}
        message = data.get("message", "")
        if not message:
            return jsonify({"error": "No message provided"}), 400
        aesgcm = AESGCM(SESSION_KEY_BYTES)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, message.encode("utf-8"), None)
        return jsonify({
            "status": "ENCRYPTED",
            "foundation": "Quantum cryptography",
            "algorithm": "AES-256-GCM",
            "key_source": "QRNG quantum randomness",
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8")
        })
    except Exception as e:
        log.error(f"Encryption error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/crypto/decrypt', methods=['POST'])
def decrypt_message():
    global SESSION_KEY_BYTES
    try:
        if SESSION_KEY_BYTES is None:
            return jsonify({"error": "No quantum key available"}), 400
        data = request.get_json(silent=True) or {}
        nonce_b64 = data.get("nonce", "")
        ciphertext_b64 = data.get("ciphertext", "")
        if not nonce_b64 or not ciphertext_b64:
            return jsonify({"error": "Missing nonce or ciphertext"}), 400
        aesgcm = AESGCM(SESSION_KEY_BYTES)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        message = plaintext.decode("utf-8")
        return jsonify({
            "status": "DECRYPTED",
            "foundation": "Quantum cryptography",
            "message": message,
            "verification": "Quantum key authentication successful",
            "integrity": "Message authenticated and verified"
        })
    except Exception as e:
        log.error(f"Decryption error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ---- Defense status (cosmetic/demo) ------------------------------------------
@app.route('/defense/status', methods=['GET'])
def defense_communications_status():
    platforms = [
        {"name":"Satellite Communications","emoji":"🛰️","status":random.choice(["Secure","Monitoring","Key Refresh"]),
         "qrng_enabled":True,"encryption":"AES-256-GCM + E91 QKD",
         "last_key_exchange":(datetime.now()-timedelta(minutes=random.randint(1,30))).strftime("%H:%M IST"),
         "throughput":f"{random.uniform(2.0,5.0):.1f} Gbps","entropy_level":random.uniform(0.95,0.99),"qber":random.uniform(0.02,0.08),
         "applications":["GPS","Comms","Reconnaissance"]},
        {"name":"Naval Command","emoji":"🚢","status":random.choice(["Secure","Monitoring"]),
         "qrng_enabled":True,"encryption":"PQC: ML-KEM (Kyber-768) + AES-256-GCM",
         "last_key_exchange":(datetime.now()-timedelta(minutes=random.randint(5,45))).strftime("%H:%M IST"),
         "throughput":f"{random.uniform(1.5,3.0):.1f} Gbps","entropy_level":random.uniform(0.92,0.98),"qber":random.uniform(0.03,0.09),
         "applications":["Fleet Coordination","Sonar Data","Tactical Planning"]},
        {"name":"Airborne Systems","emoji":"✈️","status":random.choice(["Secure","Monitoring","Maintenance"]),
         "qrng_enabled":True,"encryption":"AES-256-GCM + E91 QKD",
         "last_key_exchange":(datetime.now()-timedelta(minutes=random.randint(10,60))).strftime("%H:%M IST"),
         "throughput":f"{random.uniform(0.8,2.0):.1f} Gbps","entropy_level":random.uniform(0.90,0.97),"qber":random.uniform(0.04,0.10),
         "applications":["Fighter Jets","Drones","AWACS"]},
        {"name":"Ground Control","emoji":"🏗️","status":"Secure","qrng_enabled":True,
         "encryption":"PQC: ML-KEM + ML-DSA (Dilithium)",
         "last_key_exchange":(datetime.now()-timedelta(minutes=random.randint(1,20))).strftime("%H:%M IST"),
         "throughput":f"{random.uniform(3.0,6.0):.1f} Gbps","entropy_level":random.uniform(0.96,0.99),"qber":random.uniform(0.01,0.06),
         "applications":["Command Centers","Radar Systems","Communication Hubs"]},
    ]
    total = len(platforms)
    sec = len([p for p in platforms if p["status"] == "Secure"])
    return jsonify({
        "service": "Defense Communications Status",
        "foundation": "QRNG-Secured Defense Network",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        "overall_status": "OPERATIONAL",
        "security_level": "QUANTUM_ENHANCED",
        "platforms": platforms,
        "summary": {
            "total_platforms": total,
            "secure_platforms": sec,
            "security_percentage": (sec / total) * 100.0,
            "average_entropy": sum(p["entropy_level"] for p in platforms) / total,
            "average_qber": sum(p["qber"] for p in platforms) / total,
            "quantum_advantage": "All platforms enhanced with QRNG foundation"
        }
    })

# ---- 90B dataset capture/status ----------------------------------------------
@app.route('/entropy/90b/capture', methods=['POST'])
def capture_90b():
    try:
        req = request.get_json(silent=True) or {}
        kind = req.get("kind", "raw")  # raw|cond|restart
        samples = int(req.get("samples", 1000000))
        if kind not in ("raw", "cond", "restart"):
            return jsonify({"error": "Invalid kind"}), 400

        # For demo, capture conditioned bits as a stand-in; in production wire raw tap
        bits, _ = qrng.generate_random_bits(num_bits=samples, shots=max(2*samples, 4096))
        filename = f"{kind}_{int(time.time())}_{samples}.bin"
        fpath = os.path.join(CAPTURE_DIR, filename)
        # Store compactly as bytes
        pad = (-len(bits)) % 8
        bits_padded = bits + ("0" * pad)
        data = int(bits_padded, 2).to_bytes(len(bits_padded)//8, "big")
        with open(fpath, "wb") as f:
            f.write(data)
        h = sha256_hex(data)
        DATASET_HASHES[kind] = f"sha256:{h}"
        return jsonify({"status": "CAPTURED", "kind": kind, "samples": samples,
                        "file": fpath, "sha256": h})
    except Exception as e:
        log.error(f"Capture 90B error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/entropy/90b/status', methods=['GET'])
def status_90b():
    return jsonify({
        "online_health": {"ok": health.ok, "reason": health.reason,
                          "rct_cutoff": health.rct_cutoff,
                          "ap_window": health.ap_window, "ap_cutoff": health.ap_cutoff},
        "datasets": DATASET_HASHES
    })

# ---- SP 800-22 placeholder metadata endpoint --------------------------------
@app.route('/stats/sp800-22', methods=['GET'])
def stats_sp80022():
    # Integrate external test runner in CI; publish last report metadata here
    return jsonify({
        "status": "NOT_AVAILABLE",
        "note": "Run NIST SP 800-22r1a externally and publish report here.",
        "reference": "NIST SP 800-22r1a"
    })

# ---- Sustainability reporting (Scope 2) --------------------------------------
@app.route('/sustainability/report', methods=['POST', 'GET'])
def sustainability_report():
    try:
        if request.method == 'POST':
            req = request.get_json(silent=True) or {}
            SUSTAIN["window_start"] = req.get("window_start")
            SUSTAIN["window_end"] = req.get("window_end")
            SUSTAIN["kwh"] = float(req.get("kwh", 0.0))
            SUSTAIN["ef_loc"] = float(req.get("ef_loc", 0.0))
            SUSTAIN["ef_mkt"] = float(req.get("ef_mkt", 0.0))
            SUSTAIN["co2_loc"] = SUSTAIN["kwh"] * SUSTAIN["ef_loc"]
            SUSTAIN["co2_mkt"] = SUSTAIN["kwh"] * SUSTAIN["ef_mkt"]
        return jsonify(SUSTAIN)
    except Exception as e:
        log.error(f"Sustainability report error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# ---- Runner ------------------------------------------------------------------
if __name__ == '__main__':
    # For production, place behind gunicorn/uwsgi and enforce HTTPS/CSP at proxy; debug off
    app.run(debug=False, host='127.0.0.1', port=5000)
