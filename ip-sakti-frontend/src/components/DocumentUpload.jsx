import React, { useState } from 'react';
import { uploadDocument } from '../api/chatApi';

export const DocumentUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [isError, setIsError] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const allowedTypes = ['application/pdf', 'text/plain'];
      
      if (!allowedTypes.includes(selectedFile.type) && !selectedFile.name.match(/\.(pdf|txt)$/i)) {
        setStatusMessage('Error: Only PDF (.pdf) and Text (.txt) files are allowed.');
        setIsError(true);
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setStatusMessage('');
      setIsError(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || uploading) return;

    setUploading(true);
    setStatusMessage('Uploading and re-indexing dynamic FAISS vector store...');
    setIsError(false);

    try {
      const response = await uploadDocument(file);
      setStatusMessage(`Success: ${response.message}`);
      setIsError(false);
      setFile(null);
      e.target.reset();

      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (err) {
      setStatusMessage(`Error: ${err.message || 'Failed to upload document'}`);
      setIsError(true);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{
      padding: '20px',
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      marginBottom: '20px',
      backgroundColor: '#ffffff',
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
    }}>
      <h3 style={{ marginTop: 0, marginBottom: '10px', color: '#1a202c' }}>
        Add Legal Document to Knowledge Base
      </h3>
      <p style={{ margin: '0 0 15px 0', fontSize: '14px', color: '#666' }}>
        Upload supplementary statutory PDFs or TXT documents to trigger dynamic FAISS re-indexing.
      </p>

      <form onSubmit={handleUpload} style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          disabled={uploading}
          style={{ flex: 1, minWidth: '240px' }}
        />
        <button
          type="submit"
          disabled={!file || uploading}
          style={{
            padding: '10px 20px',
            backgroundColor: file && !uploading ? '#28a745' : '#6c757d',
            color: '#ffffff',
            border: 'none',
            borderRadius: '6px',
            cursor: file && !uploading ? 'pointer' : 'not-allowed',
            fontWeight: '600'
          }}
        >
          {uploading ? 'Processing & Indexing...' : 'Upload & Re-index'}
        </button>
      </form>

      {statusMessage && (
        <div style={{
          marginTop: '15px',
          padding: '10px 12px',
          borderRadius: '6px',
          fontSize: '14px',
          backgroundColor: isError ? '#f8d7da' : '#d4edda',
          color: isError ? '#721c24' : '#155724',
          border: `1px solid ${isError ? '#f5c6cb' : '#c3e6cb'}`
        }}>
          {statusMessage}
        </div>
      )}
    </div>
  );
};
