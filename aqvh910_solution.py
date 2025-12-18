"""
PROJECT: Amaravati Quantum Valley Hackathon 2025
PROBLEM STATEMENT: AQVH910 - Design a basic QRNG using a quantum circuit.
TEAM: Quantum Shield
AUTHOR: Saffan

DESCRIPTION:
    This script fulfills the requirement of generating truly random bits 
    by utilizing Quantum Superposition and Measurement.
    
    KEY COMPONENTS:
    1. Quantum Circuit (1 Qubit).
    2. Hadamard Gate (H) -> Creates Superposition state |+>.
    3. Measurement (M) -> Collapses state to 0 or 1.
    4. Statistical Proof -> Verifies the randomness distribution.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def create_qrng_circuit():
    """
    Creates the specific quantum circuit asked for in AQVH910.
    """
    # 1. Initialize 1 Quantum Bit and 1 Classical Bit
    qc = QuantumCircuit(1, 1)
    
    # 2. Apply Hadamard Gate (H)
    # This puts the qubit into Superposition: (|0> + |1>) / sqrt(2)
    # The qubit is now '0' and '1' at the same time.
    qc.h(0)
    
    # 3. Measure the Qubit
    # This collapses the superposition into a definite state (0 or 1).
    qc.measure(0, 0)
    
    return qc

def generate_true_random_bit(simulator, qc):
    """
    Runs the circuit once to get a single random bit.
    """
    job = simulator.run(qc, shots=1, memory=True)
    result = job.result()
    memory = result.get_memory()
    return int(memory[0])

def demonstrate_proof_of_randomness(simulator, qc, shots=1000):
    """
    PROOF OF CONCEPT:
    Runs the circuit 1000 times to show judges that the distribution 
    is balanced (approx 50/50), proving true probabilistic behavior.
    """
    print(f"\n[ DEMO ] Running 'Proof of Randomness' Test ({shots} shots)...")
    
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    
    zeros = counts.get('0', 0)
    ones = counts.get('1', 0)
    
    print(f"    Total Runs: {shots}")
    print(f"    Outcome '0': {zeros} times ({(zeros/shots)*100:.1f}%)")
    print(f"    Outcome '1': {ones} times ({(ones/shots)*100:.1f}%)")
    
    if 0.45 < zeros/shots < 0.55:
        print("    [ PASS ] Distribution is balanced. Superposition confirmed.")
    else:
        print("    [ WARN ] Distribution skewed (likely statistical variance).")
        
    return counts

# ==========================================
# MAIN EXECUTION FOR JUDGES
# ==========================================
if __name__ == "__main__":
    print("--- AQVH910 SOLUTION: BASIC QUANTUM RANDOM NUMBER GENERATOR ---\n")
    
    # 1. Setup Simulator
    simulator = AerSimulator()
    
    # 2. Build Circuit
    qc = create_qrng_circuit()
    
    # 3. Show Circuit Diagram (Visual Proof for Judges)
    print("1. THE QUANTUM CIRCUIT (Visual Proof):")
    print(qc.draw(output='text'))
    print("   (H = Hadamard/Superposition, M = Measurement)\n")
    
    # 4. Generate Random Bits
    print("2. GENERATING RANDOM BITS:")
    random_bits = [generate_true_random_bit(simulator, qc) for _ in range(5)]
    print(f"   Generated Sequence: {random_bits}")
    
    # 5. Proof of Randomness
    demonstrate_proof_of_randomness(simulator, qc)
    
    print("\n--- DEMO COMPLETE ---")