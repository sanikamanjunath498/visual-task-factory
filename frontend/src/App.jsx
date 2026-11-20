import React, { useState } from "react";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [difficulty, setDifficulty] = useState(3);
  const [tasks, setTasks] = useState([]);
  const [evalReport, setEvalReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: 3, difficulty }),
      });
      const data = await res.json();
      setTasks((prev) => [...data.tasks, ...prev]);
    } catch (err) {
      alert("Error connecting to backend. Make sure Uvicorn is running on port 8000.");
    }
    setLoading(false);
  };

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/evaluate`, { method: "POST" });
      const data = await res.json();
      setEvalReport(data);
    } catch (err) {
      alert("Evaluation failed. Check your GEMINI_API_KEY in the backend terminal!");
    }
    setLoading(false);
  };

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", maxWidth: "950px", margin: "40px auto", padding: "20px", color: "#111" }}>
      <h1>🏭 Visual Task Factory (Track 2)</h1>
      <p style={{ color: "#555" }}>Automated Synthetic Visual Benchmark & Frontier AI Stress-Tester</p>

      {/* Control Panel */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", alignItems: "center", background: "#f4f4f5", padding: "20px", borderRadius: "10px", border: "1px solid #e4e4e7" }}>
        <div>
          <label><strong>Noise Difficulty (1–5): {difficulty}</strong></label><br />
          <input
            type="range"
            min="1"
            max="5"
            value={difficulty}
            onChange={(e) => setDifficulty(Number(e.target.value))}
            style={{ cursor: "pointer", marginTop: "6px" }}
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          style={{ padding: "10px 18px", cursor: "pointer", borderRadius: "6px", border: "1px solid #111", background: "#fff", color: "#111", fontWeight: "600" }}
        >
          {loading ? "Working..." : "1. Generate Synthetic Tasks"}
        </button>

        <button
          onClick={handleEvaluate}
          disabled={loading || tasks.length === 0}
          style={{ padding: "10px 18px", cursor: "pointer", borderRadius: "6px", border: "none", background: tasks.length === 0 ? "#999" : "#111", color: "#fff", fontWeight: "600" }}
        >
          {loading ? "Evaluating AI..." : "2. Run Frontier AI Eval"}
        </button>
      </div>

      {/* Benchmark Scorecard */}
      {evalReport && (
        <div style={{ marginTop: "20px", padding: "18px", border: "2px solid #111", borderRadius: "10px", background: "#fafafa" }}>
          <h3 style={{ margin: "0 0 8px 0" }}>📊 Evaluation Report: {evalReport.model}</h3>
          <p style={{ margin: 0, fontSize: "16px" }}>
            <strong>Accuracy:</strong> {evalReport.accuracy_percent}% ({evalReport.total_tested} tasks tested)
          </p>
        </div>
      )}

      {/* Generated Tasks Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))", gap: "20px", marginTop: "25px" }}>
        {tasks.map((t) => {
          const result = evalReport?.results.find((r) => r.task_id === t.task_id);
          return (
            <div key={t.task_id} style={{ border: "1px solid #ddd", borderRadius: "10px", padding: "16px", background: "#fff", boxShadow: "0 2px 6px rgba(0,0,0,0.04)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong>Task #{t.task_id} (Level {t.difficulty})</strong>
                {result && (
                  <span style={{ color: result.passed ? "#059669" : "#dc2626", fontWeight: "bold", fontSize: "14px" }}>
                    {result.passed ? "✓ PASSED" : `✗ FAILED (AI said: ${result.parsed_prediction})`}
                  </span>
                )}
              </div>
              <img
                src={`${API_BASE}${t.image_url}`}
                alt={`Synthetic Task ${t.task_id}`}
                style={{ width: "100%", marginTop: "12px", border: "1px solid #eee", borderRadius: "6px" }}
              />
              <p style={{ fontSize: "14px", marginBottom: "6px" }}><strong>Q:</strong> {t.question}</p>
              <p style={{ fontSize: "14px", color: "#059669", margin: 0 }}><strong>Verified Ground Truth:</strong> {t.ground_truth}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
