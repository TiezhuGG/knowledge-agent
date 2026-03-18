import { useMemo, useState } from "react";

type Citation = {
  doc_id: string;
  source: string;
  chunk_id: string;
  quote: string;
};

type ChatResponse = {
  answer: string;
  citations: Citation[];
  confidence: number;
  trace_id: string;
  suggested_action: "none" | "open_ticket";
};

type TraceEvent = {
  step: string;
  status: "ok" | "error";
  latency_ms: number;
  tool_name?: string;
  detail?: string;
  timestamp: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export default function App() {
  const [source, setSource] = useState("kb://faq/auth.md");
  const [content, setContent] = useState(
    [
      "Password reset:",
      "Users can click Forgot Password on the login page.",
      "",
      "Timeout troubleshooting:",
      "Check API key, region, and retry with exponential backoff."
    ].join("\n")
  );
  const [sessionId, setSessionId] = useState("demo-session-1");
  const [question, setQuestion] = useState("How do I reset my password?");
  const [customerTier, setCustomerTier] = useState<"free" | "pro" | "enterprise">("pro");
  const [chatResp, setChatResp] = useState<ChatResponse | null>(null);
  const [trace, setTrace] = useState<TraceEvent[]>([]);
  const [evalResult, setEvalResult] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canAsk = useMemo(() => question.trim().length > 0, [question]);

  async function ingest() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/knowledge/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source, content })
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      setEvalResult(`Ingested ${data.chunk_count} chunks, doc_id=${data.doc_id}`);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  async function ask() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          question,
          customer_tier: customerTier
        })
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data: ChatResponse = await res.json();
      setChatResp(data);
      const traceRes = await fetch(`${API_BASE}/api/traces/${data.trace_id}`);
      if (traceRes.ok) {
        const traceData = await traceRes.json();
        setTrace(traceData.events);
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  async function runEval() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/evals/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eval_suite_id: "default" })
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      setEvalResult(
        `Accuracy=${data.metrics.accuracy}, Groundedness=${data.metrics.groundedness}, ToolSuccess=${data.metrics.tool_success_rate}`
      );
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="card">
        <h1>SaaS Knowledge Agent MVP</h1>
        <p>Ingest docs, ask grounded questions, inspect citations and traces.</p>
      </section>

      <section className="card">
        <h2>1) Ingest Knowledge</h2>
        <label>
          Source
          <input value={source} onChange={(e) => setSource(e.target.value)} />
        </label>
        <label>
          Content
          <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={7} />
        </label>
        <button onClick={ingest} disabled={loading}>
          Ingest
        </button>
      </section>

      <section className="card">
        <h2>2) Ask Agent</h2>
        <label>
          Session ID
          <input value={sessionId} onChange={(e) => setSessionId(e.target.value)} />
        </label>
        <label>
          Customer Tier
          <select value={customerTier} onChange={(e) => setCustomerTier(e.target.value as any)}>
            <option value="free">free</option>
            <option value="pro">pro</option>
            <option value="enterprise">enterprise</option>
          </select>
        </label>
        <label>
          Question
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={4} />
        </label>
        <div className="row">
          <button onClick={ask} disabled={loading || !canAsk}>
            Ask
          </button>
          <button onClick={runEval} disabled={loading}>
            Run Eval
          </button>
        </div>
      </section>

      {error && (
        <section className="card error">
          <strong>Error:</strong> {error}
        </section>
      )}

      {evalResult && (
        <section className="card">
          <h2>Eval Result</h2>
          <pre>{evalResult}</pre>
        </section>
      )}

      {chatResp && (
        <section className="card">
          <h2>Agent Answer</h2>
          <p>{chatResp.answer}</p>
          <p>
            Confidence: <b>{chatResp.confidence}</b> | Suggested Action: <b>{chatResp.suggested_action}</b>
          </p>
          <h3>Citations</h3>
          <ul>
            {chatResp.citations.map((c) => (
              <li key={c.chunk_id}>
                <code>{c.source}</code> - {c.quote}
              </li>
            ))}
          </ul>
          <h3>Trace</h3>
          <ul>
            {trace.map((e, idx) => (
              <li key={`${e.timestamp}-${idx}`}>
                {e.step} ({e.status}) - {e.latency_ms}ms {e.tool_name ? `[${e.tool_name}]` : ""}{" "}
                {e.detail ? `| ${e.detail}` : ""}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}

