import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { motion, AnimatePresence } from "framer-motion";
import {
  Github,
  BookOpen,
  Terminal,
  Layout,
  Code,
  ChevronRight,
  ArrowLeft,
  Sparkles,
  Zap,
} from "lucide-react";

const backendUrl = "http://127.0.0.1:8000";

function App() {
  const [gitUrl, setGitUrl] = useState("");
  const [localPath, setLocalPath] = useState("");
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState("");
  const [activePage, setActivePage] = useState("README.md");
  const [docsReady, setDocsReady] = useState(false);
  const [traces, setTraces] = useState<string[]>([]);
  const [showTraces, setShowTraces] = useState(false);

  const generateFromGit = async () => {
    if (!gitUrl) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("git_url", gitUrl);
      await axios.post(`${backendUrl}/generate-from-git`, formData);
      setDocsReady(true);
      loadPage("README.md");
    } catch (error: any) {
      console.error("Documentation generation error:", error);
      const errorMessage = error.response?.data?.error || error.message || "Unknown error";
      alert(`Failed to generate documentation: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const generateFromPath = async () => {
    if (!localPath) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("folder_path", localPath);
      await axios.post(`${backendUrl}/generate-from-path`, formData);
      setDocsReady(true);
      loadPage("README.md");
    } catch (error: any) {
      console.error("Path generation error:", error);
      const errorMessage = error.response?.data?.error || error.message || "Unknown error";
      alert(`Failed to generate from path: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const loadPage = async (page: string) => {
    setShowTraces(false);
    setActivePage(page);
    try {
      const response = await axios.get(`${backendUrl}/docs-static/${page}`);
      setContent(response.data);
    } catch (error) {
      console.error(error);
      setContent("# Error\nFailed to load documentation page.");
    }
  };

  const loadTraces = async () => {
    setActivePage("traces");
    setShowTraces(true);
    setLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/traces`);
      setTraces(response.data.traces || []);
    } catch (error) {
      console.error("Error loading traces:", error);
      alert("Failed to load execution traces.");
    } finally {
      setLoading(false);
    }
  };

  const pages = [
    { id: "README.md", label: "Getting Started", icon: <BookOpen size={18} /> },
    { id: "API_REFERENCE.md", label: "API Reference", icon: <Terminal size={18} /> },
    { id: "ARCHITECTURE.md", label: "Architecture", icon: <Layout size={18} /> },
    { id: "EXAMPLES.md", label: "Usage Examples", icon: <Code size={18} /> },
    { id: "diagrams/architecture.mermaid", label: "Visual Flow", icon: <ChevronRight size={18} /> },
    { id: "traces", label: "Execution Traces", icon: <Zap size={18} />, onClick: loadTraces },
  ];

  return (
    <div className="app-container">
      <AnimatePresence mode="wait">
        {!docsReady ? (
          <motion.div
            key="landing"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="landing-page"
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              minHeight: "100vh",
              padding: "2rem"
            }}
          >
            <div className="card" style={{ maxWidth: "600px", width: "100%", textAlign: "center" }}>
              <div style={{ display: "inline-flex", padding: "1rem", background: "var(--primary-light)", borderRadius: "1rem", marginBottom: "1.5rem" }}>
                <Sparkles size={32} color="var(--primary)" />
              </div>
              <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem", fontWeight: 800 }}>Documentation Generator</h1>

              <div style={{ display: "flex", flexDirection: "column", gap: "2rem", textAlign: "left" }}>
                <div>
                  <label style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--primary)", marginBottom: "0.5rem", display: "block" }}>
                    From GitHub
                  </label>
                  <div style={{ display: "flex", gap: "0.75rem" }}>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="https://github.com/username/repo"
                      value={gitUrl}
                      onChange={(e) => setGitUrl(e.target.value)}
                    />
                    <button className="btn-primary" onClick={generateFromGit} disabled={loading}>
                      {loading ? <Zap size={18} className="animate-spin" /> : <Github size={18} />}
                      Generate
                    </button>
                  </div>
                </div>

                <div style={{ position: "relative", textAlign: "center" }}>
                  <hr style={{ border: "none", borderTop: "1px solid var(--border)", margin: "1rem 0" }} />
                  <span style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", background: "white", padding: "0 1rem", color: "var(--text-muted)", fontSize: "0.8rem", fontWeight: 600 }}>OR</span>
                </div>

                <div>
                  <label style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--primary)", marginBottom: "0.5rem", display: "block" }}>
                    Local Folder Path
                  </label>
                  <div style={{ display: "flex", gap: "0.75rem" }}>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="/Users/username/project-folder"
                      value={localPath}
                      onChange={(e) => setLocalPath(e.target.value)}
                    />
                    <button className="btn-primary" onClick={generateFromPath} disabled={loading}>
                      {loading ? <Zap size={18} className="animate-spin" /> : <Terminal size={18} />}
                      Generate
                    </button>
                  </div>
                  <p style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    Enter the absolute path to your local project directory.
                  </p>
                </div>
              </div>

              {loading && (
                <div style={{ marginTop: "2rem", color: "var(--primary)", fontWeight: 600, display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}>
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                    <Zap size={20} />
                  </motion.div>
                  Analyzing codebase...
                </div>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="docs"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ display: "flex", minHeight: "100vh" }}
          >
            <div className="sidebar">
              <div className="sidebar-header">
                <div style={{ padding: "0.5rem", background: "var(--primary)", borderRadius: "0.5rem" }}>
                  <Sparkles size={20} color="white" />
                </div>
                <span style={{ fontWeight: 800, fontSize: "1.25rem", letterSpacing: "-0.02em" }}>Documentation Generator</span>
                <button
                  onClick={() => setDocsReady(false)}
                  style={{ marginLeft: "auto", padding: "0.5rem", border: "none", background: "none", cursor: "pointer", color: "var(--text-muted)" }}
                >
                  <ArrowLeft size={18} />
                </button>
              </div>
              <div className="sidebar-content">
                {pages.map(page => (
                  <div
                    key={page.id}
                    className={`nav-item ${activePage === page.id ? "active" : ""}`}
                    onClick={() => loadPage(page.id)}
                  >
                    {page.icon}
                    {page.label}
                  </div>
                ))}
              </div>
            </div>

            <div style={{ flex: 1, background: "white", minHeight: "100vh" }}>
              <motion.div
                key={activePage}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                className="markdown-content"
              >
                <ReactMarkdown>{content}</ReactMarkdown>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        .animate-spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

export default App;
