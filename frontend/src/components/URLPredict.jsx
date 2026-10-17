import React, { useState } from 'react';

export default function URLPredict() {
  const [urlInput, setUrlInput] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!urlInput.trim()) return;

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('/api/detect_url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlInput.trim() }),
      });

      if (!response.ok) throw new Error('Server error during URL detection');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('Failed to analyze URL: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          placeholder="https://example.com"
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !urlInput.trim()}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Processing...' : 'Analyze URL'}
        </button>
      </form>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {result && !error && (
        <div className="mt-6">
          <h3 className="font-semibold text-lg">Result:</h3>
          <p>
            URL: <code>{result.url}</code>
          </p>
          <p>
            Status:{' '}
            <span
              className={`px-2 py-1 rounded-full text-white ${
                result.isMalicious ? 'bg-red-600' : 'bg-green-600'
              }`}
            >
              {result.isMalicious ? 'Malicious' : 'Safe'}
            </span>
          </p>
        </div>
      )}
    </>
  );
}
