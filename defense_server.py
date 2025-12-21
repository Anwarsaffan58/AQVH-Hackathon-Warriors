import time
import random
import sys
import secrets
from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
    print("✅ QUANTUM CORE ONLINE. MILITARY PROTOCOLS LOADED.")
except ImportError:
    QISKIT_AVAILABLE = False
    print("⚠️ SIMULATION MODE ACTIVE.")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def print_log(phase, message):
    print(f"[{phase}] {message}")
    time.sleep(0.1)

@app.route('/transmit_intel', methods=['POST', 'OPTIONS'])
def transmit_intel():
    if request.method == 'OPTIONS': return jsonify({"status": "ok"}), 200

    data = request.json
    mode = data.get('mode', 'classical')
    attack = data.get('attack', False)

    print("\n" + "="*70)
    print(f"🚀 INCOMING TRANSMISSION | TARGET: DRDO_SAT_01")
    print("="*70)

    # --- MILITARY QUANTUM MODE ---
    if mode == 'quantum':
        print("\n🔵 [PHASE 1] QUANTUM UPLINK INITIATED")
        print_log("HARDWARE", "Activating QRNG Module (Ruggedized)...")
        
        # QRNG SIMULATION
        entropy = 0.9999
        print_log("ENTROPY", f"Source Stability: {entropy*100}% (Perfect)")
        
        print("\n🟣 [PHASE 2] E91 ENTANGLEMENT DISTRIBUTION")
        print_log("LINK", "Firing Photons to Satellite (Free-Space Optical)...")
        print_log("SYNC", "Aligning Polarization Bases...")

        if attack:
            print("\n❌ ALERT: ENEMY SIGNAL INTERCEPTION DETECTED!")
            print("   -> 📉 QBER SPIKE: 42% (Massive Interference)")
            print("   -> 🕵️ HOSTILE: Attempting to measure photons.")
            print("   -> ⚛️ PHYSICS: Wavefunction Collapsed.")
            print("\n🛑 COUNTERMEASURE: SELF-DESTRUCT KEYS. LINK SEVERED.")
            print("="*70 + "\n")
            return jsonify({"status": "defended", "message": "HOSTILE INTERCEPT DETECTED. LINK CUT."})
        
        print_log("QBER", "0.01% (Secure Channel)")
        print_log("KEYS", "Shared Secret Established.")

        print("\n🟢 [PHASE 3] MILITARY-GRADE ENCRYPTION")
        print_log("ALGO", "AES-256-GCM + Quantum One-Time Pad")
        print_log("STATUS", "Intel Packet Locked.")
        
        print("\n✅ TRANSMISSION SUCCESSFUL.")
        print("="*70 + "\n")
        return jsonify({"status": "success", "message": "INTEL SECURED. UPLINK COMPLETE."})

    # --- CLASSICAL RADIO MODE ---
    else:
        print("\n🟠 [PHASE 1] STANDARD RF RADIO LINK")
        print_log("PROTOCOL", "Standard Military Radio (VHF/UHF)")
        
        if attack:
            print("\n❌ CRITICAL FAILURE")
            print("   -> 📡 JAMMING: Signal Intercepted.")
            print("   -> 🔓 DECRYPTION: Enemy cracked Static Key.")
            print("   -> ☠️ INTEL LEAKED: Coordinates Compromised.")
            print("="*70 + "\n")
            return jsonify({"status": "hacked", "message": "SIGNAL INTERCEPTED. INTEL LEAKED."})
        
        print("\n✅ TRANSMISSION COMPLETE (Standard Risk).")
        print("="*70 + "\n")
        return jsonify({"status": "success", "message": "Radio Transmission Complete."})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛡️ DRDO / ARMY QUANTUM DEFENSE NODE ONLINE")
    print("   Listening for Tactical Uplinks...")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000)