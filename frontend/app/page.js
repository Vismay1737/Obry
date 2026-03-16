'use client'

import { useState, useEffect, useRef } from 'react'

const API_BASE = 'http://localhost:8000/api'
const WS_BASE = 'ws://localhost:8000/ws'

export default function Dashboard() {
  const [target, setTarget] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [scanId, setScanId] = useState(null)
  const [scanResult, setScanResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [liveLogs, setLiveLogs] = useState([])
  
  const terminalRef = useRef(null)
  const wsRef = useRef(null)
  const pollIntervalRef = useRef(null)

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [liveLogs])

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
    setLiveLogs(['> Connection established. Synchronizing engines...'])

    try {
      const res = await fetch(`${API_BASE}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target.trim() })
      })
      
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || `Server error: ${res.status}`)
      }
      
      const newScanId = data._id || data.id
      setScanId(newScanId)

      // Initialize WebSocket
      if (wsRef.current) wsRef.current.close()
      const ws = new WebSocket(`${WS_BASE}/scan/${newScanId}`)
      wsRef.current = ws

      ws.onmessage = (event) => {
        try {
          const wsData = JSON.parse(event.data)
          const logText = wsData.log.trim()
          if (logText) {
            setLiveLogs(prev => [...prev, `[${wsData.tool}] > ${logText}`])
          }
        } catch (err) {}
      }

      // Initialize Polling
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = setInterval(async () => {
        try {
          const checkRes = await fetch(`${API_BASE}/scans/${newScanId}`)
          const scanData = await checkRes.json()
          
          if (scanData.status === 'completed' || scanData.status === 'failed') {
            clearInterval(pollIntervalRef.current)
            if (wsRef.current) wsRef.current.close()
            setIsScanning(false)
            setScanResult(scanData)
            
            if (scanData.status === 'failed') {
               setError('Scan failed: ' + (scanData.ai_analysis || scanData.error || 'Unknown Error'))
            }
          }
        } catch (e) {}
      }, 5000)

    } catch (err) {
      setError(`Failed to start scan: ${err.message}`)
      setIsScanning(false)
      setLiveLogs([])
    }
  }

  const handleCopyScript = (scriptText) => {
    navigator.clipboard.writeText(scriptText)
  }

  return (
    <div className="container">
      <div className="bg-blobs">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>

      <header className="header">
        <div className="ai-orb-container">
          <div className="ai-orb"></div>
        </div>
        <h1>OrbyTech Copilot</h1>
        {isScanning && (
          <div className="searching-pill" style={{ color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
            <span className="spinner-small" style={{ display: 'inline-block', width: '20px', height: '20px', border: '2px solid rgba(0,243,255,0.3)', borderTopColor: 'var(--accent-cyan)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
            <span>Orby AI is scanning {target}</span>
          </div>
        )}
        <form className="scanner-input-container" onSubmit={handleScan} style={{ maxWidth: '700px', width: '100%', margin: '40px auto 0', display: 'flex', gap: '12px', padding: '8px', background: 'rgba(255, 255, 255, 0.03)', backdropFilter: 'blur(10px)', borderRadius: '20px', border: '1px solid var(--glass-border)' }}>
          <input
            type="text"
            className="scanner-input"
            style={{ flex: 1, background: 'transparent', border: 'none', padding: '16px 24px', borderRadius: '12px', color: '#fff', fontSize: '1.1rem', outline: 'none' }}
            placeholder="Enter IP, Domain, or URL to scan..."
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            disabled={isScanning}
          />
          <button type="submit" className="glow-btn" disabled={isScanning || !target} style={{ background: '#fff', color: '#030305', border: 'none', padding: '0 32px', borderRadius: '14px', fontWeight: 700, cursor: isScanning ? 'not-allowed' : 'pointer' }}>
            {isScanning ? 'Scanning...' : 'Initiate Scan'}
          </button>
          <button type="button" className="glow-btn" 
            style={{ background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid var(--glass-border)', padding: '0 32px', borderRadius: '14px', fontWeight: 700, cursor: 'pointer' }}
            onClick={loadHistory} disabled={isScanning}>
             History
          </button>
        </form>
      </header>

      <main style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
        {error && (
          <div className="glass-panel" style={{ borderColor: 'var(--danger)', color: 'var(--danger)', padding: '20px', borderRadius: '16px', border: '1px solid var(--danger)', backgroundColor: 'rgba(255,42,85,0.1)' }}>
            ⚠️ {error}
          </div>
        )}

        {isScanning && !scanResult && (
          <div className="glass-panel" style={{ padding: '60px 40px', background: 'var(--glass-bg)', backdropFilter: 'blur(24px)', border: '1px solid var(--glass-border)', borderRadius: '32px' }}>
            <h2 className="typing-indicator" style={{ color: 'var(--accent-cyan)', marginBottom: '20px' }}>
              Neural Network analyzing asset footprint...
            </h2>
            <div 
              ref={terminalRef}
              className="terminal-mode" 
              style={{ 
                fontFamily: "'JetBrains Mono', monospace", background: 'rgba(0, 0, 0, 0.4)', padding: '32px', borderRadius: '24px', color: 'var(--success)', fontSize: '0.9rem', 
                height: '400px', overflowY: 'auto', border: '1px solid var(--glass-border)', textAlign: 'left' 
              }}>
              {liveLogs.map((log, idx) => (
                <p key={idx} style={{ margin: '4px 0', wordBreak: 'break-all' }}>{log}</p>
              ))}
            </div>
          </div>
        )}

        {scanResult && scanResult.status === 'completed' && (
          <div className="results-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
            <div className="glass-panel score-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px', padding: '40px', background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', borderRadius: '32px' }}>
              <h3 style={{ color: 'var(--text-muted)' }}>Security Score</h3>
              <div className="score-circle" style={{ width: '180px', height: '180px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '4rem', fontWeight: 700, border: '4px solid var(--accent-cyan)', boxShadow: '0 0 30px rgba(0, 243, 255, 0.2) inset, 0 0 30px rgba(0, 243, 255, 0.2)', textShadow: '0 0 10px var(--accent-cyan)' }}>
                {scanResult.security_score ?? '--'}
              </div>
              <div className="ai-analysis" style={{ fontSize: '1.1rem', lineHeight: 1.6, color: 'var(--text-muted)', marginTop: '20px' }}>
                <strong style={{ color: 'var(--accent-cyan)', display: 'block', marginBottom: '10px' }}>AI Summary:</strong>
                <p>{scanResult.ai_analysis}</p>
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '40px', background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', borderRadius: '32px' }}>
              <h3 style={{ marginBottom: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>Identified Vulnerabilities</h3>
              <div className="vuln-list">
                {!scanResult.vulnerabilities || scanResult.vulnerabilities.length === 0 ? (
                  <p style={{ color: 'var(--success)' }}>No vulnerabilities identified by AI.</p>
                ) : (
                  scanResult.vulnerabilities.map((vuln, idx) => {
                    const sevMap = { 'high': 'high', 'critical': 'high', 'medium': 'medium', 'low': 'low' };
                    const sClass = sevMap[vuln.severity?.toLowerCase()] || 'low';
                    const colors = { high: 'var(--danger)', medium: 'var(--warning)', low: 'var(--success)' };
                    const color = colors[sClass];

                    return (
                      <div key={idx} className={`vulnerability-card`} style={{ background: 'rgba(0, 0, 0, 0.4)', borderLeft: `4px solid ${color}`, padding: '16px', marginBottom: '16px', borderRadius: '0 8px 8px 0' }}>
                        <div className="vuln-title" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                          <h4 style={{ fontSize: '1.2rem', color: '#fff' }}>{vuln.title}</h4>
                          <span className={`badge badge-${sClass}`} style={{ padding: '4px 10px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', background: `${color}33`, color: color }}>
                            {vuln.severity}
                          </span>
                        </div>
                        <p className="vuln-desc" style={{ color: 'var(--text-muted)', marginBottom: '12px', fontSize: '0.95rem' }}>{vuln.description}</p>
                        <div className="vuln-rec" style={{ background: 'rgba(0, 243, 255, 0.05)', padding: '12px', borderRadius: '6px', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.9rem', color: 'var(--accent-cyan)' }}>
                          <strong style={{ color: '#fff' }}>Remediation:</strong> {vuln.recommendation}
                        </div>
                        
                        {vuln.remediation_script && vuln.remediation_script.trim() !== '' && (
                          <div style={{ marginTop: '12px', background: '#000', padding: '16px', borderRadius: '8px', border: '1px solid var(--glass-border)', position: 'relative' }}>
                            <span style={{ position: 'absolute', top: '8px', right: '12px', fontSize: '0.75rem', color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>Autonomous Fix</span>
                            <pre style={{ color: 'var(--success)', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.85rem', overflowX: 'auto', margin: 0 }}>
                              {vuln.remediation_script}
                            </pre>
                            <button 
                              onClick={(e) => {
                                handleCopyScript(vuln.remediation_script); 
                                e.target.innerText='Copied!'; 
                                setTimeout(()=>e.target.innerText='Copy Script', 2000)
                              }} 
                              style={{ marginTop: '12px', background: 'rgba(0,243,255,0.1)', border: '1px solid var(--accent-cyan)', color: 'var(--accent-cyan)', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 600 }}>
                              Copy Script
                            </button>
                          </div>
                        )}
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          </div>
        )}

        {/* History */}
        {showHistory && (
          <div className="glass-panel" style={{ padding: '40px', background: 'var(--glass-bg)', backdropFilter: 'blur(24px)', border: '1px solid var(--glass-border)', borderRadius: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--accent-cyan)' }}>Scan History</h2>
              <button onClick={() => setShowHistory(false)} style={{ background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid var(--glass-border)', padding: '8px 20px', borderRadius: '12px', cursor: 'pointer' }}>
                ✕ Close
              </button>
            </div>
            {history.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No scans yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {history.map((s, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 32px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)', borderRadius: '16px' }}>
                    <div>
                      <h4 style={{ color: 'var(--accent-cyan)', marginBottom: '8px', fontSize: '1.2rem' }}>{s.target}</h4>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{new Date(s.created_at).toLocaleString()} • <span style={{ color: s.status === 'completed' ? 'var(--success)' : 'var(--warning)' }}>{s.status.toUpperCase()}</span></p>
                    </div>
                    {s.status === 'completed' && (
                      <button onClick={() => { 
                          setScanResult(s); 
                          setTarget(s.target);
                          setScanId(s._id || s.id);
                          setIsScanning(false);
                          setShowHistory(false); 
                        }} 
                        style={{ background: '#fff', color: '#000', padding: '8px 24px', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', border: 'none' }}>
                        View Report
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {!isScanning && !scanResult && !showHistory && (
          <div className="glass-panel" style={{ textAlign: 'center', opacity: 0.6, padding: '100px 40px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <p style={{ fontSize: '1.2rem' }}>Enter a target above to begin a comprehensive AI security scan.</p>
          </div>
        )}
      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}} />
    </div>
  )
}
