import math
import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def _phase_oracle(n_qubits, marked_states):
    """Flip the phase of each marked computational-basis state."""
    qc = QuantumCircuit(n_qubits)
    for bitstring in marked_states:
        # Qiskit qubit 0 is the rightmost character in a displayed bitstring.
        zero_positions = [i for i, bit in enumerate(reversed(bitstring)) if bit == "0"]
        if zero_positions:
            qc.x(zero_positions)
        if n_qubits == 1:
            qc.z(0)
        else:
            qc.h(n_qubits - 1)
            qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            qc.h(n_qubits - 1)
        if zero_positions:
            qc.x(zero_positions)
    return qc

def _diffuser(n_qubits):
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    if n_qubits == 1:
        qc.z(0)
    else:
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc

def run_grover(n_qubits, marked_states, iterations, shots=2048, noise_probability=0.0):
    if not 1 <= n_qubits <= 8:
        raise ValueError("Use between 1 and 8 qubits for this demo.")
    max_state = 2 ** n_qubits
    if not marked_states:
        raise ValueError("Provide at least one marked state.")
    if len(set(marked_states)) != len(marked_states):
        raise ValueError("Marked states must be unique.")
    for state in marked_states:
        if len(state) != n_qubits or set(state) - {"0", "1"}:
            raise ValueError(f"Each marked state must be a {n_qubits}-bit binary string.")
    if len(marked_states) >= max_state:
        raise ValueError("Marked-state count must be smaller than the search space.")
    if not 0 <= iterations <= 100:
        raise ValueError("Iterations must be between 0 and 100.")
    if not 0 <= noise_probability < 1:
        raise ValueError("Noise probability must be between 0 and 1 (exclusive upper bound).")

    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    oracle = _phase_oracle(n_qubits, marked_states).to_gate(label="Oracle")
    diffuser = _diffuser(n_qubits).to_gate(label="Diffuser")
    for _ in range(iterations):
        qc.append(oracle, range(n_qubits))
        qc.append(diffuser, range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))

    simulator = AerSimulator()
    if noise_probability > 0:
        from qiskit_aer.noise import NoiseModel, depolarizing_error
        noise_model = NoiseModel()
        error_1q = depolarizing_error(noise_probability, 1)
        error_2q = depolarizing_error(noise_probability, 2)
        noise_model.add_all_qubit_quantum_error(error_1q, ["h", "x", "z"])
        noise_model.add_all_qubit_quantum_error(error_2q, ["cx"])
        simulator.set_options(noise_model=noise_model)

    started = time.perf_counter()
    compiled = transpile(qc, simulator, optimization_level=1)
    result = simulator.run(compiled, shots=shots).result()
    elapsed_ms = (time.perf_counter() - started) * 1000
    counts = result.get_counts()
    successes = sum(count for state, count in counts.items() if state.replace(" ", "") in marked_states)
    probability = successes / shots
    return {
        "algorithm": "Grover",
        "success_probability": probability,
        "success_count": successes,
        "shots": shots,
        "counts": counts,
        "execution_time_ms": elapsed_ms,
        "oracle_queries": iterations,
        "qubits": n_qubits,
        "circuit_depth": compiled.depth(),
        "gate_count": dict(compiled.count_ops()),
        "marked_states": marked_states,
        "noise_probability": noise_probability,
    }
