# FaceChain ⛓️🔍

FaceChain is an automated identity investigation and digital integrity verification pipeline. It analyzes an uploaded face image, searches for potential visual matches across the web, and cryptographically anchors proof of verification on an Ethereum-compatible blockchain.

---

## Architecture

* **Face Detection**: Fast 2D face localization using OpenCV FaceDetectorYN (YuNet).
* **Feature Extraction**: 512-dimensional normalized face embeddings via ArcFace (`buffalo_l`).
* **Web Search**: Candidate retrieval via SerpApi / Google Lens.
* **Visual Matching**: Cosine similarity comparison between candidate images and target face.
* **Blockchain Integrity**: Computes SHA-256 hash of the image and records verification data on a Solidity smart contract using Hardhat and Web3.py.
* **Dashboard**: React interface displaying detection, search candidates, and on-chain verification state.

---

## Tech Stack

* **Frontend**: React, Vite, CSS
* **Backend API**: Python 3.10+, FastAPI, Uvicorn
* **Computer Vision**: OpenCV, YuNet, InsightFace (ArcFace)
* **Search Integration**: SerpApi (Google Lens API)
* **Smart Contracts & Web3**: Solidity, Hardhat, Web3.py

---

## Project Structure

```text
face_blockchain_pipeline/
├── backend/            # FastAPI server & pipeline orchestration
├── blockchain/         # Hardhat smart contract environment
├── frontend/           # React dashboard UI
├── requirements.txt    # Python dependencies
└── README.md