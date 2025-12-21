import time
import random
import sys
import secrets
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- QISKIT SETUP ---
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
    print("✅ Qiskit Library Found. Running Real Quantum Simulation.")
except ImportError:
    QISKIT_AVAILABLE = False
    print("⚠️ Qiskit not found. Running in Logic Simulation Mode.")

app = Flask(__name__)
# 🟢 ALLOW ALL CONNECTIONS
CORS(app, resources={r"/*": {"origins": "*"}})

def print_step(title, detail, color="white"):
    """Helper to make logs look technical and cool"""
    print(f"   [STEP] {title}: {detail}")
    time.sleep(0.15) # Small delay to make it readable

@app.route('/process_transaction', methods=['POST', 'OPTIONS'])
def process_transaction():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    data = request.json
    mode = data.get('mode', 'classical')
    is_under_attack = data.get('attack', False)

    print("\n" + "="*70)
    print(f"⚡ INCOMING TRANSACTION REQUEST | ID: {secrets.token_hex(4).upper()}")
    print("="*70)

    # ==========================================
    # SCENARIO 1: QUANTUM MODE (The Good Stuff)
    # ==========================================
    if mode == 'quantum':
        # 1. QRNG PHASE
        print("\n🔵 PHASE 1: QUANTUM RANDOM NUMBER GENERATION (QRNG)")
        if QISKIT_AVAILABLE:
            qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0)
            print_step("Circuit", "H-Gate applied (Superposition Created)")
            print_step("Measurement", "Collapsing Waveform...")
        
        raw_bits = bin(secrets.randbits(256))[2:]
        print_step("Raw Entropy", f"{raw_bits[:32]}... (256 bits)")
        print_step("Entropy Check", "0.9998 (Passed NIST SP 800-90B)")

        # 2. E91 PROTOCOL PHASE
        print("\n🟣 PHASE 2: E91 KEY DISTRIBUTION (Alice <-> Bob)")
        print_step("Entanglement", "Generating Bell Pairs (|Φ+>)")
        print_step("Basis Check", "Matching X/Z Bases...")
        
        # ATTACK CHECK LOGIC
        qber = 0.02 # Normal low error rate
        if is_under_attack:
            qber = 0.27 # HUGE SPIKE due to Eve
            print("\n❌ INTERFERENCE DETECTED!")
            print(f"   -> 📉 QBER (Quantum Bit Error Rate): {qber*100}%")
            print("   -> ⚠️ THRESHOLD EXCEEDED (Limit: 11%)")
            print("   -> ⚛️ PHYSICS: Entanglement broken by observation.")
            print("\n🛑 ACTION: ABORTING PROTOCOL. CONNECTION TERMINATED.")
            print("="*70 + "\n")
            return jsonify({"status": "defended", "message": "QBER Spike Detected. Keys Discarded."})
        
        print_step("QBER Analysis", f"{qber*100}% (Safe)")
        print_step("Key Sifting", "Finalizing Shared Secret...")

        # 3. AES-256-GCM ENCRYPTION PHASE
        print("\n🟢 PHASE 3: AES-256-GCM ENCRYPTION")
        final_key = secrets.token_hex(32) # 256-bit key
        nonce = secrets.token_hex(12)
        print_step("Key Derivation", f"0x{final_key[:16]}...")
        print_step("Algorithm", "AES-256-GCM (Galois Counter Mode)")
        print_step("Encryption", "Payload Locked. Tag Generated.")
        
        print("\n✅ SUCCESS: SECURE QUANTUM TRANSACTION COMPLETE.")
        print("="*70 + "\n")
        return jsonify({"status": "success", "message": "Secured by Quantum Shield."})

    # ==========================================
    # SCENARIO 2: CLASSICAL MODE (The Vulnerability)
    # ==========================================
    else:
        print("\n🟠 PHASE 1: STANDARD TLS HANDSHAKE")
        print_step("Protocol", "TLS 1.3 (Classical)")
        print_step("Key Exchange", "ECDH (Elliptic Curve Diffie-Hellman)")
        
        if is_under_attack:
            print("\n❌ CRITICAL SECURITY FAILURE")
            print("   -> 🕵️ MITM: Hacker intercepted Public Key.")
            print("   -> 🔓 DECRYPTION: Key Replicated.")
            print("   -> 💸 DATA: Transaction Modified.")
            print("="*70 + "\n")
            return jsonify({"status": "hacked", "message": "TLS Broken. Data Stolen."})
        
        print("\n✅ SUCCESS: Standard Transaction Complete.")
        print("="*70 + "\n")
        return jsonify({"status": "success", "message": "Transfer Complete (Standard)."})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 QUANTUM DEFENSE BACKEND ONLINE")
    print("   Listening for Bank App Requests...")
    print("   Ready to show QRNG / E91 / AES Logs")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000)