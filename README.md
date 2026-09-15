# FaceChain: Forensic Facial Analysis & Immutable Provenance Ledger

FaceChain is an automated end-to-end forensic investigation pipeline that bridges computer vision, reverse web intelligence, and decentralized ledgers. The platform ingests facial imagery, performs high-precision face detection and biometric feature alignment, cross-references digital footprints across open-web sources, generates an immutable cryptographic fingerprint of discovered media assets, and permanently commits the attestation record to an Ethereum-compatible smart contract for tamper-evident timestamping and provenance tracking.

---

## Technical Architecture
[ Input Target Image ]
│
▼
[ Biometric Detection Engine ]
├── OpenCV YuNet / InsightFace SCRFD
└── Landmark Alignment & Crop Extraction
│
▼
[ Web Reconnaissance Subsystem ]
├── SerpApi / Google Lens Reverse Image Lookup
└── Structured Social Media Entity Extraction (X, LinkedIn, Instagram, etc.)
│
▼
[ Cryptographic Hashing Engine ]
└── SHA-256 Digest of (Source URL + Post Metadata + Content Fingerprint)
│
▼
[ Decentralized Ledger Attestation ]
├── Hardhat Local / Ethereum Testnet (Sepolia/Amoy)
└── FaceChain.sol (storeFaceRecord & verifyFaceRecord)
│
▼
[ Forensic Verification & Tamper Audit Report ]
---

## Directory Structure

```text
face_blockchain_pipeline/
├── backend/
│   ├── main.py                  # FastAPI server, pipeline orchestrator & API routes
│   └── blockchain.py            # Web3.py client wrapper for smart contract calls
├── blockchain/
│   ├── contracts/
│   │   └── FaceChain.sol        # Solidity immutable attestation contract
│   ├── scripts/
│   │   └── deploy-facechain.ts  # Hardhat automated deployment routine
│   ├── hardhat.config.ts        # EVM compiler options & network targets
│   └── package.json             # Hardhat & ethers toolchain manifest
├── frontend/                    # Web client for image uploads and audit logs
├── input/                       # Staging directory for incoming forensic images
├── output/                      # Processed face crops and investigation summaries
├── scripts/                     # Standalone CLI scripts for isolated model testing
├── .env                         # Secrets, RPC endpoints, and contract addresses
├── requirements.txt             # Python backend dependencies
└── README.md                    # Project documentation
```
---

## Key Capabilities

Multi-Engine Face Detection: High-speed inference using OpenCV YuNet paired with InsightFace feature extraction for reliable face localization even under adverse lighting or severe pose variation.

Deep Reverse Reconnaissance: Leverages reverse image search APIs to identify exact or probable matches across modern social media platforms.

Tamper-Proof Data Hashing: Discovered links, post text, and media hashes are normalized and condensed into a deterministic 256-bit cryptographic digest (bytes32).

On-Chain Notarization: Transactions executed against the FaceChain contract bind the post digest to the submitter's Ethereum address and the exact block timestamp, eliminating backdating risks.

Duplicate Detection & Instant Audit: The smart contract prevents redundant submissions and supports zero-gas eth_call queries to verify existing forensic records in milliseconds.
---

## Prerequisites

Node.js: v18.x or v20.x with npm

Python: 3.10 or 3.11 (recommended for InsightFace/ONNX compatibility)

C++ Build Tools: Required on Windows for compiling certain native Python wheels

SerpApi Key: Active API token from SerpApi for reverse image queries
---

## Step-by-Step Setup Guide
1. Repository Setup
Clone the repository and prepare the root directory:

Bash
git clone <your-repository-url>
cd face_blockchain_pipeline

2. Smart Contract Compilation & Local Node
Open a terminal dedicated to the blockchain layer:

Bash
cd blockchain
npm install
npx hardhat compile
Start your persistent local Hardhat EVM node:

Bash
npx hardhat node
Keep this terminal running. Note down the deployed test accounts, specifically Account #0's address and private key.

In a separate terminal, deploy FaceChain.sol to your local node:

Bash
cd blockchain
npx hardhat console --network localhost
Inside the interactive console, execute:

JavaScript
const FaceChain = await ethers.getContractFactory("FaceChain");
const faceChain = await FaceChain.deploy();
await faceChain.waitForDeployment();
console.log("FaceChain deployed to:", await faceChain.getAddress());
.exit

Record the resulting contract address (default: 0x5FbDB2315678afecb367f032d93F642f64180aa3).

3. Environment Variable Configuration
Create a .env file inside the root directory (face_blockchain_pipeline/.env):

Ini, TOML
# Blockchain Network Configuration
BLOCKCHAIN_RPC_URL=[http://127.0.0.1:8545](http://127.0.0.1:8545)
FACECHAIN_CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
BLOCKCHAIN_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# External Intelligence APIs
SERPAPI_KEY=your_actual_serpapi_key_here
4. Python Backend Configuration
From the root directory, configure your virtual environment:

Windows (PowerShell):

PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
If requirements.txt is missing specific dependencies, run:

PowerShell
pip install fastapi uvicorn python-multipart opencv-python numpy web3 python-dotenv insightface onnxruntime requests
Launch the forensic API server:

PowerShell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
API Specification
Interactive Swagger/OpenAPI documentation is available live at http://127.0.0.1:8000/docs.

1. Health & Node Diagnostics
Route: GET /health

Purpose: Confirms API readiness, model loading state, and active JSON-RPC connection to the blockchain.

Sample Response:

JSON
{
  "status": "healthy",
  "blockchain": {
    "connected": true,
    "network_id": 31337,
    "latest_block": 1,
    "contract_address": "0x5FbDB2315678afecb367f032d93F642f64180aa3"
  }
}
2. Forensic Ingestion & Verification Pipeline
Route: POST /investigate

Content-Type: multipart/form-data

Body: file (Binary image file)

Workflow:

Detects all human faces; computes bounding boxes and crops.

Submits face artifacts to SerpApi Google Lens reverse image search.

Extracts top candidate social posts and URLs.

Generates a deterministic SHA-256 post fingerprint.

Commits storeFaceRecord(postHash) to FaceChain.sol via local Hardhat wallet.

Sample Response:

JSON
{
  "investigation_id": "inv_9381048",
  "faces_detected": 1,
  "top_match": {
    "source": "Twitter/X",
    "title": "Profile Update / User Post",
    "link": "[https://x.com/sample_user/status/1234567890](https://x.com/sample_user/status/1234567890)"
  },
  "blockchain_record": {
    "status": "verified",
    "verified": true,
    "post_hash": "0x4f83b8b1a8d05541e202517865fcdb4923f1737e94cb02ff7a1c8901e18bc253",
    "transaction_hash": "0x3f51a84beec3126f58f5bc63212871ad29045b84950e167ff8dfb776269df6d3",
    "block_number": 2,
    "contract_address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "submitted_by": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
  }
}
3. Record Audit Verification
Route: GET /verify/{post_hash}

Purpose: Queries the immutable mapping on FaceChain.sol to retrieve the original timestamp and attester address without sending a state-changing transaction.

Contract Implementation Details
The underlying Solidity implementation uses a gas-optimized mapping keyed by the cryptographic post hash:

Solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

contract FaceChain {
    struct Record {
        uint256 timestamp;
        address submittedBy;
        bool exists;
    }

    mapping(bytes32 => Record) private records;

    event RecordStored(bytes32 indexed postHash, address indexed submittedBy, uint256 timestamp);

    function storeFaceRecord(bytes32 postHash) external {
        require(!records[postHash].exists, "Record already exists");
        records[postHash] = Record(block.timestamp, msg.sender, true);
        emit RecordStored(postHash, msg.sender, block.timestamp);
    }

    function verifyFaceRecord(bytes32 postHash) external view returns (bool verified, uint256 timestamp, address submittedBy) {
        Record memory rec = records[postHash];
        return (rec.exists, rec.timestamp, rec.submittedBy);
    }
}
Common Troubleshooting
Blockchain Unreachable (Connection refused at 127.0.0.1:8545):

Ensure npx hardhat node is actively running in its own terminal before booting the FastAPI backend.

ABI File Not Found:

Run npx hardhat compile inside the blockchain/ folder to regenerate artifacts/contracts/FaceChain.sol/FaceChain.json.

Zero Results from Reverse Search:

Verify your SERPAPI_KEY is present and funded with queries in .env.