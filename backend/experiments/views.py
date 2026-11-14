from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .quantum import run_grover
from .classical import run_linear_search
import math

@api_view(["POST"])
def compare(request):
    data = request.data
    try:
        n_qubits = int(data.get("n_qubits", 3))
        marked_states = data.get("marked_states", ["101"])
        if isinstance(marked_states, str):
            marked_states = [x.strip() for x in marked_states.split(",") if x.strip()]
        iterations = int(data.get("iterations", max(0, round((math.pi / 4) * math.sqrt((2**n_qubits) / len(marked_states)) - 0.5))))
        shots = int(data.get("shots", 2048))
        noise_probability = float(data.get("noise_probability", 0))
        if not 1 <= shots <= 100000:
            raise ValueError("Shots must be between 1 and 100000.")

        quantum = run_grover(n_qubits, marked_states, iterations, shots, noise_probability)
        classical = run_linear_search(n_qubits, marked_states)

        # Transparent illustrative cost model. User-adjustable rates are not real market prices.
        quantum_rate = float(data.get("quantum_cost_per_shot", 0.001))
        classical_rate = float(data.get("classical_cost_per_ms", 0.00001))
        quantum_cost = shots * quantum_rate
        classical_cost = classical["execution_time_ms"] * classical_rate

        return Response({
            "configuration": {
                "n_qubits": n_qubits, "search_space_size": 2**n_qubits,
                "marked_states": marked_states, "iterations": iterations,
                "shots": shots, "noise_probability": noise_probability
            },
            "quantum": quantum,
            "classical": classical,
            "cost_estimate": {
                "quantum": quantum_cost,
                "classical": classical_cost,
                "currency": "arbitrary cost units",
                "assumptions": {
                    "quantum_cost_per_shot": quantum_rate,
                    "classical_cost_per_ms": classical_rate,
                    "warning": "Illustrative model only; not actual hardware or cloud-provider pricing."
                }
            }
        })
    except (ValueError, TypeError, ArithmeticError) as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
