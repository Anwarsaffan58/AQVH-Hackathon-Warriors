from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import random

def generate_qrng_bits(num_bits=8, show_visuals=False):
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)  # Put qubit in superposition
    circuit.measure(0, 0)

    simulator = AerSimulator()
    compiled_circuit = transpile(circuit, simulator)
    job = simulator.run(compiled_circuit, shots=num_bits)
    result = job.result()
    counts = result.get_counts()

    bits_list = []
    for bitstring, count in counts.items():
        bits_list.extend([bitstring] * count)

    random.shuffle(bits_list)
    bits_str = ''.join(bits_list)

    print("\nQuantum Circuit:\n")
    print(circuit.draw())  # ASCII circuit diagram in console

    if show_visuals:
        plot_histogram(counts)  # Bar graph of measurement counts
        plt.show()

    return bits_str

if __name__ == "__main__":
    bits = generate_qrng_bits(16, show_visuals=True)
    print("\nQuantum Random Bits:", bits)
