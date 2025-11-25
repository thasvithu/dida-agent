import React, { useState } from 'react';
import { X, Key, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';

function SettingsPanel({ onClose }) {
    const [apiKeyInput, setApiKeyInput] = useState('');
    const [showKey, setShowKey] = useState(false);

    const {
        apiKey,
        hasSessionKey,
        hasSystemKey,
        isValidating,
        validationError,
        validateAndSetKey,
        removeApiKey
    } = useAuthStore();

    const handleSetKey = async () => {
        if (!apiKeyInput.trim()) return;

        const result = await validateAndSetKey(apiKeyInput);
        if (result.success) {
            setApiKeyInput('');
        }
    };

    const handleRemoveKey = async () => {
        await removeApiKey();
    };

    return (
        <div className="card relative">
            <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
                <X className="w-5 h-5 text-slate-400" />
            </button>

            <h2 className="text-2xl font-bold text-slate-800 mb-2">Settings</h2>
            <p className="text-slate-600 mb-6">Configure your OpenAI API key and preferences</p>

            {/* API Key Section */}
            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                        <Key className="w-4 h-4 inline mr-2" />
                        OpenAI API Key
                    </label>

                    {/* Status Indicators */}
                    <div className="flex space-x-2 mb-3">
                        {hasSessionKey && (
                            <span className="badge badge-success">
                                <CheckCircle2 className="w-3 h-3 mr-1" />
                                Session Key Active
                            </span>
                        )}
                        {hasSystemKey && !hasSessionKey && (
                            <span className="badge badge-info">
                                System Key Available
                            </span>
                        )}
                        {!hasSessionKey && !hasSystemKey && (
                            <span className="badge badge-warning">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                No Key Configured
                            </span>
                        )}
                    </div>

                    {!hasSessionKey ? (
                        <div className="space-y-3">
                            <div className="relative">
                                <input
                                    type={showKey ? 'text' : 'password'}
                                    value={apiKeyInput}
                                    onChange={(e) => setApiKeyInput(e.target.value)}
                                    placeholder="sk-..."
                                    className="input-field pr-20 font-mono text-sm"
                                    disabled={isValidating}
                                />
                                <button
                                    onClick={() => setShowKey(!showKey)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-primary-600 hover:text-primary-700 font-medium"
                                >
                                    {showKey ? 'Hide' : 'Show'}
                                </button>
                            </div>

                            <button
                                onClick={handleSetKey}
                                disabled={isValidating || !apiKeyInput.trim()}
                                className="btn-primary w-full"
                            >
                                {isValidating ? (
                                    <>
                                        <Loader2 className="w-4 h-4 inline mr-2 animate-spin" />
                                        Validating...
                                    </>
                                ) : (
                                    'Validate and Save Key'
                                )}
                            </button>

                            {validationError && (
                                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                                    <AlertCircle className="w-4 h-4 inline mr-2" />
                                    {validationError}
                                </div>
                            )}

                            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                <h4 className="font-semibold text-blue-900 text-sm mb-2">🔒 Privacy & Security</h4>
                                <ul className="text-xs text-blue-800 space-y-1">
                                    <li>• Your API key is stored in session memory only</li>
                                    <li>• Keys are never saved to disk or database</li>
                                    <li>• Keys are cleared when you close the browser</li>
                                    <li>• All requests are made directly to OpenAI</li>
                                </ul>
                            </div>

                            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                                <h4 className="font-semibold text-slate-800 text-sm mb-2">📝 How to get an API key</h4>
                                <ol className="text-xs text-slate-600 space-y-1 list-decimal list-inside">
                                    <li>Go to <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">platform.openai.com/api-keys</a></li>
                                    <li>Sign in or create an OpenAI account</li>
                                    <li>Click "Create new secret key"</li>
                                    <li>Copy the key and paste it above</li>
                                </ol>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h4 className="font-semibold text-green-900 text-sm mb-1">
                                            <CheckCircle2 className="w-4 h-4 inline mr-2" />
                                            API Key Configured
                                        </h4>
                                        <p className="text-xs text-green-700">
                                            Your OpenAI API key is active and ready to use
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={handleRemoveKey}
                                className="btn-secondary w-full text-red-600 hover:text-red-700 hover:border-red-300"
                            >
                                Remove API Key
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default SettingsPanel;
