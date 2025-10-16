import React, { useState } from 'react';
import axios from 'axios';
import './BuildGraph.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface BuildResponse {
  status: string;
  message: string;
  next_steps: string[];
  estimated_time: string;
}

const BuildGraph: React.FC = () => {
  const [connectionString, setConnectionString] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<BuildResponse | null>(null);
  const [error, setError] = useState('');
  const [checking, setChecking] = useState(false);
  const [graphBuilt, setGraphBuilt] = useState(false);

  const handleBuild = async () => {
    if (!connectionString.trim()) {
      setError('Please enter a connection string');
      return;
    }

    setLoading(true);
    setError('');
    setResponse(null);
    setGraphBuilt(false);

    try {
      const res = await axios.post(`${API_BASE_URL}/build-graph`, {
        connection_string: connectionString,
        rebuild: false,
      });

      setResponse(res.data);
      // Start checking status
      checkStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start graph build');
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    setChecking(true);
    let attempts = 0;
    const maxAttempts = 100; // 5 minutes (100 * 3 seconds)
    
    const interval = setInterval(async () => {
      attempts++;
      
      try {
        const res = await axios.get(`${API_BASE_URL}/health`);
        if (res.data.graph_built) {
          setGraphBuilt(true);
          setChecking(false);
          clearInterval(interval);
        } else if (attempts >= maxAttempts) {
          // Timeout after max attempts
          setChecking(false);
          setError('Graph build timed out. Please check server logs.');
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Error checking status:', err);
        setChecking(false);
        setError('Failed to check build status. Please check if backend is running.');
        clearInterval(interval);
      }
    }, 3000);
  };

  return (
    <div className="build-graph">
      <div className="card">
        <h2>Build Knowledge Graph</h2>
        <p className="subtitle">
          Convert your PostgreSQL database into an intelligent knowledge graph
        </p>

        <div className="input-group">
          <label>PostgreSQL Connection String</label>
          <input
            type="text"
            placeholder="postgresql://user:password@host:port/database"
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            disabled={loading || checking}
          />
          <small>Example: postgresql://user:pass@localhost:5432/mydb</small>
        </div>

        <button
          className="build-button"
          onClick={handleBuild}
          disabled={loading || checking}
        >
          {loading ? 'Starting...' : checking ? 'Building...' : 'Build Graph'}
        </button>

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">×</span>
            <p>{error}</p>
          </div>
        )}

        {response && (
          <div className="alert alert-success">
            <span className="alert-icon">✓</span>
            <div>
              <p><strong>{response.message}</strong></p>
              <p className="meta">Estimated time: {response.estimated_time}</p>
            </div>
          </div>
        )}

        {response && (
          <div className="steps-card">
            <h3>Next Steps:</h3>
            <ol>
              {response.next_steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
          </div>
        )}

        {checking && (
          <div className="progress-card">
            <div className="loader"></div>
            <p>Building knowledge graph...</p>
            <small>This may take 30-60 seconds</small>
          </div>
        )}

        {graphBuilt && (
          <div className="alert alert-success">
            <span className="alert-icon">✓</span>
            <div>
              <p><strong>Graph Built Successfully!</strong></p>
              <p>You can now query your knowledge graph in the Chat tab</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BuildGraph;

