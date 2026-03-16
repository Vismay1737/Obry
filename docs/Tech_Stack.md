# Technology Stack - OrbyTech Enterprise Architecture

## 1. Frontend Layer
| Technology | Usage |
| :--- | :--- |
| **Next.js 14 / React** | Core web framework with App Router support and state management. |
| **WebSocket API** | Native browser `WebSocket` implementation for streaming live Kali logs. |
| **Vanilla CSS** | Custom Cyberpunk design system featuring Neo-Matrix glowing effects and CRT scanlines. |
| **Google Fonts** | "Plus Jakarta Sans" for UI and "JetBrains Mono" for code terminals. |

## 2. Backend Layer
| Technology | Usage |
| :--- | :--- |
| **FastAPI** | Modern, fast ASGI framework for Python, serving both HTTP and `ws://` endpoints. |
| **Uvicorn** | High-performance asynchronous production server. |
| **AsyncSSH** | Asynchronous SSH client library with iterative stream reading for live server output. |
| **Pydantic v2** | Strict data parsing and validation for resolving exact JSON LLM outputs. |
| **WebSockets** | Python `websockets` library for maintaining full-duplex persistent client connections. |

### 2.1 Execution & Streaming Architecture
- **Concurrent Scanning:** All 9 security tools execute in parallel using SSH connection multiplexing. 
- **Live Event Broadcasting:** The backend captures `stdout` line-by-line using asynchronous generators and pushes the payload directly to connected frontend clients via WebSockets.
- **Zero-Trust Input Validation:** Custom backend sanitizers parse target domains/IPs, stripping bash metacharacters and blocking private routing addresses (SSRF mitigation).

## 3. Data Storage
| Technology | Usage |
| :--- | :--- |
| **MongoDB Atlas** | Cloud-native NoSQL database to persist scan history, raw logs, and structured AI results. |
| **Motor** | Non-blocking, asynchronous driver for MongoDB. |
| **Certifi** | Provides Mozilla's CA Bundle to securely validate MongoDB TLS/SSL connections on Windows environments. |

## 4. Security Toolchain & AI
| Tool | Purpose | Status |
| :--- | :--- | :--- |
| **Nmap, HTTPX, Nuclei...** | The 9-suite Kali Linux intelligence gathering toolkit. | Active / Multiplexed |
| **NVIDIA NIM API** | Hosts the `meta/llama-3.1-405b-instruct` model for inference. | Active |
| **Autonomous Remediation** | Generates exact `bash`, `ufw`, or `docker` scripts to auto-patch discovered vulnerabilities. | Active |

## 5. Development & DevOps
| Technology | Usage |
| :--- | :--- |
| **Pip/Venv & NPM** | Backend and Frontend environments. |
| **VirtualBox** | Locally hosted Kali Linux virtualization. |
| **Powershell** | Local Windows development environment execution. |
