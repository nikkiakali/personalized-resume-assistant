import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { API_BASE } from "../api";

type Message = { role: "user" | "assistant"; content: string };

export default function Chat() {
  const [q, setQ] = useState("");
  const [history, setHistory] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  async function ask() {
    const query = q.trim();
    if (!query) return;
    setLoading(true);
    setHistory((h) => [...h, { role: "user", content: query }]);

    try {
      const r = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, k: 10 }),
      });

      if (!r.ok) {
        const text = await r.text();
        let errorMsg = text;
        try {
          // Try to parse a JSON error response from our backend
          const errorJson = JSON.parse(text);
          if (errorJson.detail) {
            errorMsg = errorJson.detail;
          }
        } catch (e) {
          // Not a JSON response, the raw text is fine.
        }
        throw new Error(errorMsg);
      }
      const j = await r.json();
      setHistory((h) => [
        ...h,
        { role: "assistant", content: j.answer },
      ]);
    } catch (err: any) {
      setHistory((h) => [
        ...h,
        {
          role: "assistant",
          content: String(err?.message || err),
        },
      ]);
    } finally {
      setQ("");
      setLoading(false);
    }
  }

  useEffect(() => {
    // Automatically scroll to the bottom of the chat history
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  return (
    <div className="bg-white p-4 sm:p-6 rounded-xl shadow-sm">
      <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-4">
        {history.map((m, i) => (
          <div
            key={i}
            className={`flex items-start gap-3 ${
              m.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`h-8 w-8 rounded-full flex-shrink-0 flex items-center justify-center font-semibold ${
                m.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-700 text-white"
              }`}
            >
              {m.role === "user" ? "You" : "AI"}
            </div>
            <div
              className={
                "p-3 rounded-lg max-w-lg " +
                (m.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-800")
              }
            >
              <ReactMarkdown>{m.content}</ReactMarkdown>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="mt-4 pt-4 border-t border-gray-200 flex items-center gap-2">
        <input
          className="flex-1 w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
          placeholder="Ask a question..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && ask()}
        />
        <button
          className="inline-flex items-center justify-center rounded-md border border-transparent bg-black px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={ask}
          disabled={loading}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Thinking...
            </>
          ) : "Ask"}
        </button>
      </div>
    </div>
  );
}