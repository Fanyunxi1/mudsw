import React from 'react';
import URLPredict from './URLPredict';
import UploadCSV from './UploadCSV';

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <section className="bg-white shadow-md p-6 rounded-xl">
        <h2 className="text-xl font-semibold mb-4">🔍 URL 单条预测</h2>
        <URLPredict />
      </section>

      <section className="bg-white shadow-md p-6 rounded-xl">
        <h2 className="text-xl font-semibold mb-4">📄 批量 CSV 上传预测</h2>
        <UploadCSV />
      </section>
    </div>
  );
}
