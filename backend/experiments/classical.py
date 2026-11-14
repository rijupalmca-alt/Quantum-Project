import time

def run_linear_search(n_qubits, marked_states, trials=100):
    n = 2 ** n_qubits
    targets = set(int(x, 2) for x in marked_states)
    total_comparisons = 0
    found = 0
    started = time.perf_counter()
    # Average across every possible starting target in a deterministic order.
    # This is a simple baseline, not a claim about every search distribution.
    for _ in range(trials):
        for item in range(n):
            total_comparisons += 1
            if item in targets:
                found += 1
                break
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {
        "algorithm": "Classical linear search",
        "execution_time_ms": elapsed_ms,
        "element_comparisons": total_comparisons,
        "average_comparisons": total_comparisons / trials,
        "successful_trials": found,
        "trials": trials,
        "worst_case_comparisons": n,
    }
