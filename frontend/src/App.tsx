import React, { useState } from 'react';
import './App.css';
import BuildGraph from './components/BuildGraph';
import Chat from './components/Chat';

type Tab = 'build' | 'chat';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('build');

  return (
    <div className="App">
      <header className="App-header">
        <h1>RAG Knowledge Graph</h1>
        <p>AI-Powered Database to Graph Conversion</p>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'build' ? 'active' : ''}`}
          onClick={() => setActiveTab('build')}
        >
          Build Graph
        </button>
        <button
          className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          Chat
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'build' && <BuildGraph />}
        {activeTab === 'chat' && <Chat />}
      </div>

      <footer className="App-footer">
        <p>Powered by FAISS, Neo4j, and Gemini LLM</p>
      </footer>
    </div>
  );
}

export default App;
