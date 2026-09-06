import {
  ScanFace,
  Search,
  ShieldCheck,
  Database,
  Upload,
  ArrowRight,
  CheckCircle2,
  Circle,
} from "lucide-react";

import "./App.css";

function PipelineStep({ icon, title, description, active }) {
  return (
    <div className={`pipeline-step ${active ? "active" : ""}`}>
      <div className="step-icon">{icon}</div>

      <div className="step-info">
        <strong>{title}</strong>
        <span>{description}</span>
      </div>

      {active ? (
        <CheckCircle2 className="step-check" size={17} />
      ) : (
        <Circle className="step-check" size={17} />
      )}
    </div>
  );
}

function App() {
  return (
    <div className="app">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            <ScanFace size={24} />
          </div>

          <div>
            <h1>
              FACE<span>CHAIN</span>
            </h1>
            <p>IDENTITY FORENSICS</p>
          </div>
        </div>

        <nav>
          <button className="nav-item active">
            <ScanFace size={18} />
            Investigation
          </button>

          <button className="nav-item">
            <Database size={18} />
            Blockchain
          </button>

          <button className="nav-item">
            <Search size={18} />
            Search History
          </button>
        </nav>

        <div className="network-status">
          <div className="status-dot"></div>

          <div>
            <strong>LOCAL NETWORK</strong>
            <span>Blockchain connected</span>
          </div>
        </div>

      </aside>


      {/* MAIN */}
      <main className="main">

        <header className="topbar">

          <div>
            <p className="eyebrow">
              SECURE INVESTIGATION SYSTEM
            </p>

            <h2>
              Face Identification
              <br />
              <span>& Blockchain Verification</span>
            </h2>
          </div>

          <div className="system-status">
            <span></span>
            SYSTEM READY
          </div>

        </header>


        {/* UPLOAD */}
        <section className="card upload-card">

          <div className="section-heading">

            <div>
              <p className="section-number">01 / INPUT</p>

              <h3>Upload Face Scan</h3>

              <p className="description">
                Provide an image containing the face you want
                to investigate.
              </p>
            </div>

            <ScanFace size={32} />

          </div>


          <div className="upload-area">

            <div className="upload-icon">
              <Upload size={28} />
            </div>

            <h4>Drop your image here</h4>

            <p>JPG • JPEG • PNG • WEBP</p>

            <button className="primary-button">
              SELECT IMAGE
              <ArrowRight size={16} />
            </button>

          </div>

        </section>


        {/* PIPELINE */}
        <section className="card pipeline-card">

          <div className="section-heading">

            <div>
              <p className="section-number">02 / PIPELINE</p>
              <h3>Investigation Pipeline</h3>
            </div>

            <div className="live-indicator">
              ● LIVE
            </div>

          </div>


          <div className="pipeline">

            <PipelineStep
              icon={<ScanFace size={20} />}
              title="Face Detection"
              description="Detect & encode"
              active={true}
            />

            <div className="connector"></div>

            <PipelineStep
              icon={<Search size={20} />}
              title="Web Search"
              description="Find matching content"
              active={false}
            />

            <div className="connector"></div>

            <PipelineStep
              icon={<Database size={20} />}
              title="Blockchain"
              description="Create fingerprint"
              active={false}
            />

            <div className="connector"></div>

            <PipelineStep
              icon={<ShieldCheck size={20} />}
              title="Verification"
              description="Verify integrity"
              active={false}
            />

          </div>

        </section>


        {/* RESULTS */}
        <div className="bottom-grid">

          <section className="card result-card">

            <div className="card-title">

              <div>
                <p className="section-number">03 / MATCH</p>
                <h3>Matching Content</h3>
              </div>

              <Search size={21} />

            </div>


            <div className="empty-state">

              <Search size={30} />

              <p>No investigation started</p>

              <span>
                Upload a face image to begin searching.
              </span>

            </div>

          </section>


          <section className="card verification-card">

            <div className="card-title">

              <div>
                <p className="section-number">04 / TRUST</p>
                <h3>Blockchain Status</h3>
              </div>

              <ShieldCheck size={21} />

            </div>


            <div className="empty-state">

              <div className="shield">
                <ShieldCheck size={27} />
              </div>

              <strong>AWAITING VERIFICATION</strong>

              <span>
                A blockchain fingerprint will appear
                after a matching result is found.
              </span>

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}

export default App;