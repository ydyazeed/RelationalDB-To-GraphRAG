import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './Chat.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  reasoning?: string[];
  tools_used?: string[];
  sources?: any[];
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/chat`, {
        query: input,
        stream: false,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: res.data.response,
        reasoning: res.data.reasoning,
        tools_used: res.data.tools_used,
        sources: res.data.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${err.response?.data?.detail || 'Failed to get response'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const exampleQueries = [
    'How many records are in the database?',
    'Find items matching a specific criteria',
    'Show me details about a specific entity',
    'What relationships exist between entities?',
    'Display statistics about the data',
  ];

  return (
    <div className="chat-container">
      <div className="chat-card">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>Ask Anything About Your Data</h2>
            <p>Try these example queries:</p>
            <div className="example-queries">
              {exampleQueries.map((query, idx) => (
                <button
                  key={idx}
                  className="example-query"
                  onClick={() => setInput(query)}
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? 'U' : 'AI'}
              </div>
              <div className="message-content">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
                
                {msg.tools_used && msg.tools_used.length > 0 && (
                  <div className="message-meta">
                    <span className="tools-badge">
                      Tools: {msg.tools_used.join(', ')}
                    </span>
                  </div>
                )}

                {msg.reasoning && msg.reasoning.length > 0 && (
                  <details className="reasoning-details">
                    <summary>View Reasoning Chain</summary>
                    <div className="reasoning-content">
                      {msg.reasoning.map((step, i) => (
                        <div key={i} className="reasoning-step">
                          <span className="step-number">{i + 1}</span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                {msg.sources && msg.sources.length > 0 && (
                  <details className="sources-details">
                    <summary>View Sources</summary>
                    <div className="sources-content">
                      {msg.sources.map((source, i) => (
                        <div key={i} className="source-item">
                          <strong>{source.tool}</strong>
                          <pre>{source.content}</pre>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="message-avatar">AI</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <textarea
            placeholder="Ask a question about your knowledge graph..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            rows={2}
          />
          <button onClick={handleSend} disabled={loading || !input.trim()}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;

