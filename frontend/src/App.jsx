import React, { useEffect, useState } from 'react';
import { Database, Sparkles, Settings, MessageSquare, FileText, Download } from 'lucide-react';
import FileUpload from './components/FileUpload';
import DataPreview from './components/DataPreview';
import AnalysisView from './components/AnalysisView';
import SettingsPanel from './components/SettingsPanel';
import ChatInterface from './components/ChatInterface';
import { useDataStore } from './store/useDataStore';
import { useAuthStore } from './store/useAuthStore';

function App() {
    const [activeTab, setActiveTab] = useState('upload');
    const [showSettings, setShowSettings] = useState(false);

    const { uploadedFile, preview, rows, columns, analysis } = useDataStore();
    const { checkKeyStatus, hasSessionKey, hasSystemKey } = useAuthStore();

    useEffect(() => {
        checkKeyStatus();
    }, [checkKeyStatus]);

    const tabs = [
        { id: 'upload', label: 'Upload Data', icon: Database },
        { id: 'analyze', label: 'Analysis', icon: Sparkles, disabled: !uploadedFile },
        { id: 'chat', label: 'Chat', icon: MessageSquare, disabled: !uploadedFile },
    ];

    const needsApiKey = !hasSessionKey && !hasSystemKey;

    return (
        <div className="min-h-screen">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 sticky top-0 z-50 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-lg flex items-center justify-center">
                                <Sparkles className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                                    DIDA
                                </h1>
                                <p className="text-xs text-slate-500">Domain-Aware Intelligent Data Scientist Agent</p>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            {uploadedFile && (
                                <div className="text-sm text-slate-600">
                                    <span className="font-semibold">{uploadedFile.name}</span>
                                    <span className="text-slate-400 ml-2">
                                        {rows?.toLocaleString()} rows × {columns} columns
                                    </span>
                                </div>
                            )}

                            <button
                                onClick={() => setShowSettings(!showSettings)}
                                className={`p-2 rounded-lg transition-colors ${needsApiKey
                                        ? 'bg-yellow-100 text-yellow-600 animate-pulse'
                                        : 'hover:bg-slate-100 text-slate-600'
                                    }`}
                                title={needsApiKey ? 'API Key Required' : 'Settings'}
                            >
                                <Settings className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="flex space-x-1 mt-4">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => !tab.disabled && setActiveTab(tab.id)}
                                    disabled={tab.disabled}
                                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === tab.id
                                            ? 'bg-primary-600 text-white shadow-md'
                                            : tab.disabled
                                                ? 'text-slate-400 cursor-not-allowed'
                                                : 'text-slate-600 hover:bg-slate-100'
                                        }`}
                                >
                                    <Icon className="w-4 h-4" />
                                    <span>{tab.label}</span>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* API Key Warning */}
                {needsApiKey && !showSettings && (
                    <div className="mb-6 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg animate-fade-in">
                        <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-yellow-200 rounded-full flex items-center justify-center">
                                <span className="text-yellow-700 font-bold">!</span>
                            </div>
                            <div className="flex-1">
                                <h3 className="font-semibold text-yellow-900">OpenAI API Key Required</h3>
                                <p className="text-sm text-yellow-700">
                                    Please provide your OpenAI API key in settings to use DIDA's AI features.
                                </p>
                            </div>
                            <button
                                onClick={() => setShowSettings(true)}
                                className="btn-primary text-sm"
                            >
                                Add API Key
                            </button>
                        </div>
                    </div>
                )}

                {/* Settings Panel */}
                {showSettings && (
                    <div className="mb-6 animate-slide-up">
                        <SettingsPanel onClose={() => setShowSettings(false)} />
                    </div>
                )}

                {/* Tab Content */}
                <div className="animate-fade-in">
                    {activeTab === 'upload' && (
                        <div className="space-y-6">
                            <FileUpload />
                            {preview.length > 0 && <DataPreview />}
                        </div>
                    )}

                    {activeTab === 'analyze' && (
                        <AnalysisView />
                    )}

                    {activeTab === 'chat' && (
                        <ChatInterface />
                    )}
                </div>
            </main>

            {/* Footer */}
            <footer className="mt-16 py-8 border-t border-slate-200 bg-white/50">
                <div className="max-w-7xl mx-auto px-6 text-center text-sm text-slate-500">
                    <p>DIDA v1.0 - Powered by OpenAI GPT-4</p>
                    <p className="mt-1">Built with React, FastAPI, and ❤️</p>
                </div>
            </footer>
        </div>
    );
}

export default App;
