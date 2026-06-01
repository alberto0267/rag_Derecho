import { useEffect, useRef, useState } from "react";
import { query } from "../api";

interface Source {
  file: string;
  similarity: number;
}

interface Message {
  role: "user" | "bot";
  text: string;
  sources?: Source[];
  tool_used?: string;
}

interface HistoryMessage {
  role: string;
  content: string;
}

const MAX_HISTORY = 10;

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [history, setHistory] = useState<HistoryMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const data = await query(question, history);

      setMessages((prev) => [...prev, { role: "bot", text: data.answer, sources: data.sources, tool_used: data.tool_used }]);

      setHistory((prev) => {
        const updated = [
          ...prev,
          { role: "user", content: question },
          { role: "assistant", content: data.answer },
        ];
        return updated.slice(-MAX_HISTORY);
      });
    } catch {
      setMessages((prev) => [...prev, { role: "bot", text: "Error al conectar con el servidor." }]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <section className="chat-panel">
      <div className="messages">
        {messages.length === 0 && (
          <p className="empty">Haz una pregunta sobre tus documentos...</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <span className="bubble">{msg.text}</span>
            {msg.tool_used === "search_web" && (
              <div className="sources">
                <span className="sources-label">Fuente:</span>
                <span className="source-tag web">Web</span>
              </div>
            )}
            {!msg.tool_used && msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <span className="sources-label">Fuentes:</span>
                {[...new Set(msg.sources.map((s) => s.file))].map((file, j) => (
                  <span key={j} className="source-tag">📄 {file}</span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <span className="bubble loading">Pensando...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div id="poda">
        <div className="glow" />
        <div className="darkBorderBg" />
        <div className="white" />
        <div className="border" />
        <div id="main">
          <textarea
            className="input"
            placeholder="Escribe tu pregunta..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button id="send-btn" onClick={handleSend} disabled={loading}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </section>
  );
}
