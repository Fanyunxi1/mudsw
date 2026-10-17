import React from 'react';
import Dashboard from './components/Dashboard';

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4">LinkScaner</h1>
          <p className="text-lg text-gray-600">Analyze URLs or CSV files to detect malicious content.</p>
        </div>
        <Dashboard />
        <div className="mt-6 text-center text-sm text-gray-500">Powered by ML URL scanner</div>
      </div>
    </div>
  );
}
