'use client'

import { useState, useEffect } from 'react'

const API_BASE = 'http://127.0.0.1:8000/api'

const TOOLS = ['nmap', 'whatweb', 'subfinder', 'nikto']
const TOOL_LABELS = {
  nmap: '🔍 Nmap — Port Scanner',
  whatweb: '🌐 WhatWeb — Tech Fingerprint',
  subfinder: '📡 Subfinder — Subdomain Enum',
  nikto: '🛡️ Nikto — Web Vulnerability'
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

  // Poll for results when scan is running
  useEffect(() => {
    if (!scanId || !isScanning) return
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/scans/${scanId}`)
        const data = await res.json()
        if (data.status === 'completed' || data.status === 'failed') {
          setScanResult(data)
          setIsScanning(false)
          clearInterval(interval)
        }
      } catch (e) {}
    }, 2000)
    return () => clearInterval(interval)
  }, [scanId, isScanning])

  const loadHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/scans`)
      setHistory(await res.json())
      setShowHistory(true)
    } catch (e) {
      setError('Could not load scan history')
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
        <div className="ai-orb"></div>
        <h1>OrbyTech Copilot</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
          Kali Linux Security Scanner — Nmap · Nikto · WhatWeb · Subfinder
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

        {isScanning && (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '60px 20px' }}>
            <h2 className="typing-indicator" style={{ color: 'var(--accent-cyan)' }}>
              Running Security Tools on {target}
            </h2>
            <div className="terminal-mode" style={{ marginTop: '20px', textAlign: 'left' }}>
              <p>{'>'} Spawning nmap stealth port scan...</p>
              <p>{'>'} Fingerprinting web technologies with WhatWeb...</p>
              <p>{'>'} Enumerating subdomains with Subfinder...</p>
              <p>{'>'} Running Nikto web vulnerability scanner...</p>
            </div>
          </div>
        )}

        {!isScanning && scanResult && (
          <div className="glass-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ color: 'var(--accent-cyan)' }}>Scan Results: {scanResult.target}</h2>
              <span style={{
                padding: '4px 14px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600,
                background: scanResult.status === 'completed' ? 'rgba(0,255,136,0.15)' : 'rgba(255,77,109,0.15)',
                color: scanResult.status === 'completed' ? '#00ff88' : '#ff4d6d',
                border: `1px solid ${scanResult.status === 'completed' ? '#00ff88' : '#ff4d6d'}`
              }}>
                {scanResult.status.toUpperCase()}
              </span>
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
                    fontFamily: 'inherit'
                  }}>
                  {tool.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Raw output */}
            <div>
              <h3 style={{ color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                {TOOL_LABELS[activeTab]}
              </h3>
              <div className="terminal-mode" style={{ minHeight: '300px', whiteSpace: 'pre-wrap', wordBreak: 'break-all', fontSize: '0.82rem', lineHeight: '1.6' }}>
                {scanResult.raw_output?.[activeTab] || `No output for ${activeTab}.`}
              </div>
            </div>
          </div>
        )}

        {/* History */}
        {showHistory && !isScanning && !scanResult && (
          <div className="glass-panel">
            <h2 style={{ color: 'var(--accent-cyan)', marginBottom: '1.5rem' }}>Scan History</h2>
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
                    onClick={() => { setScanResult(s); setShowHistory(false) }}>
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
              <p>The Network Mapper is the gold standard for port scanning and network discovery. It identifies open services, OS fingerprints, and potential entry points.</p>
            </div>
            <div className="info-card">
              <h3>🛡️ Nikto</h3>
              <p>A comprehensive web server scanner that tests for over 6,700 potentially dangerous files and programs, outdated versions, and specific server misconfigurations.</p>
            </div>
            <div className="info-card">
              <h3>🌐 WhatWeb</h3>
              <p>Identifies content management systems (CMS), blogging platforms, statistic/analytics packages, JavaScript libraries, and web servers used by the target.</p>
            </div>
            <div className="info-card">
              <h3>📡 Subfinder</h3>
              <p>An advanced tool for subdomain discovery. It uses passive sources to map out the entire domain infrastructure, uncovering hidden assets.</p>
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
