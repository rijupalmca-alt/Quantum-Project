import { useState } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'

const API = 'http://127.0.0.1:8000/api/experiments/compare/'

export default function App() {
  const [n, setN] = useState(3)
  const [marked, setMarked] = useState('101')
  const [iterations, setIterations] = useState(1)
  const [shots, setShots] = useState(2048)
  const [noise, setNoise] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function run() {
    setLoading(true); setError(''); setResult(null)
    try {
      const response = await axios.post(API, {
        n_qubits: Number(n),
        marked_states: marked.split(',').map(x => x.trim()).filter(Boolean),
        iterations: Number(iterations), shots: Number(shots),
        noise_probability: Number(noise)
      })
      setResult(response.data)
    } catch (e) {
      setError(e.response?.data?.error || 'Could not connect to Django API. Check that the backend is running.')
    } finally { setLoading(false) }
  }

  const chartData = result ? [
    { metric: 'Execution time (ms)', Grover: Number(result.quantum.execution_time_ms.toFixed(3)), Classical: Number(result.classical.execution_time_ms.toFixed(3)) },
    { metric: 'Cost (illustrative units)', Grover: result.cost_estimate.quantum, Classical: result.cost_estimate.classical }
  ] : []

  return <main className="container">
    <header><div><p className="eyebrow">QUANTUM COMPUTING RESEARCH</p><h1>Quantum Search Lab</h1><p className="muted">Compare Grover's algorithm with classical linear search.</p></div></header>
    <section className="panel">
      <h2>Experiment configuration</h2>
      <div className="form-grid">
        <label>Number of qubits<input type="number" min="1" max="8" value={n} onChange={e => {setN(e.target.value); setIterations(Math.max(0, Math.round(Math.PI/4*Math.sqrt((2**Number(e.target.value))/Math.max(1, marked.split(',').length))-.5)))}} /></label>
        <label>Marked states (comma-separated)<input value={marked} onChange={e => setMarked(e.target.value)} placeholder="e.g. 101, 011" /></label>
        <label>Grover iterations<input type="number" min="0" max="100" value={iterations} onChange={e => setIterations(e.target.value)} /></label>
        <label>Measurement shots<input type="number" min="1" max="100000" value={shots} onChange={e => setShots(e.target.value)} /></label>
        <label>Depolarizing noise probability<input type="number" min="0" max="0.99" step="0.01" value={noise} onChange={e => setNoise(e.target.value)} /></label>
      </div>
      <button onClick={run} disabled={loading}>{loading ? 'Running experiment…' : 'Run comparison'}</button>
      <p className="hint">Marked states must be binary strings whose length equals the number of qubits.</p>
      {error && <p className="error">{error}</p>}
    </section>

    {result && <>
      <section className="stats">
        <article className="stat"><span>Search space</span><strong>{result.configuration.search_space_size}</strong><small>states</small></article>
        <article className="stat"><span>Grover success probability</span><strong>{(result.quantum.success_probability*100).toFixed(2)}%</strong><small>{result.quantum.success_count} successful shots</small></article>
        <article className="stat"><span>Grover circuit depth</span><strong>{result.quantum.circuit_depth}</strong><small>{result.quantum.qubits} qubits</small></article>
        <article className="stat"><span>Classical comparisons</span><strong>{result.classical.average_comparisons.toFixed(1)}</strong><small>average per trial</small></article>
      </section>
      <section className="panel">
        <h2>Performance comparison</h2>
        <div className="chart"><ResponsiveContainer width="100%" height={300}><BarChart data={chartData}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="metric"/><YAxis/><Tooltip/><Legend/><Bar dataKey="Grover" fill="#6558d3"/><Bar dataKey="Classical" fill="#18a58b"/></BarChart></ResponsiveContainer></div>
        <div className="two-col">
          <div><h3>Grover's algorithm</h3><p>Execution time: <b>{result.quantum.execution_time_ms.toFixed(3)} ms</b></p><p>Oracle queries: <b>{result.quantum.oracle_queries}</b></p><p>Success probability: <b>{(result.quantum.success_probability*100).toFixed(2)}%</b></p><p>Circuit depth: <b>{result.quantum.circuit_depth}</b></p></div>
          <div><h3>Classical linear search</h3><p>Execution time: <b>{result.classical.execution_time_ms.toFixed(3)} ms</b></p><p>Element comparisons (average): <b>{result.classical.average_comparisons.toFixed(2)}</b></p><p>Worst-case comparisons: <b>{result.classical.worst_case_comparisons}</b></p></div>
        </div>
        <h3>Estimated cost</h3>
        <p>Quantum: <b>{result.cost_estimate.quantum.toFixed(6)}</b> | Classical: <b>{result.cost_estimate.classical.toFixed(6)}</b> {result.cost_estimate.currency}</p>
        <p className="hint">{result.cost_estimate.assumptions.warning} Cost rates can be changed in the API request.</p>
        <h3>Measurement counts</h3><pre>{JSON.stringify(result.quantum.counts, null, 2)}</pre>
      </section>
    </>}
    <footer>Research prototype • Simulator timings are not quantum-hardware timings.</footer>
  </main>
}
