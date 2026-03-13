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
- **Two-Stage Scanning:** Implemented to improve User Experience. Fast tools (Nmap/WhatWeb) execute and report results first, while slower tools (Subfinder/Nikto) run in the background.
- **Extended Timeouts:** Execution limits increased to **600 seconds (10 minutes)** to accommodate deep vulnerability scanning.

## 3. Data Storage
| Technology | Usage |
| :--- | :--- |
| **MongoDB Atlas** | Cloud-native NoSQL database for persistent storage of scan history and raw outputs. |
| **Motor** | Non-blocking, asynchronous driver for MongoDB in Python. |

## 4. Security Toolchain (Kali Linux)
| Tool | Purpose | Status |
| :--- | :--- | :--- |
| **Nmap** | Port scanning and service discovery. | Stage 1 (Fast) |
| **WhatWeb** | Web technology and CMS fingerprinting. | Stage 1 (Fast) |
| **Subfinder** | Passive subdomain enumeration. | Stage 2 (Deep) |
| **Nikto** | Web server vulnerability scanning. | Stage 2 (Deep) |

## 5. Development & DevOps
| Technology | Usage |
| :--- | :--- |
| **Pip/Venv** | Python dependency and environment management. |
| **NPM** | Node.js package management. |
| **Git/GitHub** | Version control and collaboration. |
| **VirtualBox** | Locally hosted Kali Linux virtualization. |
