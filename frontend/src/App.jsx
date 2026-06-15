import { useEffect, useState } from "react";
import axios from "axios";
import jsPDF from "jspdf";
import "./App.css";

const BASE_URL = "http://127.0.0.1:8000";
const ANALYZE_URL = `${BASE_URL}/analyze`;

function getSection(title, text) {
  const pattern = new RegExp(`${title}:([\\s\\S]*?)(?=\\n\\d+\\. |$)`, "i");
  const match = text?.match(pattern);
  return match ? match[1].trim() : "Not available";
}

function App() {
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [complaint, setComplaint] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedUser = localStorage.getItem("echocase_user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const registerUser = async () => {
    if (!name || !email || !password) {
      alert("Please fill all fields.");
      return;
    }

    const response = await axios.post(`${BASE_URL}/register`, {
      name,
      email,
      password,
    });

    if (response.data.error) {
      alert(response.data.error);
    } else {
      alert("Registration successful. Please login.");
      setAuthMode("login");
    }
  };

  const loginUser = async () => {
    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }

    const response = await axios.post(`${BASE_URL}/login`, {
      email,
      password,
    });

    if (response.data.error) {
      alert(response.data.error);
    } else {
      localStorage.setItem("echocase_user", JSON.stringify(response.data.user));
      setUser(response.data.user);
    }
  };

  const logoutUser = () => {
    localStorage.removeItem("echocase_user");
    setUser(null);
    setResult(null);
    setComplaint("");
    setHistory([]);
  };

  const analyzeComplaint = async () => {
    if (!complaint.trim()) {
      alert("Please enter your complaint.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(ANALYZE_URL, {
        complaint,
        user_id: user.id,
      });

      setResult(response.data);

      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    } catch (error) {
      alert("API Error. Make sure FastAPI backend is running.");
    }

    setLoading(false);
  };

  const loadHistory = async () => {
    const response = await axios.get(`${BASE_URL}/history/${user.id}`);
    setHistory(response.data.history);
  };

  const downloadTextReport = () => {
    if (!result) return;

    const report = `
EchoCase Financial Complaint Intelligence Report

Complaint:
${result.complaint}

AI Analysis:
${result.analysis}
`;

    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "EchoCase_Report.txt";
    link.click();

    URL.revokeObjectURL(url);
  };

  const downloadPDFReport = () => {
    if (!result) return;

    const doc = new jsPDF();
    const margin = 15;
    const pageWidth = doc.internal.pageSize.getWidth();

    doc.setFontSize(18);
    doc.text("EchoCase Intelligence Report", margin, 20);

    doc.setFontSize(11);

    const content = `
Complaint:
${result.complaint}

AI Analysis:
${result.analysis}
`;

    const lines = doc.splitTextToSize(content, pageWidth - 30);
    doc.text(lines, margin, 35);

    doc.save("EchoCase_Report.pdf");
  };

  const analysis = result?.analysis || "";

  if (!user) {
    return (
      <div className="website auth-page">
        <div className="auth-card">
          <div className="auth-logo">EC</div>

          <h1>EchoCase</h1>
          <p className="auth-subtitle">
            Financial Complaint Intelligence Platform
          </p>

          <div className="auth-tabs">
            <button
              className={authMode === "login" ? "active" : ""}
              onClick={() => setAuthMode("login")}
            >
              Login
            </button>

            <button
              className={authMode === "register" ? "active" : ""}
              onClick={() => setAuthMode("register")}
            >
              Register
            </button>
          </div>

          {authMode === "register" && (
            <input
              type="text"
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          )}

          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {authMode === "login" ? (
            <button className="main-btn" onClick={loginUser}>
              Login to EchoCase
            </button>
          ) : (
            <button className="main-btn" onClick={registerUser}>
              Create Account
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="website">
      <header className="navbar">
        <div className="logo">
          <span>EC</span>
          <div>
            <h2>EchoCase</h2>
            <p>Complaint Intelligence</p>
          </div>
        </div>

        <nav>
          <a href="#home">Home</a>
          <a href="#analyze">Analyze</a>
          <a href="#features">Features</a>
          <a href="#workflow">Workflow</a>
          <a href="#history" onClick={loadHistory}>History</a>
          <a href="#about">About</a>
        </nav>

        <button className="nav-cta" onClick={logoutUser}>
          Logout
        </button>
      </header>

      <section className="hero section" id="home">
        <div className="hero-left">
          <span className="badge">AI Financial Complaint Intelligence</span>

          <h1>Resolve financial complaints with smarter case insight.</h1>

          <p>
            EchoCase helps users understand financial disputes by retrieving similar
            historical complaints, identifying risk, suggesting evidence, and preparing
            action-ready guidance.
          </p>

          <div className="hero-buttons">
            <a href="#analyze">Analyze Complaint</a>
            <a href="#workflow" className="outline">See Workflow</a>
          </div>
        </div>

        <div className="hero-right">
          <div className="main-orb">CASE</div>
          <div className="chip chip1">Vector Search</div>
          <div className="chip chip2">Risk Check</div>
          <div className="chip chip3">AI Report</div>
        </div>
      </section>

      <section className="stats-grid">
        <div><h3>40K+</h3><p>Indexed complaint cases</p></div>
        <div><h3>5</h3><p>Similar cases retrieved</p></div>
        <div><h3>AI</h3><p>Guidance generation</p></div>
        <div><h3>PDF</h3><p>Downloadable reports</p></div>
      </section>

      <section className="section" id="analyze">
        <div className="section-title">
          <h1>Analyze Complaint</h1>
          <p>
            Enter your issue and EchoCase will generate a structured complaint intelligence report.
          </p>
        </div>

        <div className="analyze-layout">
          <div className="card input-card">
            <h2>Complaint Details</h2>

            <textarea
              value={complaint}
              maxLength={1000}
              onChange={(e) => setComplaint(e.target.value)}
              placeholder="Example: A debt collection agency is trying to collect money that I already paid..."
            />

            <p className="count">{complaint.length}/1000 characters</p>

            <button className="main-btn" onClick={analyzeComplaint} disabled={loading}>
              {loading ? "Generating Report..." : "Generate Intelligence Report"}
            </button>
          </div>

          <div className="card steps-card">
            <h2>What You Receive</h2>
            <div><span>01</span><p>Complaint category and main issue</p></div>
            <div><span>02</span><p>Risk level and strength score</p></div>
            <div><span>03</span><p>Evidence checklist</p></div>
            <div><span>04</span><p>Suggested next steps</p></div>
            <div><span>05</span><p>Saved history and PDF report</p></div>
          </div>
        </div>

        {loading && (
          <div className="loading-card">
            <div className="loader"></div>
            <p>Retrieving similar cases and preparing your report...</p>
          </div>
        )}
      </section>

      {result && (
        <section className="section" id="results">
          <div className="section-title">
            <h1>Intelligence Report</h1>
            <p>Your complaint analysis displayed as clear, separated decision cards.</p>
          </div>

          <div className="download-actions">
            <button onClick={downloadTextReport}>Download TXT Report</button>
            <button onClick={downloadPDFReport}>Download PDF Report</button>
          </div>

          <section className="result-metrics">
            <div className="metric danger">
              <p>Risk Level</p>
              <h2>{getSection("Risk Level", analysis).split("\n")[0]}</h2>
            </div>

            <div className="metric">
              <p>Strength Score</p>
              <h2>{getSection("Complaint Strength Score", analysis).split("\n")[0]}</h2>
            </div>

            <div className="metric">
              <p>Category</p>
              <h2>{getSection("Complaint Category", analysis).split("\n")[0]}</h2>
            </div>

            <div className="metric">
              <p>Similar Cases</p>
              <h2>{result.similar_cases.length}</h2>
            </div>
          </section>

          <section className="report-grid">
            <div className="card">
              <h2>Main Issue</h2>
              <p>{getSection("Main Issue Identified", analysis)}</p>
            </div>

            <div className="card">
              <h2>Similar Pattern</h2>
              <p>{getSection("Similar Case Pattern", analysis)}</p>
            </div>

            <div className="card">
              <h2>Evidence Checklist</h2>
              <p>{getSection("Evidence Checklist", analysis)}</p>
            </div>

            <div className="card">
              <h2>Suggested Next Steps</h2>
              <p>{getSection("Suggested Next Steps", analysis)}</p>
            </div>
          </section>

          <section className="card draft-card">
            <h2>Draft Complaint Statement</h2>
            <p>{getSection("Draft Complaint Statement", analysis)}</p>
          </section>
        </section>
      )}

      <section className="section" id="history">
  <div className="section-title">
    <h1>Complaint History</h1>
    <p>Your previously analyzed complaints, saved under your account.</p>
  </div>

  <div className="history-top">
    <button className="main-btn" onClick={loadHistory}>
      Refresh History
    </button>
  </div>

  <div className="history-list">
    {history.length === 0 ? (
      <div className="card empty-history">
        <h2>No history yet</h2>
        <p>Your analyzed complaints will appear here.</p>
      </div>
    ) : (
      history.map((item) => (
        <div className="history-card" key={item.id}>
          <div className="history-card-top">
            <div>
              <h2>{item.complaint}</h2>
              <p>{item.created_at}</p>
            </div>

            <span className="history-badge">
              Saved Report
            </span>
          </div>

          <div className="history-preview">
            <div>
              <h4>Category</h4>
              <p>{getSection("Complaint Category", item.analysis).split("\n")[0]}</p>
            </div>

            <div>
              <h4>Risk</h4>
              <p className="risk-text">
                {getSection("Risk Level", item.analysis).split("\n")[0]}
              </p>
            </div>

            <div>
              <h4>Score</h4>
              <p>{getSection("Complaint Strength Score", item.analysis).split("\n")[0]}</p>
            </div>
          </div>

          <details>
            <summary>View Full Report</summary>
            <p>{item.analysis}</p>
          </details>
        </div>
      ))
    )}
  </div>
</section>

      <section className="section" id="features">
        <div className="section-title">
          <h1>Platform Features</h1>
          <p>Everything needed to understand, organize, and prepare a financial complaint.</p>
        </div>

        <div className="feature-grid">
          <div className="card"><h2>Similar Case Search</h2><p>Finds related complaint patterns from historical case records.</p></div>
          <div className="card"><h2>Risk Detection</h2><p>Identifies whether the issue indicates low, medium, or high consumer risk.</p></div>
          <div className="card"><h2>Evidence Guide</h2><p>Suggests documents that can support the complaint.</p></div>
          <div className="card"><h2>Saved History</h2><p>Stores user complaint reports securely in account history.</p></div>
        </div>
      </section>

      <section className="section" id="workflow">
        <div className="section-title">
          <h1>Workflow</h1>
          <p>From complaint input to final report, EchoCase follows a transparent intelligence pipeline.</p>
        </div>

        <div className="workflow-grid">
          {[
            ["01", "User Login", "User signs in to access personalized complaint history."],
            ["02", "Complaint Input", "User submits complaint details."],
            ["03", "Vector Search", "Similar complaints are retrieved."],
            ["04", "AI Analysis", "AI evaluates risk, evidence, and next steps."],
            ["05", "Report Output", "A structured report is generated."],
            ["06", "History Storage", "The report is saved in the user's account."]
          ].map((step) => (
            <div className="workflow-card" key={step[0]}>
              <span>{step[0]}</span>
              <h2>{step[1]}</h2>
              <p>{step[2]}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section about-section" id="about">
        <div className="section-title about-title">
          <span className="badge">About EchoCase</span>
          <h1>Built to make complaint decisions clearer.</h1>
          <p>
            EchoCase helps users understand financial complaints through similar case
            patterns, risk interpretation, evidence guidance, and structured action steps.
          </p>
        </div>

        <div className="about-grid">
          <div className="about-main">
            <h2>What EchoCase Does</h2>
            <p>
              EchoCase turns unstructured complaint descriptions into organized intelligence.
              It helps users identify the issue, understand possible risk, compare similar
              complaint patterns, and prepare a stronger response.
            </p>

            <div className="about-points">
              <div><h3>01</h3><p>Understands the complaint context</p></div>
              <div><h3>02</h3><p>Finds similar historical cases</p></div>
              <div><h3>03</h3><p>Generates practical next steps</p></div>
            </div>
          </div>

          <div className="about-side">
            <h2>Designed For</h2>
            <div className="about-item">Consumers facing financial disputes</div>
            <div className="about-item">People preparing complaint statements</div>
            <div className="about-item">Users needing evidence guidance</div>
          </div>
        </div>
      </section>

      <footer>
        <p className="copyright">
          © 2026 EchoCase. All rights reserved.
        </p>
      </footer>
    </div>
  );
}

export default App;