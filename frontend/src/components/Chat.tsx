import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { API_BASE } from "../api";

type Message = { role: "user" | "assistant"; content: string };

export default function Chat() {
  const [q, setQ] = useState("");
  const [history, setHistory] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function ask() {
    const query = q.trim();
    if (!query) return;
    setLoading(true);
    setHistory((h) => [...h, { role: "user", content: query }]);

    try {
      const r = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, k: 5 }),
      });

      if (!r.ok) {
        const text = await r.text();
        throw new Error(`${r.status} ${text}`);
      }
      const j = await r.json();
      const citations = formatCitations(j.citations);
      setHistory((h) => [
        ...h,
        { role: "assistant", content: `${j.answer}\n\n${citations}`.trim() },
      ]);
    } catch (err: any) {
      setHistory((h) => [
        ...h,
        {
          role: "assistant",
          content: `Request failed: ${String(err?.message || err)}`,
        },
      ]);
    } finally {
      setQ("");
      setLoading(false);
    }
  }

  function formatCitations(cites: any[]): string {
    if (!Array.isArray(cites) || cites.length === 0) return "";
    const uniq = new Map<string, number>();
    for (const c of cites) {
      const key = `${c.filename}#${c.chunk_id}`;
      if (!uniq.has(key)) uniq.set(key, c.score);
    }
    const parts = [...uniq.keys()].map((k) => `[${k}]`);
    return parts.length ? `_Sources: ${parts.join(", ")}_` : "";
  }

  return (
    <div className="p-4 border rounded-lg bg-white">
      <div className="space-y-3 max-h-96 overflow-auto">
        {history.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <div
              className={
                "inline-block px-3 py-2 rounded " +
                (m.role === "user" ? "bg-blue-100" : "bg-gray-100")
              }
            >
              <ReactMarkdown>{m.content}</ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <input
          className="flex-1 border p-2 rounded"
          placeholder="Ask about your resume or the JD..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
        />
        <button
          className="px-4 py-2 bg-black text-white rounded"
          onClick={ask}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>
    </div>
  );
}