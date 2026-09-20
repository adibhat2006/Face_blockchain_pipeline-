# FaceChain: Decentralized Biometric Verification Pipeline

FaceChain is an end-to-end computer vision and blockchain verification pipeline designed to detect facial features, cross-reference them against visual web indexes via Google Lens (SerpApi), and immutably record cryptographic verification proofs on an Ethereum/Hardhat blockchain ledger.

---

## System Architecture

1. **Frontend**: React + Vite interface allowing users to upload facial images and observe real-time pipeline status and on-chain verification receipts.
2. **Backend**: FastAPI web server orchestrating the detection, feature extraction, external search query, and Web3 interactions.
3. **Computer Vision Layer**:
   - **Face Detection**: OpenCV YuNet ONNX model for bounding-box and landmark detection.
   - **Feature Embedding**: InsightFace / ArcFace for high-dimensional biometric representation.
4. **Search Integration**: SerpApi Google Lens visual search engine integration for identifying duplicate or matching profiles across the public web.
5. **Blockchain Layer**: Solidity smart contract (`FaceChain.sol`) deployed to Hardhat local node for tamper-proof verification history logging.

---

## Security & Privacy Highlights

- **Salted Biometric Fingerprints**: Biometric hashes stored on-chain utilize a secret server-side salt via HMAC-SHA256, protecting against rainbow table attacks and public lookup correlation.
- **Strict Environment Separation**: All private keys, RPC URLs, contract addresses, and API credentials reside strictly in local `.env` files managed via `python-dotenv`.
- **Pre-execution Validation**: Rigorous checks enforce acceptable MIME types (JPEG, PNG, WebP), verify non-empty payloads, confirm image matrix decoding, and validate face detection prior to downstream blockchain transactions.
- **Transaction Receipt Controls**: Web3 state modifications enforce receipt confirmations with a 120-second timeout to handle high gas conditions and prevent deadlocks.

---

## Repository Structure

```text
face_blockchain_pipeline/
├── backend/
│   ├── main.py              # FastAPI pipeline endpoints & validation
│   ├── blockchain.py        # Web3 transaction building & contract caller
│   ├── requirements.txt     # Python backend dependencies
│   ├── Dockerfile           # Backend container definition
│   └── models/              # Neural network weights (YuNet, ArcFace)
├── frontend/                # React dashboard application
├── blockchain/
│   ├── contracts/           # FaceChain.sol Solidity contracts
│   └── hardhat.config.js    # Hardhat network configuration
├── docker-compose.yml       # Multi-container orchestration
├── .env.example             # Safe template for environment variables
└── README.md                # System documentation