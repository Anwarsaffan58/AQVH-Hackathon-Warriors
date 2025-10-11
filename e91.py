# e91.py
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import random

def create_e91_circuit():
    """Create a Bell pair (entangled qubits for Alice and Bob)"""
    qc = QuantumCircuit(2, 2)
    qc.h(0)         # Hadamard on Alice's qubit
    qc.cx(0, 1)     # CNOT to entangle Alice's and Bob's qubits
    return qc

def measure_in_basis(qc, qubit, classical_bit, basis):
    """Measure a single qubit in the specified basis (Z, X, or Y)"""
    if basis == 'X':
        qc.h(qubit)
    elif basis == 'Y':
        qc.sdg(qubit)
        qc.h(qubit)
    qc.measure(qubit, classical_bit)

def e91_protocol(num_rounds=50):  # Reduced for quick runs
    simulator = AerSimulator()

    # Bases choices for Alice and Bob
    alice_bases = ['X', 'Y', 'Z']
    bob_bases = ['X', 'Y', 'Z']

    alice_results = []
    bob_results = []

    demo_circ = None
    demo_counts = None

    for i in range(num_rounds):
        qc = create_e91_circuit()

        # Random bases for each round
        alice_basis = random.choice(alice_bases)
        bob_basis = random.choice(bob_bases)

        measure_in_basis(qc, 0, 0, alice_basis)
        measure_in_basis(qc, 1, 1, bob_basis)

        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=1)
        result = job.result()
        counts = result.get_counts()
        measured_bits = list(counts.keys())[0]  # e.g. '01'

        # Note: Qiskit bit order in counts is reversed (classical bits)
        alice_bit = int(measured_bits[1])
        bob_bit = int(measured_bits[0])

        alice_results.append((alice_basis, alice_bit))
        bob_results.append((bob_basis, bob_bit))

        if i == 0:
            demo_circ = qc
            demo_counts = counts

    # Keep only when bases match
    shared_key = []
    for (a_basis, a_bit), (b_basis, b_bit) in zip(alice_results, bob_results):
        if a_basis == b_basis:
            shared_key.append(str(a_bit))

    # Print simulation summary
    print(f"E91 Protocol simulation with {num_rounds} rounds")
    print("Total bits with matching bases (key length):", len(shared_key))
    print("Shared key (first 64 bits):", "".join(shared_key[:64]))
    print("\nExample quantum circuit used for one round:")
    print(demo_circ.draw())

    # Save histogram instead of blocking
    plot_histogram(demo_counts)
    plt.title("Measurement outcomes - first round")
    plt.savefig("e91_measurement_histogram.png")
    plt.close()
    print("\n[✔] Histogram saved to e91_measurement_histogram.png in this folder.")

if __name__ == "__main__":
    e91_protocol(num_rounds=50)  # quick run; increase for final results
