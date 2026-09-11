# FaceChain 🛡️⛓️

FaceChain is an automated identity investigation and digital integrity verification pipeline[span_0](start_span)[span_0](end_span). It scans an uploaded face image, searches for potential visual matches across the web, and cryptographically anchors proof of the image onto the Ethereum blockchain[span_1](start_span)[span_1](end_span).

## Architecture

* **Face Detection**: Fast 2D face localization using OpenCV FaceDetectorYN (YuNet)[span_2](start_span)[span_2](end_span).
* **Feature Extraction**: 512-dimensional normalized face embeddings via ArcFace (`buffalo_l`)[span_3](start_span)[span_3](end_span).
* **Web Search**: Candidate retrieval via SerpApi / Google Lens[span_4](start_span)[span_4](end_span).
* **Visual Matching**: Cosine similarity comparison between candidate images and target face[span_5](start_span)[span_5](end_span).
* **Blockchain Integrity**: Computes SHA-256 hash of the image and records verification data on a Solidity smart contract deployed to a local Hardhat network[span_6](start_span)[span_6](end_span).
* **Dashboard**: React interface displaying detection, search candidates, and on-chain verification state[span_7](start_span)[span_7](end_span).

## Tech Stack

* **Frontend**: React + Vite[span_8](start_span)[span_8](end_span)
* **Backend API**: Python, FastAPI, Uvicorn[span_9](start_span)[span_9](end_span)
* **Computer Vision**: OpenCV, YuNet, InsightFace (ArcFace)[span_10](start_span)[span_10](end_span)
* **Search Integration**: SerpApi (Google Lens API)[span_11](start_span)[span_11](end_span)
* **Smart Contracts & Web3**: Solidity, Hardhat, Web3.py[span_12](start_span)[span_12](end_span)
*