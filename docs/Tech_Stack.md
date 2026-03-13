# Technology Stack - OrbyTech

## 1. Frontend Layer
| Technology | Usage |
| :--- | :--- |
| **Next.js 14** | Core web framework with App Router support. |
| **React** | Component-based UI logic and state management. |
| **Vanilla CSS** | custom-built design system with Glassmorphism and CSS variables. |
| **Google Fonts** | "Space Grotesk" for UI and "JetBrains Mono" for code. |

## 2. Backend Layer
| Technology | Usage |
| :--- | :--- |
| **FastAPI** | Modern, fast ASGI framework for Python. |
| **Uvicorn** | High-performance production server for the API. |
| **AsyncSSH** | Asynchronous SSHv2 client library for remote command execution. |
| **Pydantic v2** | Data parsing and validation for API models. |
| **Python Dotenv** | Configuration and environment variable management. |

### 2.1 Execution Architecture
- **Concurrent Scanning:** All 9 security tools execute in parallel using SSH connection multiplexing. Results are saved incrementally as each tool finishes.
- **Connection Multiplexing:** Share a single persistent SSH tunnel across all concurrent tasks to eliminate handshake overhead.
- **Optimized Timeouts:** Individual tool caps (e.g., 180s for Nikto, 120s for Nuclei) ensure a fast and predictable user experience.

## 3. Data Storage
| Technology | Usage |
| :--- | :--- |
| **MongoDB Atlas** | Cloud-native NoSQL database for persistent storage of scan history and raw outputs. |
| **Motor** | Non-blocking, asynchronous driver for MongoDB in Python. |

## 4. Security Toolchain (9 Tools)
| Tool | Purpose | Status |
| :--- | :--- | :--- |
| **Nmap** | Port scanning and service discovery. | Active |
| **WhatWeb** | Web technology and CMS fingerprinting. | Active |
| **HTTPX** | Probing alive domains and tech stacks. | Active |
| **Subfinder** | Passive subdomain enumeration. | Active |
| **Amass** | Deep subdomain enum and DNS mapping. | Active |
| **GAU** | Fetching known URLs from web archives. | Active |
| **Nikto** | Web server vulnerability scanning. | Active |
| **Nuclei** | Template-based vulnerability assessment. | Active |
| **Katana** | Advanced website crawling and parsing. | Active |
| **AI Copilot** | Log synthesis and remediation analysis (GPT-4/Llama). | Active |

## 5. Development & DevOps
| Technology | Usage |
| :--- | :--- |
| **Pip/Venv** | Python dependency and environment management. |
| **NPM** | Node.js package management. |
| **Git/GitHub** | Version control and collaboration. |
| **VirtualBox** | Locally hosted Kali Linux virtualization. |
