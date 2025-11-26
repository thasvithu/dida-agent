import React, { useState } from 'react';
import { Brain, Download, AlertCircle, CheckCircle2, Settings, X } from 'lucide-react';
import { useDataStore } from '../store/useDataStore';

function MLPrepModal({ isOpen, onClose, columns, suggestedTarget }) {
    const { prepareForML, isPreparingML } = useDataStore();
    const [targetColumn, setTargetColumn] = useState(suggestedTarget || '');
    const [testSize, setTestSize] = useState(0.2);
    const [scalingStrategy, setScalingStrategy] = useState('standard');
    const [encodingStrategy, setEncodingStrategy] = useState('auto');

    const handlePrepare = async () => {
        if (!targetColumn) {
            alert('Please select a target column');
            return;
        }

        const result = await prepareForML(targetColumn, {
            testSize,
            randomState: 42,
            scalingStrategy,
            encodingStrategy
        });

        if (result.success) {
            // Close modal on success so user can see results
            onClose();
        } else {
            // Show error
            alert(`ML Preparation failed: ${result.error}`);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-slate-200 flex items-center justify-between">
                    <div className="flex items-center">
                        <Brain className="w-6 h-6 text-primary-600 mr-2" />
                        <h2 className="text-2xl font-bold text-slate-800">Prepare for Machine Learning</h2>
                    </div>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {/* Target Column Selection */}
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">
                            Target Column (What you want to predict)
                        </label>
                        <select
                            value={targetColumn}
                            onChange={(e) => setTargetColumn(e.target.value)}
                            className="input w-full"
                        >
                            <option value="">Select target column...</option>
                            {columns.map((col) => (
                                <option key={col} value={col}>{col}</option>
                            ))}
                        </select>
                    </div>

                    {/* Test Size */}
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">
                            Test Set Size: {(testSize * 100).toFixed(0)}%
                        </label>
                        <input
                            type="range"
                            min="0.1"
                            max="0.4"
                            step="0.05"
                            value={testSize}
                            onChange={(e) => setTestSize(parseFloat(e.target.value))}
                            className="w-full"
                        />
                        <p className="text-xs text-slate-500 mt-1">
                            Recommended: 20-30% for most datasets
                        </p>
                    </div>

                    {/* Scaling Strategy */}
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">
                            Scaling Strategy
                        </label>
                        <select
                            value={scalingStrategy}
                            onChange={(e) => setScalingStrategy(e.target.value)}
                            className="input w-full"
                        >
                            <option value="standard">Standard (Z-score normalization)</option>
                            <option value="minmax">Min-Max (0-1 scaling)</option>
                            <option value="robust">Robust (handles outliers)</option>
                        </select>
                    </div>

                    {/* Encoding Strategy */}
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">
                            Categorical Encoding
                        </label>
                        <select
                            value={encodingStrategy}
                            onChange={(e) => setEncodingStrategy(e.target.value)}
                            className="input w-full"
                        >
                            <option value="auto">Auto (smart selection)</option>
                            <option value="onehot">One-Hot Encoding</option>
                            <option value="label">Label Encoding</option>
                        </select>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-3 pt-4">
                        <button
                            onClick={handlePrepare}
                            disabled={isPreparingML || !targetColumn}
                            className="btn-primary flex-1"
                        >
                            {isPreparingML ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                                    Preparing...
                                </>
                            ) : (
                                <>
                                    <Brain className="w-4 h-4 mr-2" />
                                    Prepare Dataset
                                </>
                            )}
                        </button>
                        <button onClick={onClose} className="btn-secondary">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

function MLPrepResults({ mlPrep, onClose }) {
    if (!mlPrep) return null;

    return (
        <div id="ml-prep-results" className="card bg-gradient-to-br from-green-50 to-blue-50 border-green-200 mt-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-slate-800 flex items-center">
                    <CheckCircle2 className="w-6 h-6 text-green-600 mr-2" />
                    ML-Ready Dataset Prepared!
                </h3>
                <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
                    <X className="w-5 h-5" />
                </button>
            </div>

            {/* Problem Type */}
            <div className="mb-4 p-3 bg-white rounded-lg border border-blue-200">
                <div className="text-sm font-semibold text-slate-700">Problem Type</div>
                <div className="text-2xl font-bold text-primary-600 capitalize">{mlPrep.problem_type}</div>
            </div>

            {/* Dataset Info */}
            <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                    <div className="text-xs text-slate-500">Training Samples</div>
                    <div className="text-xl font-bold text-slate-800">{mlPrep.train_samples}</div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                    <div className="text-xs text-slate-500">Test Samples</div>
                    <div className="text-xl font-bold text-slate-800">{mlPrep.test_samples}</div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200">
                    <div className="text-xs text-slate-500">Features</div>
                    <div className="text-xl font-bold text-slate-800">{mlPrep.num_features}</div>
                </div>
            </div>

            {/* Recommended Algorithms */}
            {mlPrep.recommended_algorithms && mlPrep.recommended_algorithms.length > 0 && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="text-sm font-semibold text-blue-900 mb-2">Recommended ML Algorithms</div>
                    <div className="flex flex-wrap gap-2">
                        {mlPrep.recommended_algorithms.map((algo, idx) => (
                            <span key={idx} className="badge bg-blue-100 text-blue-800">{algo}</span>
                        ))}
                    </div>
                </div>
            )}

            {/* Warnings */}
            {mlPrep.warnings && mlPrep.warnings.length > 0 && (
                <div className="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div className="text-sm font-semibold text-yellow-900 mb-2 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        Warnings
                    </div>
                    <ul className="text-sm text-yellow-800 space-y-1">
                        {mlPrep.warnings.map((warning, idx) => (
                            <li key={idx}>• {warning}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Best Practices */}
            {mlPrep.best_practices && mlPrep.best_practices.length > 0 && (
                <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
                    <div className="text-sm font-semibold text-green-900 mb-2">Best Practices</div>
                    <ul className="text-sm text-green-800 space-y-1">
                        {mlPrep.best_practices.map((practice, idx) => (
                            <li key={idx}>• {practice}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Download Links */}
            <div className="p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg border border-primary-200">
                <div className="text-sm font-semibold text-slate-800 mb-3">Download ML-Ready Datasets</div>
                <div className="grid grid-cols-2 gap-3">
                    {Object.entries(mlPrep.download_urls).map(([name, url]) => (
                        <a
                            key={name}
                            href={url}
                            download
                            className="btn-secondary text-sm py-2 flex items-center justify-center"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            {name}.csv
                        </a>
                    ))}
                </div>
            </div>
        </div>
    );
}

export { MLPrepModal, MLPrepResults };
