import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useDataStore } from '../store/useDataStore';

function FileUpload() {
    const [isDragging, setIsDragging] = useState(false);
    const [showPasteInput, setShowPasteInput] = useState(false);
    const [pastedData, setPastedData] = useState('');
    const fileInputRef = useRef(null);

    const { uploadFile, uploadPastedData, isUploading, uploadError } = useDataStore();

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            await uploadFile(files[0]);
        }
    };

    const handleFileSelect = async (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            await uploadFile(files[0]);
        }
    };

    const handlePasteUpload = async () => {
        if (!pastedData.trim()) return;

        const result = await uploadPastedData(pastedData);
        if (result.success) {
            setPastedData('');
            setShowPasteInput(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="card">
                <h2 className="text-2xl font-bold text-slate-800 mb-2">Upload Your Dataset</h2>
                <p className="text-slate-600 mb-6">
                    Upload a CSV, Excel, or TSV file, or paste your data directly
                </p>

                {/* Drag and Drop Area */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${isDragging
                            ? 'border-primary-500 bg-primary-50 scale-105'
                            : 'border-slate-300 hover:border-primary-400 hover:bg-slate-50'
                        }`}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".csv,.xlsx,.xls,.tsv"
                        onChange={handleFileSelect}
                        className="hidden"
                    />

                    <div className="flex flex-col items-center space-y-4">
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors ${isDragging ? 'bg-primary-200' : 'bg-slate-100'
                            }`}>
                            <Upload className={`w-8 h-8 ${isDragging ? 'text-primary-600' : 'text-slate-400'}`} />
                        </div>

                        <div>
                            <p className="text-lg font-semibold text-slate-700">
                                {isDragging ? 'Drop your file here' : 'Drag and drop your file here'}
                            </p>
                            <p className="text-sm text-slate-500 mt-1">
                                Supports CSV, Excel (.xlsx, .xls), and TSV files
                            </p>
                        </div>

                        <div className="flex space-x-3">
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                disabled={isUploading}
                                className="btn-primary"
                            >
                                <FileText className="w-4 h-4 inline mr-2" />
                                Browse Files
                            </button>

                            <button
                                onClick={() => setShowPasteInput(!showPasteInput)}
                                disabled={isUploading}
                                className="btn-secondary"
                            >
                                Paste Data
                            </button>
                        </div>
                    </div>

                    {isUploading && (
                        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <div className="text-center">
                                <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-3"></div>
                                <p className="text-slate-600 font-medium">Uploading and parsing...</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Paste Input Area */}
                {showPasteInput && (
                    <div className="mt-6 p-6 bg-slate-50 rounded-xl border border-slate-200 animate-slide-up">
                        <h3 className="font-semibold text-slate-800 mb-3">Paste Your Data</h3>
                        <textarea
                            value={pastedData}
                            onChange={(e) => setPastedData(e.target.value)}
                            placeholder="Paste CSV data here (with headers)..."
                            className="input-field font-mono text-sm h-48 resize-none"
                            disabled={isUploading}
                        />
                        <div className="flex justify-end space-x-3 mt-3">
                            <button
                                onClick={() => {
                                    setShowPasteInput(false);
                                    setPastedData('');
                                }}
                                className="btn-secondary text-sm"
                                disabled={isUploading}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handlePasteUpload}
                                disabled={isUploading || !pastedData.trim()}
                                className="btn-primary text-sm"
                            >
                                Upload Pasted Data
                            </button>
                        </div>
                    </div>
                )}

                {/* Error Display */}
                {uploadError && (
                    <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3 animate-fade-in">
                        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <h4 className="font-semibold text-red-900">Upload Failed</h4>
                            <p className="text-sm text-red-700 mt-1">{uploadError}</p>
                        </div>
                    </div>
                )}

                {/* Success Message */}
                {!isUploading && !uploadError && useDataStore.getState().uploadedFile && (
                    <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-3 animate-fade-in">
                        <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <h4 className="font-semibold text-green-900">Upload Successful</h4>
                            <p className="text-sm text-green-700 mt-1">
                                Your dataset has been uploaded and is ready for analysis
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Supported Formats Info */}
            <div className="card bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
                <h3 className="font-semibold text-slate-800 mb-3">📊 Supported Formats</h3>
                <ul className="space-y-2 text-sm text-slate-700">
                    <li className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                        <span><strong>CSV</strong> - Comma-separated values (.csv)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                        <span><strong>Excel</strong> - Microsoft Excel files (.xlsx, .xls)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                        <span><strong>TSV</strong> - Tab-separated values (.tsv)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                        <span><strong>Paste</strong> - Copy and paste data directly</span>
                    </li>
                </ul>
                <p className="text-xs text-slate-500 mt-4">
                    Maximum file size: 100MB
                </p>
            </div>
        </div>
    );
}

export default FileUpload;
