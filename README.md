# OrbyTech - Cybersecurity Copilot

OrbyTech is a high-performance AI cybersecurity dashboard featuring a modern "Hacker UI," a suite of 9 integrated scanning tools (Nmap, Nikto, WhatWeb, Subfinder, HTTPX, Nuclei, Amass, Katana, GAU), and an AI Cybersecurity Copilot that parses raw logs into actionable intelligence.

## Project Structure

- `/backend` - FastAPI Python server with SSH orchestration and MongoDB persistence.
- `/frontend` - Next.js React client with custom dark glassmorphic styling and real-time polling.

## Prerequisites

To run this project, you need:
- **Python 3.10+**
- **Node.js (v18+)** and **npm**
- **MongoDB** (Local or Atlas URI)
- **Kali Linux VM** (Accessible via SSH for remote command execution)

## Local Setup Instructions

### 1. Backend Setup (FastAPI)

1. Navigate to the backend directory: `cd backend`
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Update `.env` with your SSH credentials for the Kali VM and your MongoDB URL.
5. Start the API server: `uvicorn main:app --reload`

### 2. Frontend Setup (Next.js)

1. Navigate to the frontend directory: `cd frontend`
2. Install npm dependencies: `npm install`
3. Start the dev server: `npm run dev`
4. Visit `http://localhost:3000`.

## Key Features

- **Distributed Scanning Architecture**: Offloads heavy processing to a remote Kali Linux instance via encrypted SSH tunnels.
- **Two-Stage Execution**: Delivers fast results (Nmap/WhatWeb) in seconds while background scans (Nikto/Subfinder) continue deeper analysis.
- **Live Updating Dashboard**: Real-time polling updates the UI as tools complete their execution.
- **Extended Deep Scans**: Configured with 10-minute timeouts to ensure comprehensive vulnerability discovery.
- **Dark Hacker UI**: A visually stunning, high-contrast, glowing UI with Glassmorphic effects and terminal-style outputs.