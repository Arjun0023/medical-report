import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Check if API is running on mount
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const result = await axios.get('http://127.0.0.1:8002/test');
        setApiStatus(result.data);
      } catch (err) {
        setApiStatus({ status: 'API connection failed', error: err.message });
      }
    };
    
    checkApiStatus();

    // Check user preference for dark mode
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(prefersDark);
  }, []);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      console.log('Submitting file:', selectedFile.name, selectedFile.type, selectedFile.size);
      
      const result = await axios.post('http://127.0.0.1:8002/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Response received:', result);
      setResponse(result.data);
    } catch (err) {
      console.error('Error details:', err);
      
      let errorMessage = err.message || 'An error occurred';
      if (err.response && err.response.data) {
        if (typeof err.response.data === 'object') {
          errorMessage = JSON.stringify(err.response.data, null, 2);
        } else {
          errorMessage = err.response.data;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`app-container ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <div className="header">
        <h1>Medical Report Analyzer</h1>
        <button 
          onClick={toggleDarkMode} 
          className="theme-toggle"
          aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </div>
      
      {apiStatus && (
        <div className={`api-status ${apiStatus.status === 'API is running' ? 'success' : 'error'}`}>
          <h3>API Status</h3>
          <div className="status-content">
            {apiStatus.status === 'API is running' ? 
              '✅ Connected successfully' : 
              `❌ Connection failed: ${apiStatus.error}`
            }
          </div>
        </div>
      )}
      
      <div className="upload-section">
        <form onSubmit={handleSubmit}>
          <div className="file-input-container">
            <label htmlFor="file-upload" className="file-label">
              {selectedFile ? selectedFile.name : 'Choose PDF file'}
              <span className="file-size">
                {selectedFile && `(${Math.round(selectedFile.size / 1024)} KB)`}
              </span>
            </label>
            <input 
              id="file-upload"
              type="file" 
              accept=".pdf" 
              onChange={handleFileChange} 
              className="file-input"
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading || !selectedFile} 
            className={`submit-button ${loading || !selectedFile ? 'disabled' : ''}`}
          >
            {loading ? 'Analyzing...' : 'Analyze Report'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Processing your medical report...</p>
          <p className="loading-subtext">This may take a minute depending on the report size.</p>
        </div>
      )}

      {error && (
        <div className="error-container">
          <h3>Error</h3>
          <pre className="error-message">{error}</pre>
        </div>
      )}

      {response && (
        <div className="result-container">
          <h2>Analysis Result</h2>
          <div className="report-content">
            {response.report}
          </div>
        </div>
      )}

      <style jsx>{`
        :root {
          --light-bg: #f9fafb;
          --light-text: #1f2937;
          --light-accent: #3b82f6;
          --light-border: #e5e7eb;
          --light-hover: #dbeafe;
          --light-card: #ffffff;
          --light-error-bg: #fee2e2;
          --light-error-text: #b91c1c;
          --light-success-bg: #d1fae5;
          --light-success-text: #065f46;
          
          --dark-bg: #111827;
          --dark-text: #f3f4f6;
          --dark-accent: #60a5fa;
          --dark-border: #374151;
          --dark-hover: #1e3a8a;
          --dark-card: #1f2937;
          --dark-error-bg: #7f1d1d;
          --dark-error-text: #fecaca;
          --dark-success-bg: #064e3b;
          --dark-success-text: #a7f3d0;
        }
        
        * {
          box-sizing: border-box;
          transition: background-color 0.3s, color 0.3s;
        }
        
        .app-container {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
          max-width: 900px;
          margin: 0 auto;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .light-mode {
          background-color: var(--light-card);
          color: var(--light-text);
        }
        
        .dark-mode {
          background-color: var(--dark-card);
          color: var(--dark-text);
        }
        
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid;
          border-color: inherit;
        }
        
        .header h1 {
          font-size: 1.8rem;
          margin: 0;
        }
        
        .theme-toggle {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .light-mode .theme-toggle {
          background-color: var(--light-hover);
        }
        
        .dark-mode .theme-toggle {
          background-color: var(--dark-hover);
        }
        
        .api-status {
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }
        
        .light-mode .api-status.success {
          background-color: var(--light-success-bg);
          color: var(--light-success-text);
        }
        
        .light-mode .api-status.error {
          background-color: var(--light-error-bg);
          color: var(--light-error-text);
        }
        
        .dark-mode .api-status.success {
          background-color: var(--dark-success-bg);
          color: var(--dark-success-text);
        }
        
        .dark-mode .api-status.error {
          background-color: var(--dark-error-bg);
          color: var(--dark-error-text);
        }
        
        .api-status h3 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1.2rem;
        }
        
        .status-content {
          display: flex;
          align-items: center;
          font-size: 0.95rem;
        }
        
        .upload-section {
          margin-bottom: 2rem;
        }
        
        .file-input-container {
          margin-bottom: 1rem;
        }
        
        .file-label {
          display: block;
          padding: 1rem;
          border: 2px dashed;
          border-radius: 8px;
          cursor: pointer;
          text-align: center;
          font-weight: 500;
          margin-bottom: 1rem;
        }
        
        .light-mode .file-label {
          border-color: var(--light-border);
          background-color: var(--light-bg);
        }
        
        .dark-mode .file-label {
          border-color: var(--dark-border);
          background-color: var(--dark-bg);
        }
        
        .file-size {
          margin-left: 0.5rem;
          font-size: 0.85rem;
          opacity: 0.8;
        }
        
        .file-input {
          width: 0.1px;
          height: 0.1px;
          opacity: 0;
          overflow: hidden;
          position: absolute;
          z-index: -1;
        }
        
        .submit-button {
          display: block;
          width: 100%;
          padding: 0.75rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .light-mode .submit-button {
          background-color: var(--light-accent);
          color: white;
        }
        
        .dark-mode .submit-button {
          background-color: var(--dark-accent);
          color: white;
        }
        
        .submit-button.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .loading-container {
          text-align: center;
          padding: 2rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }
        
        .light-mode .loading-container {
          background-color: var(--light-bg);
        }
        
        .dark-mode .loading-container {
          background-color: var(--dark-bg);
        }
        
        .loading-spinner {
          border: 4px solid rgba(0, 0, 0, 0.1);
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border-left-color: var(--light-accent);
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }
        
        .dark-mode .loading-spinner {
          border: 4px solid rgba(255, 255, 255, 0.1);
          border-left-color: var(--dark-accent);
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .loading-subtext {
          font-size: 0.85rem;
          opacity: 0.7;
        }
        
        .error-container {
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 2rem;
          overflow: auto;
        }
        
        .light-mode .error-container {
          background-color: var(--light-error-bg);
          color: var(--light-error-text);
        }
        
        .dark-mode .error-container {
          background-color: var(--dark-error-bg);
          color: var(--dark-error-text);
        }
        
        .error-container h3 {
          margin-top: 0;
        }
        
        .error-message {
          white-space: pre-wrap;
          word-break: break-word;
          font-family: monospace;
          font-size: 0.9rem;
          background: rgba(0, 0, 0, 0.05);
          padding: 1rem;
          border-radius: 4px;
        }
        
        .dark-mode .error-message {
          background: rgba(255, 255, 255, 0.05);
        }
        
        .result-container {
          padding: 1.5rem;
          border-radius: 8px;
        }
        
        .light-mode .result-container {
          background-color: var(--light-bg);
        }
        
        .dark-mode .result-container {
          background-color: var(--dark-bg);
        }
        
        .result-container h2 {
          margin-top: 0;
          margin-bottom: 1.5rem;
          font-size: 1.5rem;
        }
        
        .report-content {
          white-space: pre-wrap;
          word-break: break-word;
          line-height: 1.6;
          padding: 1.5rem;
          border-radius: 8px;
        }
        
        .light-mode .report-content {
          background-color: white;
          border: 1px solid var(--light-border);
        }
        
        .dark-mode .report-content {
          background-color: var(--dark-card);
          border: 1px solid var(--dark-border);
        }
        
        @media (max-width: 768px) {
          .app-container {
            padding: 1rem;
            margin: 0;
            border-radius: 0;
            box-shadow: none;
          }
          
          .header h1 {
            font-size: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
}

export default App;