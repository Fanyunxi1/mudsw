import React, { useState, useRef } from 'react';
import { UploadCloud, Trash2, Download, Loader2 } from 'lucide-react';

export default function UploadCSV() {
    const [file, setFile] = useState(null);
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState(''); // 新增状态管理成功消息
    const fileInputRef = useRef(null);

    const handleFileChange = async (e) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile) return;

        if (!selectedFile.name.endsWith('.csv')) {
            setError('请上传 CSV 文件');
            return;
        }

        setFile(selectedFile);
        setIsLoading(true);
        setError('');
        setResults(null);
        setSuccessMessage(''); // 开始处理时清除之前的成功消息

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://localhost:8001/api/upload_csv', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('服务器处理失败');

            const blob = await response.blob();

            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;

            const contentDisposition = response.headers.get('content-disposition');
            let filename = 'results.csv';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?(.+)"?/);
                if (match && match[1]) filename = match[1];
            }
            link.download = filename;

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);

            // 显示成功消息，3秒后自动清除
            setSuccessMessage('检测成功');
            setTimeout(() => {
                setSuccessMessage('');
            }, 3000);
            
            // 重置所有状态到初始值
            setFile(null);
            setResults(null);
            setError('');
            setIsLoading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';

        } catch (err) {
            setError('处理失败: ' + err.message);
            console.error('错误详情:', err);
            setIsLoading(false);
        }
    };

    const handleRemoveFile = () => {
        setFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const downloadResults = () => {
        // 实际项目中可能需要重新获取数据
        alert('下载全部结果');
    };

    return (
        <div className="max-w-4xl mx-auto p-6 bg-white shadow rounded space-y-6">
            <div className="flex items-center gap-4">
                <input
                    type="file"
                    ref={fileInputRef}
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                    id="csvUpload"
                />
                <label htmlFor="csvUpload">
                    <div className="cursor-pointer flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                        <UploadCloud className="w-4 h-4" />
                        选择 CSV 文件
                    </div>
                </label>

                {file && (
                    <div className="flex items-center bg-green-50 px-4 py-2 rounded shadow-sm">
                        <span className="text-green-700 font-medium">{file.name}</span>
                        <button onClick={handleRemoveFile} className="ml-4 text-red-600 hover:underline text-sm flex items-center gap-1">
                            <Trash2 className="w-4 h-4" />
                            移除
                        </button>
                    </div>
                )}
            </div>

            {/* 新增：显示成功消息 */}
            {successMessage && (
                <div className="text-green-600 bg-green-100 px-4 py-2 rounded flex items-center">
                    <span className="mr-2">✅</span>
                    <span>{successMessage}</span>
                </div>
            )}

            {isLoading && (
                <div className="flex items-center gap-2 text-gray-600">
                    <Loader2 className="animate-spin w-5 h-5" />
                    正在处理，请稍候...
                </div>
            )}

            {error && (
                <div className="text-red-600 bg-red-100 px-4 py-2 rounded">{error}</div>
            )}

            {results && results.length > 0 && (
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold">前 100 条检测结果</h3>

                    <div className="overflow-x-auto border rounded-lg shadow-sm">
                        <table className="min-w-full text-sm text-left table-auto">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="px-4 py-2 font-medium text-gray-700">URL</th>
                                    <th className="px-4 py-2 font-medium text-gray-700">预测标签</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.slice(0, 100).map((r, i) => (
                                    <tr key={i} className={r.isMalicious ? "bg-red-50" : ""}>
                                        <td className="px-4 py-2 break-all">{r.url}</td>
                                        <td className="px-4 py-2">
                                            <span
                                                className={`px-2 py-1 text-xs rounded-full font-semibold ${r.isMalicious
                                                    ? "bg-red-200 text-red-800"
                                                    : "bg-green-200 text-green-800"
                                                    }`}
                                            >
                                                {r.isMalicious ? "Malicious" : "Safe"}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <button
                        onClick={downloadResults}
                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
                    >
                        <Download className="w-4 h-4" />
                        下载全部结果 CSV
                    </button>
                </div>
            )}

        </div>
    );
}