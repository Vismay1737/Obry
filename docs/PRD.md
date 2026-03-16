# Product Requirements Document (PRD) - OrbyTech v1.0

## 1. Product Vision
OrbyTech aims to democratize enterprise-grade cybersecurity by providing an AI Copilot that not only orchestrates complex Kali Linux penetration testing tools but also autonomously writes the scripts required to patch the vulnerabilities it discovers.

## 2. Target Audience
- Security Enthusiasts / Hackathon Judges.
- DevSecOps Engineers looking to drastically reduce the time between vulnerability discovery and patching.
- System Administrators seeking a centralized, beautiful dashboard for security posturing.

## 3. Core Features (Implemented)

### 3.1 The Hackathon Core
- **Integrated Kali Scanner:** 9 fully integrated tools running securely over SSH (Nmap, WhatWeb, HTTPX, Subfinder, Amass, GAU, Nikto, Nuclei, Katana).
- **Cyberpunk Live Dashboard:** A Next.js frontend featuring WebSockets that stream the raw terminal output from Kali directly to the user's browser in real-time.
- **Autonomous Remediation:** Utilizing Llama 3.1 405b to read the logs and generate precise copy-and-paste scripts (Bash/UFW/Terraform) to fix discovered vulnerabilities immediately.

### 3.2 Security & Compliance
- **Zero-Trust Validation:** The platform protects itself from its users. Anti-Command Injection and Anti-SSRF routing modules guarantee that users cannot attack the backend server or the internal network.
- **TLS/SSL Datastores:** Safe storage of previous reports in MongoDB Atlas relying on `certifi` CA validation.

## 4. Out of Scope (For Post-Hackathon)
- **Automated Scheduling:** Running cron job scans automatically every week.
- **Click-to-Patch Action:** Allowing the dashboard to automatically SSH into the target web server and run the generated remediation script without human intervention.
- **Multi-tenant Authentication:** User logins to isolate scan histories.
