import { useState, useMemo } from "react";
import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import "./App.css";

function UploadPage() {
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const file = event.target.elements.file.files[0];
    if (!file) {
      setStatus("Please select a file.");
      return;
    }
    setLoading(true);
    setStatus("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData
      });
      if (!res.ok) {
        throw new Error(`Upload failed: ${res.status}`);
      }
      setStatus("Upload successful.");
    } catch (error) {
      setStatus(error.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <div className="card-header">
        <span className="badge">Knowledge Intake</span>
        <h2>Upload Files</h2>
        <p>Feed PDFs, docs, or spreadsheets. We will embed and index them for lightning fast answers.</p>
      </div>
      <form className="stack gap-lg" onSubmit={handleSubmit}>
        <label className="file-picker">
          <input
            type="file"
            name="file"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          />
          <div>
            <p>{selectedFile ? selectedFile.name : "Choose a file from your device"}</p>
            <small>Max 20MB • Securely stored in your private vector space</small>
          </div>
        </label>
        <button className="primary" type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload & index"}
        </button>
      </form>
      {status && <p className="status">{status}</p>}
    </section>
  );
}

function ChatPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const sendQuestion = async () => {
    if (!question.trim()) {
      setAnswer("Enter a question.");
      return;
    }
    setLoading(true);
    setAnswer("");
    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });
      if (!res.ok) {
        throw new Error(`Chat failed: ${res.status}`);
      }
      const data = await res.json();
      setAnswer(data.answer || "No response.");
    } catch (error) {
      setAnswer(error.message || "Chat failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <div className="card-header">
        <span className="badge tone-secondary">AI Workspace</span>
        <h2>Chat with your knowledge</h2>
        <p>Ask natural language questions. The assistant cites the documents you uploaded.</p>
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question"
        />
        <button className="primary" onClick={sendQuestion} disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
      {answer && (
        <div className="chat-response">
          <strong>Response</strong>
          <p>{answer}</p>
        </div>
      )}
    </section>
  );
}

export default function App() {
  const location = useLocation();
  const activePageCopy = useMemo(() => {
    if (location.pathname.includes("chat")) {
      return {
        title: "Knowledge copilots engineered for clarity",
        body: "Every chat turns your scattered files into reliable answers with citations and tone you control."
      };
    }
    return {
      title: "Centralize documents. Answer anything.",
      body: "Upload contracts, financials, research, or playbooks. Cheddup makes them searchable with instant chat."
    };
  }, [location.pathname]);

  return (
    <div className="app-shell">
      <div className="gradient" />
      <header className="app-header">
        <Link to="/" className="logo">
          cheddup
        </Link>
        <nav>
          <NavLink to="/upload">Upload</NavLink>
          <NavLink to="/chat">Chat</NavLink>
        </nav>
        <Link to="/chat" className="primary ghost">
          Launch workspace
        </Link>
      </header>
      <main className="app-main">
        <section className="hero">
          <p className="eyebrow">AI Knowledge Infrastructure</p>
          <h1>{activePageCopy.title}</h1>
          <p>{activePageCopy.body}</p>
          <div className="hero-cta">
            <Link to="/upload" className="primary">
              Upload content
            </Link>
            <Link to="/chat" className="secondary">
              Chat instantly
            </Link>
          </div>
        </section>
        <Routes>
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="*" element={<UploadPage />} />
        </Routes>
      </main>
      <footer className="app-footer">
        <p>© {new Date().getFullYear()} cheddup. Knowledge infrastructure for lean teams.</p>
        <div className="footer-links">
          <Link to="/upload">Upload</Link>
          <Link to="/chat">Chat</Link>
        </div>
      </footer>
    </div>
  );
}
