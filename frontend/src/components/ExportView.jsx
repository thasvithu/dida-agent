import React, { useState } from 'react';
import { Download, FileText, Code, BookOpen, FileJson, CheckCircle2, Loader2 } from 'lucide-react';
import { useDataStore } from '../store/useDataStore';

function ExportView() {
    const [selectedFormats, setSelectedFormats] = useState(['csv']);
    const [includeOriginal, setIncludeOriginal] = useState(false);
    const [isExporting, setIsExporting] = useState(false);
    const [exportResult, setExportResult] = useState(null);

    const { sessionId } = useDataStore();

    const formats = [
        {
            id: 'csv',
            label: 'CSV File',
            icon: FileText,
            description: 'Comma-separated values format',
            color: 'bg-green-100 text-green-700 border-green-300',
        },
        {
            id: 'excel',
            label: 'Excel File',
            icon: FileText,
            description: 'Microsoft Excel spreadsheet',
            color: 'bg-blue-100 text-blue-700 border-blue-300',
        },
        {
            id: 'json',
            label: 'JSON File',
            icon: FileJson,
            description: 'JavaScript Object Notation',
            color: 'bg-yellow-100 text-yellow-700 border-yellow-300',
        },
        {
            id: 'python',
            label: 'Python Script',
            icon: Code,
            description: 'Reproducible Python code',
            color: 'bg-purple-100 text-purple-700 border-purple-300',
        },
        {
            id: 'notebook',
            label: 'Jupyter Notebook',
            icon: BookOpen,
            description: 'Interactive analysis notebook',
            color: 'bg-orange-100 text-orange-700 border-orange-300',
        },
    ];

    const toggleFormat = (formatId) => {
        setSelectedFormats((prev) =>
            prev.includes(formatId)
                ? prev.filter((f) => f !== formatId)
                : [...prev, formatId]
        );
    };

    const handleExport = async () => {
        if (selectedFormats.length === 0) return;

        setIsExporting(true);
        setExportResult(null);

        try {
            const response = await fetch('/api/export/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': sessionId,
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    formats: selectedFormats,
                    include_original: includeOriginal,
                }),
            });

            if (!response.ok) {
                throw new Error('Export failed');
            }

            const data = await response.json();
            setExportResult(data);
        } catch (error) {
            console.error('Export error:', error);
            alert('Export failed: ' + error.message);
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="card bg-gradient-to-br from-primary-50 to-secondary-50 border-primary-200">
                <h2 className="text-2xl font-bold text-slate-800 mb-2">
                    <Download className="w-6 h-6 inline mr-2 text-primary-600" />
                    Export Your Data
                </h2>
                <p className="text-slate-600">
                    Download your processed data in various formats for further analysis or sharing
                </p>
            </div>

            {/* Format Selection */}
            <div className="card">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Select Export Formats</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {formats.map((format) => {
                        const Icon = format.icon;
                        const isSelected = selectedFormats.includes(format.id);

                        return (
                            <button
                                key={format.id}
                                onClick={() => toggleFormat(format.id)}
                                className={`p-4 rounded-lg border-2 transition-all text-left ${
                                    isSelected
                                        ? `${format.color} border-current scale-105 shadow-md`
                                        : 'bg-white border-slate-200 hover:border-primary-300'
                                }`}
                            >
                                <div className="flex items-start space-x-3">
                                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                                        isSelected ? 'bg-white/50' : 'bg-slate-100'
                                    }`}>
                                        <Icon className="w-5 h-5" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <h4 className="font-semibold">{format.label}</h4>
                                            {isSelected && (
                                                <CheckCircle2 className="w-5 h-5" />
                                            )}
                                        </div>
                                        <p className="text-sm opacity-80">{format.description}</p>
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Options */}
            <div className="card">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Export Options</h3>
                <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                        type="checkbox"
                        checked={includeOriginal}
                        onChange={(e) => setIncludeOriginal(e.target.checked)}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
                    />
                    <div>
                        <span className="font-medium text-slate-800">Include Original Dataset</span>
                        <p className="text-sm text-slate-600">
                            Export the original uploaded file alongside processed versions
                        </p>
                    </div>
                </label>
            </div>

            {/* Export Button */}
            <div className="card bg-gradient-to-r from-primary-50 to-secondary-50 border-primary-200">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="font-semibold text-slate-800 mb-1">Ready to Export</h3>
                        <p className="text-sm text-slate-600">
                            {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
                        </p>
                    </div>
                    <button
                        onClick={handleExport}
                        disabled={selectedFormats.length === 0 || isExporting}
                        className="btn-primary px-6"
                    >
                        {isExporting ? (
                            <>
                                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                Exporting...
                            </>
                        ) : (
                            <>
                                <Download className="w-5 h-5 mr-2" />
                                Export Files
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Export Results */}
            {exportResult && (
                <div className="card bg-green-50 border-green-200 animate-fade-in">
                    <div className="flex items-center text-green-800 font-medium mb-3">
                        <CheckCircle2 className="w-5 h-5 mr-2" />
                        Export Successful
                    </div>
                    <p className="text-sm text-green-700 mb-4">{exportResult.summary}</p>
                    
                    <div className="space-y-2">
                        <h4 className="font-semibold text-green-900 text-sm mb-2">Download Files:</h4>
                        {Object.entries(exportResult.files).map(([format, url]) => {
                            const formatInfo = formats.find((f) => f.id === format) || {
                                label: format.toUpperCase(),
                                icon: FileText,
                            };
                            const Icon = formatInfo.icon;

                            return (
                                <a
                                    key={format}
                                    href={url}
                                    download
                                    className="flex items-center justify-between p-3 bg-white rounded-lg border border-green-200 hover:border-green-400 hover:shadow-md transition-all group"
                                >
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
                                            <Icon className="w-5 h-5 text-green-700" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-slate-800">{formatInfo.label}</p>
                                            <p className="text-xs text-slate-500">{url.split('/').pop()}</p>
                                        </div>
                                    </div>
                                    <Download className="w-5 h-5 text-green-600 group-hover:scale-110 transition-transform" />
                                </a>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Info */}
            <div className="card bg-blue-50 border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">💡 Export Tips</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                    <li>• CSV and Excel formats are best for data analysis tools</li>
                    <li>• Python script provides reproducible analysis code</li>
                    <li>• Jupyter notebook is great for interactive exploration</li>
                    <li>• JSON format is ideal for web applications and APIs</li>
                    <li>• All exports use the most processed version of your data</li>
                </ul>
            </div>
        </div>
    );
}

export default ExportView;
