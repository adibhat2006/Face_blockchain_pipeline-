import { useState } from "react";
import "./App.css";

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // ============================================================
  // FILE VALIDATION
  // ============================================================

  const validateFile = (file) => {
    if (!file) {
      return "Please select an image.";
    }

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      return "Only JPG, PNG and WEBP images are supported.";
    }

    const maxSize = 10 * 1024 * 1024;

    if (file.size > maxSize) {
      return "Image size must be less than 10 MB.";
    }

    return "";
  };

  // ============================================================
  // HANDLE FILE
  // ============================================================

  const handleFile = (file) => {
    const validationError = validateFile(file);

    if (validationError) {
      setError(validationError);
      return;
    }

    setError("");
    setResult(null);
    setSelectedFile(file);

    const imageUrl = URL.createObjectURL(file);
    setPreview(imageUrl);
  };

  // ============================================================
  // FILE INPUT
  // ============================================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (file) {
      handleFile(file);
    }
  };

  // ============================================================
  // DRAG & DROP
  // ============================================================

  const handleDrop = (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files?.[0];

    if (file) {
      handleFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  // ============================================================
  // REMOVE IMAGE
  // ============================================================

  const removeImage = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError("");
  };

  // ============================================================
  // START INVESTIGATION
  // ============================================================

  const startInvestigation = async () => {
    if (!selectedFile) {
      setError("Please upload a face image first.");
      return;
    }

    setIsScanning(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      formData.append("file", selectedFile);

      const response = await fetch(
        `${BACKEND_URL}/investigate`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Investigation failed."
        );
      }

      console.log("FACECHAIN INVESTIGATION RESULT:", data);

      setResult(data);

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
        "Unable to connect to FaceChain backend."
      );

    } finally {
      setIsScanning(false);
    }
  };

  // ============================================================
  // HELPERS
  // ============================================================

  const faceDetected =
    result?.face_detection?.face_count > 0;

  const searchResults =
    result?.web_search?.results || [];

  const potentialMatches =
    result?.face_matching?.potential_matches || [];

  const exactMatchCount =
    result?.web_search?.exact_match_count || 0;

  const visualMatchCount =
    result?.web_search?.visual_match_count || 0;

  // ============================================================
  // BLOCKCHAIN DATA
  // ============================================================

  const blockchain = result?.blockchain || null;

  const blockchainStatus =
    blockchain?.status || "not_started";

  const blockchainStored =
    blockchainStatus === "verified" || blockchainStatus === "stored";

  const blockchainExisting =
    blockchainStatus === "already_verified" || blockchainStatus === "already_exists";

  const blockchainFailed =
    blockchainStatus === "failed";

  const blockchainNotStarted =
    !blockchainStored && !blockchainExisting && !blockchainFailed;

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="app">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="header">

        <div className="logo">
          <span className="logo-mark">◈</span>
          <span>FACECHAIN</span>
        </div>

        <div className="header-status">
          <span className="status-dot"></span>
          AI FORENSIC SYSTEM
        </div>

      </header>


      {/* ======================================================
          MAIN
      ====================================================== */}

      <main className="main-container">

        <section className="hero">

          <div className="hero-badge">
            AI • WEB SEARCH • BLOCKCHAIN
          </div>

          <h1>
            FACE
            <span>CHAIN</span>
          </h1>

          <p>
            Face identification and blockchain
            verification pipeline.
          </p>

        </section>


        {/* ==================================================
            PIPELINE
        ================================================== */}

        <section className="pipeline">

          <div className="pipeline-step active">

            <div className="pipeline-number">
              01
            </div>

            <div>
              <strong>FACE SCAN</strong>
              <small>YuNet + ArcFace</small>
            </div>

          </div>

          <div className="pipeline-line"></div>

          <div
            className={
              `pipeline-step ${
                result ? "active" : ""
              }`
            }
          >

            <div className="pipeline-number">
              02
            </div>

            <div>
              <strong>WEB SEARCH</strong>
              <small>Google Lens</small>
            </div>

          </div>

          <div className="pipeline-line"></div>

          <div
            className={
              `pipeline-step ${
                blockchainStored ||
                blockchainExisting
                  ? "active"
                  : ""
              }`
            }
          >

            <div className="pipeline-number">
              03
            </div>

            <div>
              <strong>VERIFY</strong>
              <small>Blockchain</small>
            </div>

          </div>

        </section>


        {/* ==================================================
            UPLOAD CARD
        ================================================== */}

        <section className="upload-card">

          <div className="section-title">
            <span>01</span>
            UPLOAD FACE IMAGE
          </div>


          {!preview ? (

            <label
              className="drop-zone"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >

              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileChange}
              />

              <div className="upload-icon">
                ⬆
              </div>

              <h3>
                DROP IMAGE HERE
              </h3>

              <p>
                or click to browse
              </p>

              <small>
                JPG • PNG • WEBP • MAX 10 MB
              </small>

            </label>

          ) : (

            <div className="preview-container">

              <img
                src={preview}
                alt="Selected face"
                className="preview-image"
              />

              <div className="preview-info">

                <div className="file-name">
                  {selectedFile?.name}
                </div>

                <div className="file-size">
                  {(
                    selectedFile?.size /
                    (1024 * 1024)
                  ).toFixed(2)} MB
                </div>

                <button
                  className="remove-button"
                  onClick={removeImage}
                  disabled={isScanning}
                >
                  REMOVE IMAGE
                </button>

              </div>

            </div>

          )}


          {error && (

            <div className="error-message">
              ⚠ {error}
            </div>

          )}


          <button
            className="scan-button"
            onClick={startInvestigation}
            disabled={
              !selectedFile ||
              isScanning
            }
          >

            {isScanning
              ? "SCANNING FACE & SEARCHING..."
              : "START INVESTIGATION →"
            }

          </button>

        </section>


        {/* ==================================================
            RESULTS
        ================================================== */}

        {result && (

          <section className="results-section">

            {/* ================================================
                FACE DETECTION
            ================================================ */}

            <div className="result-card">

              <div className="result-header">

                <div>

                  <span className="result-number">
                    01
                  </span>

                  <h2>
                    FACE DETECTION
                  </h2>

                </div>

                <span
                  className={
                    faceDetected
                      ? "success-badge"
                      : "failure-badge"
                  }
                >
                  {faceDetected
                    ? "✓ DETECTED"
                    : "✕ NOT DETECTED"
                  }
                </span>

              </div>


              {faceDetected && (

                <div className="stats-grid">

                  <div className="stat">

                    <span>
                      FACES FOUND
                    </span>

                    <strong>
                      {
                        result.face_detection
                          .face_count
                      }
                    </strong>

                  </div>

                  <div className="stat">

                    <span>
                      IMAGE WIDTH
                    </span>

                    <strong>
                      {
                        result.face_detection
                          .image_width
                      }px
                    </strong>

                  </div>

                  <div className="stat">

                    <span>
                      IMAGE HEIGHT
                    </span>

                    <strong>
                      {
                        result.face_detection
                          .image_height
                      }px
                    </strong>

                  </div>

                  <div className="stat">

                    <span>
                      EMBEDDING
                    </span>

                    <strong>
                      {
                        result.face_embedding
                          ?.dimensions || 512
                      }D
                    </strong>

                  </div>

                </div>

              )}

            </div>


            {/* ================================================
                DETECTED FACES
            ================================================ */}

            {faceDetected && (

              <div className="result-card">

                <div className="result-header">

                  <div>

                    <span className="result-number">
                      02
                    </span>

                    <h2>
                      DETECTED FACES
                    </h2>

                  </div>

                </div>


                <div className="face-list">

                  {result.face_detection.faces.map(
                    (face) => (

                      <div
                        className="face-item"
                        key={face.face_id}
                      >

                        <div className="face-id">
                          FACE #{face.face_id}
                        </div>

                        <div className="face-confidence">

                          <span>
                            Confidence
                          </span>

                          <strong>
                            {(
                              face.confidence *
                              100
                            ).toFixed(1)}
                            %
                          </strong>

                        </div>

                        <div className="face-size">

                          {face.width} ×{" "}
                          {face.height}

                        </div>

                      </div>

                    )
                  )}

                </div>

              </div>

            )}


            {/* ================================================
                WEB SEARCH
            ================================================ */}

            <div className="result-card">

              <div className="result-header">

                <div>

                  <span className="result-number">
                    03
                  </span>

                  <h2>
                    WEB SEARCH RESULTS
                  </h2>

                </div>

                <span
                  className={
                    searchResults.length > 0
                      ? "success-badge"
                      : "failure-badge"
                  }
                >
                  {searchResults.length > 0
                    ? `✓ ${searchResults.length} RESULTS`
                    : "NO RESULTS"
                  }
                </span>

              </div>


              {searchResults.length > 0 && (

                <div className="search-summary">

                  <div className="search-stat">

                    <strong>
                      {exactMatchCount}
                    </strong>

                    <span>
                      EXACT MATCHES
                    </span>

                  </div>

                  <div className="search-stat">

                    <strong>
                      {visualMatchCount}
                    </strong>

                    <span>
                      VISUAL MATCHES
                    </span>

                  </div>

                  <div className="search-stat">

                    <strong>
                      {
                        potentialMatches.length
                      }
                    </strong>

                    <span>
                      FACE MATCHES
                    </span>

                  </div>

                </div>

              )}


              <div className="web-results">

                {searchResults.length === 0 ? (

                  <div className="empty-results">
                    No web results were found.
                  </div>

                ) : (

                  searchResults
                    .slice(0, 10)
                    .map((item, index) => {

                      const comparison =
                        item.face_comparison;

                      const similarity =
                        comparison?.similarity;

                      const isPotentialMatch =
                        comparison?.match ===
                        "potential_face_match";

                      return (

                        <div
                          className={
                            `web-result ${
                              isPotentialMatch
                                ? "potential-match"
                                : ""
                            }`
                          }
                          key={
                            `${item.link}-${index}`
                          }
                        >

                          <div className="result-thumbnail">

                            {(
                              item.thumbnail ||
                              item.image
                            ) ? (

                              <img
                                src={
                                  item.thumbnail ||
                                  item.image
                                }
                                alt=""
                                loading="lazy"
                              />

                            ) : (

                              <div className="no-thumbnail">
                                FACE
                              </div>

                            )}

                          </div>


                          <div className="result-content">

                            <div className="result-source">
                              {item.source ||
                                "Web source"}
                            </div>

                            <h3>
                              {item.title ||
                                "Untitled result"}
                            </h3>


                            {similarity !== null &&
                              similarity !== undefined && (

                              <div
                                className={
                                  `similarity ${
                                    isPotentialMatch
                                      ? "high-similarity"
                                      : ""
                                  }`
                                }
                              >

                                <span>
                                  FACE SIMILARITY
                                </span>

                                <strong>
                                  {(
                                    similarity *
                                    100
                                  ).toFixed(2)}
                                  %
                                </strong>

                              </div>

                            )}


                            {comparison?.match && (

                              <div className="match-status">

                                {isPotentialMatch
                                  ? "✓ POTENTIAL FACE MATCH"
                                  : comparison.match ===
                                    "low_confidence_similarity"
                                  ? "• LOW CONFIDENCE SIMILARITY"
                                  : comparison.match ===
                                    "no_face_in_candidate"
                                  ? "NO FACE DETECTED"
                                  : "IMAGE NOT AVAILABLE"
                                }

                              </div>

                            )}


                            {item.link && (

                              <a
                                href={item.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="source-button"
                              >
                                VIEW SOURCE ↗
                              </a>

                            )}

                          </div>

                        </div>

                      );

                    })

                )}

              </div>

            </div>


            {/* ================================================
                TOP POTENTIAL MATCHES
            ================================================ */}

            {potentialMatches.length > 0 && (

              <div className="result-card highlight-card">

                <div className="result-header">

                  <div>

                    <span className="result-number">
                      04
                    </span>

                    <h2>
                      TOP POTENTIAL MATCHES
                    </h2>

                  </div>

                  <span className="success-badge">
                    AI ANALYSIS
                  </span>

                </div>


                <div className="potential-list">

                  {potentialMatches
                    .slice(0, 5)
                    .map((item, index) => {

                      const similarity =
                        item.face_comparison
                          ?.similarity || 0;

                      return (

                        <div
                          className="potential-item"
                          key={index}
                        >

                          <div className="rank">
                            #{index + 1}
                          </div>

                          <div className="potential-info">

                            <strong>
                              {item.title ||
                                "Web result"}
                            </strong>

                            <span>
                              {item.source ||
                                "Unknown source"}
                            </span>

                          </div>

                          <div className="potential-score">

                            {(
                              similarity *
                              100
                            ).toFixed(2)}%

                          </div>

                        </div>

                      );

                    })}

                </div>

              </div>

            )}


            {/* ================================================
                BLOCKCHAIN VERIFICATION
            ================================================ */}

            <div className="blockchain-card">

              <div className="blockchain-icon">
                ⛓
              </div>

              <div className="blockchain-content">

                <span className="result-number">
                  05
                </span>

                <h2>
                  BLOCKCHAIN VERIFICATION
                </h2>


                {/* ==========================================
                    STORED SUCCESSFULLY
                ========================================== */}

                {blockchainStored && (

                  <>
                    <p>
                      Image hash successfully stored
                      on the FaceChain blockchain.
                    </p>

                    <div className="blockchain-details">

                      <div>
                        <span>
                          STATUS
                        </span>

                        <strong>
                          ✓ VERIFIED & STORED
                        </strong>
                      </div>

                      <div>
                        <span>
                          SHA-256 HASH
                        </span>

                        <strong className="hash-text">
                          {blockchain.image_hash || blockchain.hash}
                        </strong>
                      </div>

                      <div>
                        <span>
                          TRANSACTION
                        </span>

                        <strong className="hash-text">
                          {blockchain.transaction_hash}
                        </strong>
                      </div>

                      <div>
                        <span>
                          BLOCK
                        </span>

                        <strong>
                          #{blockchain.block_number||blockchain.block}
                        </strong>
                      </div>

                      {blockchain.contract_address && (

                        <div>
                          <span>
                            CONTRACT
                          </span>

                          <strong className="hash-text">
                            {blockchain.contract_address}
                          </strong>
                        </div>

                      )}

                    </div>

                    <span className="success-badge">
                      ✓ BLOCKCHAIN VERIFIED
                    </span>

                  </>

                )}


                {/* ==========================================
                    RECORD ALREADY EXISTS
                ========================================== */}

                {blockchainExisting && (

                  <>
                    <p>
                      This image hash already exists
                      on the FaceChain blockchain.
                    </p>

                    <div className="blockchain-details">

                      <div>
                        <span>
                          STATUS
                        </span>

                        <strong>
                          ✓ RECORD VERIFIED
                        </strong>
                      </div>

                      <div>
                        <span>
                          SHA-256 HASH
                        </span>

                        <strong className="hash-text">
                          {blockchain.image_hash || blockchain.hash}
                        </strong>
                      </div>

                      <div>
                        <span>
                          ORIGINAL BLOCK
                        </span>

                        <strong>
                          #{blockchain.block_number||blockchain.block}
                        </strong>
                      </div>

                      {blockchain.contract_address && (

                        <div>
                          <span>
                            CONTRACT
                          </span>

                          <strong className="hash-text">
                            {blockchain.contract_address}
                          </strong>
                        </div>

                      )}

                    </div>

                    <span className="success-badge">
                      ✓ EXISTING RECORD VERIFIED
                    </span>

                  </>

                )}


                {/* ==========================================
                    FAILED
                ========================================== */}

                {blockchainFailed && (

                  <>
                    <p>
                      Blockchain verification could
                      not be completed.
                    </p>

                    {blockchain.message && (

                      <div className="error-message">
                        ⚠ {blockchain.message}
                      </div>

                    )}

                    <span className="failure-badge">
                      ✕ BLOCKCHAIN FAILED
                    </span>

                  </>

                )}


                {/* ==========================================
                    NOT STARTED
                ========================================== */}

                {blockchainNotStarted && (

                  <>
                    <p>
                      Blockchain verification has not
                      been completed for this investigation.
                    </p>

                    <span className="pending-badge">
                      PENDING
                    </span>
                  </>

                )}

              </div>

            </div>

          </section>

        )}

      </main>


      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer>

        <span>
          FACECHAIN
        </span>

        <span>
          AI FORENSIC PIPELINE
        </span>

        <span>
          v2.1
        </span>

      </footer>

    </div>
  );
}

export default App;