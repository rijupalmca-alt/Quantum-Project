# Quantum Search Lab (React + Django + Qiskit)

A starter research application comparing Grover search and classical linear search.

## Requirements
- Python 3.10+
- Node.js 18+
- npm

## Backend setup (Windows PowerShell)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```
The API runs at http://127.0.0.1:8000/api/experiments/compare/

## Frontend setup (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Example API request
POST JSON to `/api/experiments/compare/`:
```json
{
  "n_qubits": 3,
  "marked_states": ["101"],
  "iterations": 1,
  "shots": 2048,
  "noise_probability": 0.0
}
```

## Important research and measurement notes
- The Qiskit Aer simulator measures a simulated circuit; its wall-clock time is not physical quantum hardware execution time.
- The classical baseline here scans the ordered state list from zero and stops at the first marked state. Its measured timing is a small Python benchmark and should not be treated as a universal classical runtime.
- Quantum and classical timings are not directly equivalent because they include different setup and execution overheads.
- Oracle-query count is the main algorithmic comparison. Grover uses `iterations` oracle calls in this implementation; classical comparisons are reported separately.
- The cost estimate uses illustrative rates (`quantum_cost_per_shot` and `classical_cost_per_ms`) and is not actual cloud or hardware pricing. Choose and justify rates in your research methodology.
- Noise is a simple depolarizing noise model applied to selected gates. It is a simplified model, not a complete device calibration.
- This is a research prototype, not production software. `SECRET_KEY`, `DEBUG`, permissions, validation, authentication, persistence, and deployment settings must be hardened before production use.
