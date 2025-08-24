import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, FileText, AlertCircle, CheckCircle, Loader2, Search, Database, Settings } from 'lucide-react';

const PolicyQAApp = () => {
  const [activeTab, setActiveTab] = useState('query');
  const [query, setQuery] = useState('');
  const [queryMode, setQueryMode] = useState('chat');
  const [answer, setAnswer] = useState('');
  const [citations, setCitations] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [documents, setDocuments] = useState([]);
  const fileInputRef = useRef(null);

  const API_BASE = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000';
  const API_KEY = process.env.REACT_APP_API_KEY || 'A5E2FF2AA14D6E4D7CED4DA742F9A';

  const headers = {
    'X-API-Key': API_KEY,
  };

  // Fetch documents on component mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      // Note: This would need to be implemented in your FastAPI backend
      // For now, we'll simulate it
      setDocuments([]);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setLoading(true);
    setUploadStatus('Uploading files...');

    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      const response = await fetch(`${API_BASE}/ingest`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const result = await response.json();
      setUploadedFiles(prev => [...prev, ...files.map(f => f.name)]);
      setUploadStatus(`Successfully uploaded ${result.total_files || files.length} file(s). Processed ${result.total_chunks || 0} chunks.`);
      fetchDocuments();
    } catch (error) {
      setUploadStatus(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setAnswer('');
    setCitations([]);
    setMetrics(null);

    try {
      const url = queryMode === 'form' ? `${API_BASE}/query?mode=form` : `${API_BASE}/query`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const result = await response.json();
      setAnswer(result.answer || 'No answer provided');
      setCitations(result.citations || []);
      setMetrics(result.metrics || null);
    } catch (error) {
      setAnswer(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const runEvaluation = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/eval/run`, {
        method: 'POST',
        headers,
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const result = await response.json();
      alert(`Evaluation completed! Results: ${JSON.stringify(result, null, 2)}`);
    } catch (error) {
      alert(`Evaluation failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Policy Q&A</h1>
                <p className="text-gray-500 text-sm">AI-powered document analysis with citations</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-8">
          {[
            { id: 'query', label: 'Query', icon: Search },
            { id: 'upload', label: 'Upload Documents', icon: Upload },
            { id: 'eval', label: 'Evaluation', icon: Settings }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div className="space-y-6">
            {/* Query Mode Selection */}
            <div className="bg-white rounded-xl p-6 shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">Query Mode</h3>
              <div className="flex space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="chat"
                    checked={queryMode === 'chat'}
                    onChange={(e) => setQueryMode(e.target.value)}
                    className="text-blue-600"
                  />
                  <span>Regular Q&A</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="form"
                    checked={queryMode === 'form'}
                    onChange={(e) => setQueryMode(e.target.value)}
                    className="text-blue-600"
                  />
                  <span>Form Filling</span>
                </label>
              </div>
            </div>

            {/* Query Input */}
            <div className="bg-white rounded-xl p-6 shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">Ask a Question</h3>
              <div className="space-y-4">
                <div className="relative">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter your question about the uploaded documents..."
                    className="w-full p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                  />
                </div>
                <button
                  onClick={handleQuery}
                  disabled={loading || !query.trim()}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  <span>{loading ? 'Processing...' : 'Submit Query'}</span>
                </button>
              </div>
            </div>

            {/* Answer Display */}
            {(answer || loading) && (
              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">Answer</h3>
                {loading ? (
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Analyzing documents and generating response...</span>
                  </div>
                ) : (
                  <div className="prose max-w-none">
                    <p className="text-gray-800 whitespace-pre-wrap">{answer}</p>
                  </div>
                )}
              </div>
            )}

            {/* Citations */}
            {citations.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">Citations</h3>
                <div className="space-y-3">
                  {citations.map((citation, index) => (
                    <div key={index} className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">
                        Document: {citation.document_id} | Chunk: {citation.chunk_id}
                      </div>
                      <div className="text-gray-800">{citation.text}</div>
                      {citation.score && (
                        <div className="text-xs text-gray-500 mt-2">
                          Relevance Score: {citation.score.toFixed(3)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Metrics */}
            {metrics && (
              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">Query Metrics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(metrics).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-xs text-gray-500 uppercase tracking-wide">{key}</div>
                      <div className="text-lg font-semibold">
                        {typeof value === 'number' ? value.toFixed(3) : value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* File Upload */}
            <div className="bg-white rounded-xl p-6 shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">Upload Documents</h3>
              <div className="space-y-4">
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
                >
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg text-gray-600 mb-2">Click to upload files</p>
                  <p className="text-sm text-gray-500">Supports PDF, DOCX, HTML, and TXT files</p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.docx,.html,.htm,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>
                
                {uploadStatus && (
                  <div className={`p-4 rounded-lg flex items-center space-x-2 ${
                    uploadStatus.includes('failed') || uploadStatus.includes('Error')
                      ? 'bg-red-50 text-red-700'
                      : 'bg-green-50 text-green-700'
                  }`}>
                    {uploadStatus.includes('failed') || uploadStatus.includes('Error') ? (
                      <AlertCircle className="h-5 w-5" />
                    ) : (
                      <CheckCircle className="h-5 w-5" />
                    )}
                    <span>{uploadStatus}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <h3 className="text-lg font-semibold mb-4">Uploaded Files</h3>
                <div className="space-y-2">
                  {uploadedFiles.map((filename, index) => (
                    <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                      <FileText className="h-4 w-4 text-gray-600" />
                      <span className="text-gray-800">{filename}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Evaluation Tab */}
        {activeTab === 'eval' && (
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <h3 className="text-lg font-semibold mb-4">Run Evaluation</h3>
            <p className="text-gray-600 mb-6">
              Run the evaluation suite against your uploaded documents to test the system's performance.
            </p>
            <button
              onClick={runEvaluation}
              disabled={loading}
              className="flex items-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Database className="h-4 w-4" />}
              <span>{loading ? 'Running Evaluation...' : 'Run Evaluation'}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PolicyQAApp;