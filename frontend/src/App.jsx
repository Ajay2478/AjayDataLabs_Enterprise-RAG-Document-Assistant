import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Upload, Loader2, Bot, User, FileText, Trash2, Globe, FileOutput, Clock, History, Volume2, StopCircle, Plus, Copy, Check } from 'lucide-react';
import './App.css';

// 🚀 ENTERPRISE FIX: Dynamic URL
// This allows Vercel to inject the NEW backend link automatically.
// If running locally, it defaults to localhost.
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]); 
  
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [thinking, setThinking] = useState(false);
  
  // --- AUDIO & COPY STATE ---
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  // --- 1. LOAD HISTORY ---
  useEffect(() => {
    fetchHistory();
    fetchDocuments();
    return () => window.speechSynthesis.cancel();
  }, []);

  const fetchHistory = async () => {
    try {
        const res = await axios.get(`${API_BASE_URL}/history`);
        if (res.data.history.length > 0) {
            setMessages(res.data.history);
        } else {
            setMessages([{ type: 'ai', text: "Hello! Upload a PDF to start. I recall our past chats!" }]);
        }
    } catch (e) { console.error("History Error", e); }
  };

  const fetchDocuments = async () => {
    try {
        const res = await axios.get(`${API_BASE_URL}/documents`);
        setDocuments(res.data.documents);
    } catch (e) { console.error("Docs Error", e); }
  };

  // --- 2. AUDIO LOGIC ---
  const speakText = (text) => {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US'; 
        utterance.rate = 1; 
        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utterance);
    } else {
        alert("Sorry, your browser doesn't support Text-to-Speech!");
    }
  };

  const stopSpeaking = () => {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
  };

  // --- 3. COPY LOGIC ---
  const handleCopy = (text, index) => {
      navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
  };

  // --- 4. RESET & NEW UPLOAD ---
  const handleClearHistory = async () => {
    if(!window.confirm("Are you sure? This deletes ALL chat history and saved files.")) return;
    stopSpeaking();
    try {
        await axios.delete(`${API_BASE_URL}/clear`);
        setFile(null);
        setPdfUrl(null);
        setMessages([{ type: 'ai', text: "History cleared. Ready for a new document!" }]);
        fetchDocuments(); 
    } catch(e) { alert("Error clearing history"); }
  };

  const handleNewUpload = () => {
      stopSpeaking();
      setPdfUrl(null); 
      setFile(null);
      setMessages(prev => [...prev, { type: 'ai', text: "--- Ready for new file ---" }]);
  };

  // --- 5. UPLOAD ---
  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      await handleUpload(selectedFile);
    }
  };

  const handleUpload = async (selectedFile) => {
    setUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      const url = `${API_BASE_URL}/static/${selectedFile.name}`;
      setPdfUrl(url);
      setMessages(prev => [...prev, { type: 'ai', text: `I've read ${selectedFile.name}. Ask me anything!` }]);
      fetchDocuments();
    } catch (error) {
      console.error("Upload Error:", error);
      alert("Error uploading file.");
    } finally {
      setUploading(false);
    }
  };

  const loadOldFile = (filename) => {
      setPdfUrl(`${API_BASE_URL}/static/${filename}`);
      setMessages(prev => [...prev, { type: 'ai', text: `Loaded ${filename} from history.` }]);
  };

  // --- 6. CHAT ---
  const handleAsk = async (customQuestion = null) => {
    const textToSend = customQuestion || question;
    if (!textToSend.trim()) return;

    if (!customQuestion) {
        setMessages(prev => [...prev, { type: 'user', text: textToSend }]);
    }
    
    setQuestion("");
    setThinking(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/query`, { question: textToSend });
      setMessages(prev => [...prev, { type: 'ai', text: res.data.answer }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'ai', text: "Error: Could not get answer." }]);
    } finally {
      setThinking(false);
    }
  };

  const handleSummary = async () => {
    setMessages(prev => [...prev, { type: 'user', text: "✨ Generating Document Summary..." }]);
    setThinking(true);
    try {
        const res = await axios.post(`${API_BASE_URL}/summarize`);
        setMessages(prev => [...prev, { type: 'ai', text: res.data.summary }]);
    } catch (error) {
        setMessages(prev => [...prev, { type: 'ai', text: "Error generating summary." }]);
    } finally {
        setThinking(false);
    }
  };

  return (
    <div className="app-container">
      
      {/* LEFT PANEL: PDF Viewer & History */}
      <div className="left-panel">
        
        {/* Header */}
        <div className="header-bar">
          <h1 className="header-title">
            <FileText size={20} /> Document Viewer
          </h1>
          <div className="toolbar-actions">
            <button onClick={handleNewUpload} className="btn btn-blue" title="Upload a different file">
                <Plus size={16} /> New
            </button>
            
            {pdfUrl && (
                <button onClick={handleSummary} disabled={thinking} className="btn btn-green">
                    <FileOutput size={16} /> Summary
                </button>
            )}
            
            <button onClick={handleClearHistory} className="btn btn-red" title="Delete all history">
                <Trash2 size={16} /> Clear
            </button>
          </div>
        </div>

        {/* PDF Content */}
        <div className="viewer-content">
          {pdfUrl ? (
            <iframe src={pdfUrl} className="pdf-frame" title="PDF Viewer" />
          ) : (
            <div className="upload-container">
                {/* Upload Box */}
                <label className="upload-box">
                    <input type="file" onChange={handleFileChange} style={{display: 'none'}} accept=".pdf" />
                    <div className="upload-content">
                      <div className="upload-icon-wrapper">
                        {uploading ? <Loader2 className="spin text-blue-400" /> : <Upload className="text-blue-400" />}
                      </div>
                      <h3 className="font-semibold text-gray-200">Upload New PDF</h3>
                    </div>
                </label>

                {/* Saved Documents */}
                {documents.length > 0 && (
                    <div className="history-section">
                        <br/>
                        <h3 className="history-title">
                            <History size={16} /> Recently Uploaded
                        </h3>
                        <div className="history-list">
                            {documents.map((doc, i) => (
                                <div key={i} onClick={() => loadOldFile(doc.filename)} className="history-item">
                                    <div style={{display: 'flex', alignItems: 'center'}}>
                                        <FileText size={18} style={{marginRight: '10px', color: '#60a5fa'}}/>
                                        <span style={{fontSize: '0.9rem'}}>{doc.filename}</span>
                                    </div>
                                    <span style={{fontSize: '0.8rem', color: '#6b7280', display: 'flex', alignItems: 'center'}}>
                                        <Clock size={12} style={{marginRight: '4px'}}/> {doc.date.split(' ')[0]}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT PANEL: Chat */}
      <div className="right-panel">
        
        {isSpeaking && (
            <button onClick={stopSpeaking} className="btn btn-float-stop btn-red">
                <StopCircle size={20} style={{marginRight: '5px'}}/> Stop Reading
            </button>
        )}

        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.type === 'user' ? 'user-row' : ''}`}>
              
              {msg.type === 'ai' && (
                  <div className="avatar-col">
                      <div className="avatar bg-blue"><Bot size={18} color="white"/></div>
                      
                      <button onClick={() => speakText(msg.text)} className="icon-btn" title="Read Aloud">
                          <Volume2 size={16} />
                      </button>
                      
                      <button onClick={() => handleCopy(msg.text, index)} className="icon-btn" title="Copy Text">
                          {copiedIndex === index ? <Check size={16} color="#16a34a"/> : <Copy size={16} />}
                      </button>
                  </div>
              )}
              
              <div className={`message-bubble ${msg.type === 'user' ? 'bubble-user' : 'bubble-ai'}`}>
                {msg.text}
              </div>
              
              {msg.type === 'user' && <div className="avatar bg-purple" style={{marginLeft: '10px'}}><User size={18} color="white"/></div>}
            </div>
          ))}
          
          {thinking && (
            <div className="thinking">
              <Loader2 className="spin" size={16} /> AI is thinking...
            </div>
          )}
        </div>

        <div className="input-section">
          <div className="input-wrapper">
            <Globe className="text-gray-500" size={20} />
            <input 
              className="chat-input"
              type="text" 
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Ask anything..." 
            />
            <button onClick={() => handleAsk()} disabled={!question || thinking} className="send-btn-round">
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;