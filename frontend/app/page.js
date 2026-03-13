'use client'

import { useState, useEffect } from 'react'

const API_BASE = '/api'

const TOOLS = ['nmap', 'whatweb', 'httpx', 'nuclei', 'amass', 'subfinder', 'katana', 'gau', 'nikto', 'ai']
const TOOL_LABELS = {
  nmap: '🔍 Nmap — Port Scanner',
  whatweb: '🌐 WhatWeb — Tech Fingerprint',
  httpx: '🚀 HTTPX — Live Domains/Tech',
  nuclei: '🎯 Nuclei — Vulnerability Scan',
  amass: '🏗️ Amass — Passive Enum',
  subfinder: '📡 Subfinder — Subdomain Enum',
  katana: '🗡️ Katana — Web Crawler',
  gau: '🧹 GAU — Hidden Endpoints',
  nikto: '🛡️ Nikto — Web Scraper',
  ai: '🤖 AI Copilot — Security Analysis'
}

export default function Dashboard() {
  const [target, setTarget] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [scanId, setScanId] = useState(null)
  const [scanResult, setScanResult] = useState(null)
  const [activeTab, setActiveTab] = useState('nmap')
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [user, setUser] = useState(true) // Default to true to allow access without login

  // Poll for results when scan is running
  useEffect(() => {
    if (!scanId || !isScanning || showHistory) return
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/scans/${scanId}`)
        const data = await res.json()
        
        // Only update if we are not currently looking at history
        if (!showHistory) {
          setScanResult(data)
        }
        
        if (data.status === 'completed' || data.status === 'failed') {
          setIsScanning(false)
          clearInterval(interval)
        }
      } catch (e) {}
    }, 2000)
    return () => clearInterval(interval)
  }, [scanId, isScanning, showHistory])

  const loadHistory = async () => {
    try {
      setShowHistory(true)
      setScanResult(null)
      setError(null)
      const res = await fetch(`${API_BASE}/scans`)
      if (!res.ok) throw new Error('Failed to fetch history')
      const data = await res.json()
      setHistory(data)
    } catch (e) {
      console.error(e)
      setError('Could not load scan history. Ensure backend is running.')
    }
  }

  const handleScan = async (e) => {
    e.preventDefault()
    if (!target) return
    setIsScanning(true)
    setError(null)
    setScanResult(null)
    setScanId(null)
    setShowHistory(false)

    try {
      const res = await fetch(`${API_BASE}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target })
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setScanId(data._id || data.id)
    } catch (err) {
      setError(`Failed to start scan: ${err.message}`)
      setIsScanning(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <div className="ai-orb-container">
          <div className="ai-orb"></div>
        </div>
        <h1>OrbyTech Copilot</h1>
        {isScanning && (
          <div className="searching-pill">
            <span className="spinner-small"></span>
            <span>Orby AI is scanning {target}</span>
            <span className="pulse-dot"></span>
          </div>
        )}
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '1rem', marginBottom: '1rem' }}>
          Kali Linux Pro Toolkit — Nmap · Nuclei · HTTPX · Amass · Katana · GAU · Nikto
        </p>
        <form className="scanner-input-container" onSubmit={handleScan}>
          <input
            type="text"
            className="scanner-input"
            placeholder="Enter IP, Domain, or URL to scan..."
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            disabled={isScanning}
          />
          <button type="submit" className="glow-btn" disabled={isScanning || !target}>
            {isScanning ? 'Scanning...' : 'Initiate'}
          </button>
          <button type="button" className="glow-btn" style={{ background: 'transparent', border: '1px solid var(--card-border)', color: 'var(--text-main)' }}
            onClick={loadHistory} disabled={isScanning}>
            History
          </button>
        </form>
      </header>

      <main>
        {error && (
          <div className="glass-panel" style={{ borderColor: '#ff4d6d', color: '#ff4d6d' }}>
            ⚠️ {error}
          </div>
        )}

        {isScanning && !scanResult?.raw_output && (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '60px 20px' }}>
            <h2 className="typing-indicator" style={{ color: 'var(--accent-cyan)' }}>
              Preparing Security Tools for {target}
            </h2>
            <div className="terminal-mode" style={{ marginTop: '20px', textAlign: 'left' }}>
              <p>{'>'} Spawning nmap stealth port scan...</p>
              <p>{'>'} Fingerprinting tech with WhatWeb & HTTPX...</p>
              <p>{'>'} Enumerating subdomains with Amass & Subfinder...</p>
              <p>{'>'} Crawling paths with Katana & discovering endpoints with GAU...</p>
              <p>{'>'} Preparing deep vulnerability scans with Nuclei & Nikto...</p>
            </div>
          </div>
        )}

        {scanResult && (
          <div className="glass-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <h2 style={{ color: 'var(--accent-cyan)' }}>Scan Results: {scanResult.target}</h2>
                {isScanning && scanResult.raw_output?.nmap && !scanResult.raw_output?.nikto && (
                  <p style={{ color: '#ffcc00', fontSize: '0.85rem' }}>
                    🚀 Stage 1 Complete. Initiating Deep Scan (Nikto & Subfinder)...
                  </p>
                )}
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                {isScanning && (
                  <span style={{
                    padding: '4px 14px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600,
                    background: 'rgba(0,195,255,0.15)', color: 'var(--accent-cyan)', border: '1px solid var(--accent-cyan)'
                  }}>
                    LIVE UPDATING...
                  </span>
                )}
                <span style={{
                  padding: '4px 14px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600,
                  background: scanResult.status === 'completed' ? 'rgba(0,255,136,0.15)' : 
                              scanResult.status === 'failed' ? 'rgba(255,77,109,0.15)' : 'rgba(255,255,255,0.1)',
                  color: scanResult.status === 'completed' ? '#00ff88' : 
                         scanResult.status === 'failed' ? '#ff4d6d' : 'var(--text-muted)',
                  border: `1px solid ${scanResult.status === 'completed' ? '#00ff88' : 
                                       scanResult.status === 'failed' ? '#ff4d6d' : 'var(--text-muted)'}`
                }}>
                  {scanResult.status.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Tool tabs */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
              {TOOLS.map(tool => (
                <button key={tool} onClick={() => setActiveTab(tool)}
                  style={{
                    padding: '8px 18px', borderRadius: '8px', border: 'none', cursor: 'pointer',
                    background: activeTab === tool ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.05)',
                    color: activeTab === tool ? '#000' : 'var(--text-muted)',
                    fontWeight: activeTab === tool ? 700 : 400,
                    fontFamily: 'inherit',
                    position: 'relative',
                    border: tool === 'ai' ? '1px solid rgba(0, 243, 255, 0.3)' : 'none'
                  }}>
                  {tool.toUpperCase()}
                  {isScanning && !scanResult.raw_output?.[tool] && tool !== 'ai' && (
                    <span style={{ 
                      width: '6px', height: '6px', background: '#ffcc00', 
                      borderRadius: '50%', position: 'absolute', top: '5px', right: '5px',
                      boxShadow: '0 0 5px #ffcc00'
                    }}></span>
                  )}
                  {isScanning && tool === 'ai' && !scanResult.ai_analysis && (
                    <span className="spinner-small" style={{ position: 'absolute', top: '5px', right: '5px' }}></span>
                  )}
                </button>
              ))}
            </div>

            {/* Content display */}
            <div>
              <h3 style={{ color: 'var(--text-muted)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                {TOOL_LABELS[activeTab]}
                {activeTab === 'ai' && isScanning && <span className="spinner-small"></span>}
              </h3>
              <div className="terminal-mode" style={{ 
                minHeight: '400px', 
                whiteSpace: 'pre-wrap', 
                wordBreak: 'break-all', 
                fontSize: activeTab === 'ai' ? '1rem' : '0.85rem', 
                lineHeight: '1.8',
                color: activeTab === 'ai' ? '#fff' : 'var(--success)',
                background: activeTab === 'ai' ? 'rgba(0,0,0,0.85)' : '#000',
                border: activeTab === 'ai' ? '1px solid var(--accent-purple)' : '1px solid rgba(0, 255, 136, 0.2)',
                padding: '30px',
                boxShadow: activeTab === 'ai' ? '0 0 40px rgba(157, 0, 255, 0.1)' : 'none'
              }}>
                {activeTab === 'ai' 
                  ? (scanResult.ai_analysis || (isScanning ? "Orby AI is currently synthesizing tool outputs into a security report...\n\n> Parsing Nmap service versions\n> Evaluating Nikto vulnerability surface\n> Correlating WhatWeb tech stack..." : "Awaiting final analysis results."))
                  : (scanResult.raw_output?.[activeTab] || (isScanning ? `[SYSTEM] Awaiting output from ${activeTab}...\n[SYSTEM] Establishing remote connection...` : `No output for ${activeTab}.`))
                }
              </div>
            </div>
          </div>
        )}

        {/* History */}
        {showHistory && (
          <div className="glass-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ color: 'var(--accent-cyan)' }}>Scan History</h2>
              <button className="glow-btn" style={{ background: 'rgba(255,255,255,0.05)', fontSize: '0.8rem' }}
                onClick={() => setShowHistory(false)}>
                ✕ Close
              </button>
            </div>
            {history.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No scans yet.</p>
            ) : (
              history.map((s, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 0', borderBottom: '1px solid var(--card-border)'
                }}>
                  <span style={{ color: 'var(--accent-cyan)' }}>{s.target}</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {new Date(s.created_at).toLocaleString()} — {s.status}
                  </span>
                  <button className="glow-btn" style={{ padding: '4px 12px', fontSize: '0.8rem' }}
                    onClick={() => { 
                      setScanResult(s); 
                      setTarget(s.target);
                      setScanId(s._id || s.id);
                      setIsScanning(s.status === 'running');
                      setShowHistory(false); 
                    }}>
                    View
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {!isScanning && !scanResult && !showHistory && (
          <div className="glass-panel" style={{ textAlign: 'center', opacity: 0.5 }}>
            <p>Enter a target above to begin a comprehensive security scan.</p>
          </div>
        )}

        {/* Educational Sections */}
        <div className="info-section">
          <h2>🛡️ Security Toolkit</h2>
          <div className="info-grid">
            <div className="info-card">
              <h3>🔍 Nmap</h3>
              <p>Network Mapper identifies open services and potential entry points.</p>
            </div>
            <div className="info-card">
              <h3>🎯 Nuclei</h3>
              <p>Templated vulnerability scanner for high-confidence security findings across entire infrastructures.</p>
            </div>
            <div className="info-card">
              <h3>🚀 HTTPX</h3>
              <p>High-performance tool for probing live domains, status codes, and technology stacks at scale.</p>
            </div>
            <div className="info-card">
              <h3>🏗️ Amass</h3>
              <p>Active and passive domain enumeration to map out an organization's entire external attack surface.</p>
            </div>
            <div className="info-card">
              <h3>🗡️ Katana</h3>
              <p>Next-generation crawling framework for automated URL discovery and web resource spidering.</p>
            </div>
            <div className="info-card">
              <h3>🧹 GAU</h3>
              <p>Fetches known URLs from web archives to uncover long-forgotten or hidden endpoints.</p>
            </div>
            <div className="info-card">
              <h3>🛡️ Nikto</h3>
              <p>Tests for over 6,700 dangerous files, outdated versions, and server misconfigurations.</p>
            </div>
            <div className="info-card">
              <h3>📡 Subfinder</h3>
              <p>Fast passive subdomain discovery tool using multiple data sources.</p>
            </div>
          </div>
        </div>

        <div className="info-section">
          <h2>💻 The Power of Kali Linux</h2>
          <div className="glass-panel">
            <p style={{ color: 'var(--text-muted)', lineHeight: '1.8' }}>
              Kali Linux is a Debian-derived Linux distribution designed for digital forensics and penetration testing. 
              Our platform leverages the power of Kali's enterprise-grade security tools to provide you with raw, 
              unfiltered security data. By running these tools on an isolated Kali instance, we ensure that deep 
              scanning is performed safely and professionally.
            </p>
          </div>
        </div>

        <div className="info-section">
          <h2>⚡ How It Works</h2>
          <div className="info-grid">
            <div className="info-card">
              <div className="tech-step">
                <div className="step-num">1</div>
                <div className="step-content">
                  <h4>Initiate Scan</h4>
                  <p>You provide a target URL or IP. Our React frontend sends this to the FastAPI backend immediately.</p>
                </div>
              </div>
              <div className="tech-step">
                <div className="step-num">2</div>
                <div className="step-content">
                  <h4>Secure SSH Tunnel</h4>
                  <p>The backend establishes an encrypted SSH connection to a remote Kali Linux machine.</p>
                </div>
              </div>
              <div className="tech-step">
                <div className="step-num">3</div>
                <div className="step-content">
                  <h4>Distributed Scanning</h4>
                  <p>All security tools (Nmap, Nikto, etc.) run concurrently on the Kali machine to maximize speed.</p>
                </div>
              </div>
              <div className="tech-step">
                <div className="step-num">4</div>
                <div className="step-content">
                  <h4>Live Streaming</h4>
                  <p>Raw outputs are piped back through the tunnel, stored in MongoDB, and streamed to your dashboard in real-time.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
