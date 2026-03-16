# OrbyTech - AI Cybersecurity Copilot & Autonomous Remediation Engine

OrbyTech is a high-performance, enterprise-grade AI cybersecurity dashboard. It features a stunning Cyberpunk "Hacker UI" with live CRT scanlines, a suite of 9 integrated scanning tools (Nmap, Nikto, WhatWeb, Subfinder, HTTPX, Nuclei, Amass, Katana, GAU), and a **Zero-Trust Autonomous AI Engine** that not only parses raw logs but generates the exact remediation scripts needed to fix the vulnerabilities.

## 🚀 The Hackathon Winning Features

1. **Zero-Trust Input Validation & SSRF Protection**
   - The backend API strictly sanitizes all user inputs.
   - Command injection (`; rm -rf /`) is impossible.
   - Server-Side Request Forgery (SSRF) is blocked. Users cannot scan internal IP addresses (e.g., `127.0.0.1`, `192.168.x.x`, `169.254.169.254`).

2. **Real-time Live Streaming via WebSockets**
   - No more fake loading bars or clunky HTTP polling.
   - OrbyTech utilizes an asynchronous iterative stream over `websockets`. Watch Nmap, Nuclei, and Subfinder dump their payloads live onto the screen while the scan executes.

3. **Autonomous AI Remediation (Llama 3.1 405b via NVIDIA NIM)**
   - The AI doesn't just say "Port 80 is open." It generates structured JSON containing the exact `Bash`, `UFW`, or `Terraform` scripts the administrator needs to fix the flaw instantly.
   - Click "Copy Script" in the UI to deploy the autonomous fix.

## Project Structure

- `/backend` - FastAPI Python server with SSH orchestration, WebSockets, and MongoDB persistence.
- `/frontend` - Next.js React client with custom Cyberpunk Neo-Matrix styling and live terminal streaming.

## Prerequisites

To run this project natively:
- **Python 3.10+**
- **Node.js (v18+)** and **npm**
- **MongoDB** (Local or Atlas URI)
- **Kali Linux VM** (Accessible via SSH for remote command execution)

## Local Setup Instructions

### 1. Backend Setup (FastAPI)

1. Navigate to the backend directory: `cd backend`
2. Create and activate a Python virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Update `.env` with your SSH credentials for the Kali VM, your NVIDIA NIM API Key, and your MongoDB URL.
5. Start the API server: `python -m uvicorn main:app --reload`

### 2. Frontend Setup (Next.js)

1. Navigate to the frontend directory: `cd frontend`
2. Install npm dependencies: `npm install`
3. Start the dev server: `npm run dev`
4. Visit `http://localhost:3000` to interact with the OrbyTech terminal.

## Key Architecture Decisions

- **Distributed Scanning Architecture**: Offloads all heavy processing to an isolated Kali Linux instance via encrypted SSH multiplexed tunnels. The backend server never runs the tools directly, preventing host compromise.
- **Concurrent Execution**: All 9 tools execute simultaneously over multiplexed SSH streams.
- **AI-Driven JSON Extraction**: The Large Language Model runs strictly in structured JSON mode to guarantee frontend compatibility for vulnerability card rendering. 

*Designed and Built for the Global Hackathon.*