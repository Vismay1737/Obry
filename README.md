# OrbyTech - AI Cybersecurity Copilot

OrbyTech is an AI-powered cybersecurity platform featuring a modern Dark Hacker UI, automated vulnerability scanning (Nmap, Nikto, WhatWeb, Subfinder), and OpenAI-driven risk analysis and reporting.

## Project Structure

- `/backend` - FastAPI Python server with tool integrations and MongoDB models.
- `/frontend` - Next.js React client with custom dark glassmorphic styling.

## Prerequisites

To run this project, you need to have the following installed on your machine:
- **Python 3.10+**
- **Node.js (v18+)** and **npm**
- **MongoDB** running locally or a MongoDB Atlas URI
- The following security tools accessible via your system's `PATH`:
  - `nmap`
  - `nikto`
  - `whatweb`
  - `subfinder`

## Local Setup Instructions

### 1. Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   **Update the `.env` file** with your OpenAI API Key and MongoDB URL.
5. Start the API server:
   ```bash
   uvicorn main:app --reload
   ```

### 2. Frontend Setup (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:3000` to access the OrbyTech Dashboard.

## Features

- **Dark Hacker UI**: A visually stunning, high-contrast, glowing UI inspired by modern sci-fi interfaces.
- **Microservice Orchestration**: Concurrently runs multiple standard cybersecurity tools against targets.
- **AI Triage**: Parses raw CLI outputs from tools to generate a unified 0-100 Security Score.
- **Reporting**: Clearly presents risks chronologically, categorized by severity, with actionable remediation instructions.