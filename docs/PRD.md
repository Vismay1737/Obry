# Product Requirements Document (PRD) - OrbyTech

## 1. Project Overview
**OrbyTech** is a cybersecurity dashboard designed to simplify the process of running industry-standard security scans. It provides a centralized, modern interface for executing Kali Linux tools and viewing their raw outputs in real-time.

## 2. Problem Statement
Running security tools manually via the terminal can be cumbersome, especially when orchestrating multiple tools (Nmap, Nikto, etc.) across different environments. Users need a way to trigger these scans from a web interface and view consolidated results without managing multiple terminal windows.

## 3. Goals & Objectives
- **Centralized Dashboard:** A single UI to trigger scans across multiple security tools concurrently.
- **Remote Execution:** Leverage an isolated Kali Linux environment for heavy-duty scanning via secure SSH tunneling.
- **Historical Tracking:** Store and retrieve past scan results for comparison and auditing.
- **Educational Value:** Provide context on what each tool does to help users understand the scanning process.

## 4. User Personas
- **Security Enthusiasts:** Individuals learning penetration testing.
- **System Administrators:** Users wanting a quick health check of their network perimeter.
- **Developers:** Building secure applications who want to verify their public-facing services.

## 5. Functional Requirements
- **Target Input:** Support for Domain names and IP addresses.
- **Concurrent Scanning:** Execute Nmap, Nikto, WhatWeb, and Subfinder simultaneously.
- **Real-time Status:** Show a "running" state and polling mechanism to update the UI when tools finish.
- **Tabbed Results:** Clean separation of raw terminal outputs for each tool.
- **Scan History:** Persistent storage of results in a NoSQL database.

## 6. Non-Functional Requirements
- **Security:** Use encrypted SSH tunnels for remote payouts.
- **Aesthetics:** "Hacker-style" dark mode UI with modern animations (Glassmorphism).
- **Scalability:** Ability to separate the scanning engine (Kali) from the application server.

## 7. Future Scope
- **AI Analysis:** Re-integration of AI for vulnerability explanation once API quotas are resolved.
- **PDF Reports:** Downloadable summaries of scan results.
- **Custom Toolbars:** Ability for users to add their own custom bash commands to the scan suite.
