'use client'

import { useState } from 'react'

export default function Dashboard() {
  const [target, setTarget] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [scanResult, setScanResult] = useState(null)
  const [error, setError] = useState(null)

  const handleScan = async (e) => {
    e.preventDefault()
    if (!target) return
    setIsScanning(true)
    setError(null)
    setScanResult(null)

    // Simulate API call delay for UI testing purposes if backend isn't connected
    setTimeout(() => {
      setScanResult({
        security_score: 75,
        ai_analysis: "OrbyTech AI has analyzed the target. The overall security posture is adequate, but several ports are unnecessarily exposed and the web server is broadcasting an outdated version signature. Resolving these issues will significantly harden the infrastructure.",
        vulnerabilities: [
          {
            title: "Outdated Server Header revealed",
            severity: "Low",
            description: "The HTTP response headers reveal the exact server version (e.g. Apache/2.4.41). This helps attackers find specific exploits.",
            recommendation: "Configure the web server to mask or disable the 'Server' header signature."
          },
          {
            title: "Exposed Admin Interface (Port 8080)",
            severity: "High",
            description: "An administrative panel is exposed on a non-standard port without WAF protection.",
            recommendation: "Restrict access to port 8080 using a firewall or IP whitelist. Require VPN access."
          }
        ]
      })
      setIsScanning(false)
    }, 3000)
  }

  const getSeverityClass = (severity) => {
    switch(severity.toLowerCase()) {
      case 'high': case 'critical': return 'high'
      case 'medium': return 'medium'
      case 'low': default: return 'low'
    }
  }

  return (
    <div className="container">
      {/* Header section with AI Orb */}
      <header className="header">
        <div className="ai-orb"></div>
        <h1>OrbyTech Copilot</h1>
        
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
        </form>
      </header>

      {/* Main Content Area */}
      <main>
        {isScanning && (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '60px 20px' }}>
            <h2 className="typing-indicator" style={{ color: 'var(--accent-cyan)' }}>
              Neural Network analyzing asset footprint
            </h2>
            <div className="terminal-mode" style={{ marginTop: '20px', textAlign: 'left' }}>
              <p>{'>'} Initializing Nmap stealth scan...</p>
              <p>{'>'} Spawning Nikto web vulnerability scanner...</p>
              <p>{'>'} Awaiting payload responses...</p>
            </div>
          </div>
        )}

        {!isScanning && scanResult && (
          <div className="results-grid">
            {/* Score & Summary Panel */}
            <div className="glass-panel score-panel">
              <h3 style={{ color: 'var(--text-muted)' }}>Security Score</h3>
              <div className="score-circle">
                {scanResult.security_score}
              </div>
              <div className="ai-analysis">
                <strong style={{ color: 'var(--accent-cyan)' }}>AI Summary:</strong>
                <p style={{ marginTop: '10px' }}>{scanResult.ai_analysis}</p>
              </div>
            </div>

            {/* Vulnerabilities Panel */}
            <div className="glass-panel">
              <h3 style={{ marginBottom: '20px', borderBottom: '1px solid var(--card-border)', paddingBottom: '10px' }}>
                Identified Vulnerabilities
              </h3>
              
              <div className="vuln-list">
                {scanResult.vulnerabilities.map((vuln, idx) => {
                  const sClass = getSeverityClass(vuln.severity)
                  return (
                    <div key={idx} className={`vulnerability-card vuln-${sClass}`}>
                      <div className="vuln-title">
                        <h4>{vuln.title}</h4>
                        <span className={`badge badge-${sClass}`}>{vuln.severity}</span>
                      </div>
                      <p className="vuln-desc">{vuln.description}</p>
                      <div className="vuln-rec">
                        <strong>Remediation:</strong> {vuln.recommendation}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* Empty State placeholder */}
        {!isScanning && !scanResult && (
           <div className="glass-panel" style={{ textAlign: 'center', opacity: 0.5 }}>
             <p>Awaiting target specification for comprehensive security analysis.</p>
           </div>
        )}
      </main>
    </div>
  )
}
