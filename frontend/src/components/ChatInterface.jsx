import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, MessageSquare, User, Bot } from 'lucide-react';
import { useDataStore } from '../store/useDataStore';

function ChatInterface() {
    const [message, setMessage] = useState('');
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const { chatHistory, isChatting, chatError, sendChatMessage } = useDataStore();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatHistory]);

    const handleSend = async () => {
        if (!message.trim() || isChatting) return;

        const userMessage = message;
        setMessage('');

        await sendChatMessage(userMessage);
        inputRef.current?.focus();
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const exampleQuestions = [
        "Show me summary statistics for all numeric columns",
        "What are the top 5 most common values in each categorical column?",
        "Plot the distribution of [column_name]",
        "Show correlation between numeric features",
        "What percentage of data is missing in each column?",
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="card bg-gradient-to-br from-primary-50 to-secondary-50 border-primary-200">
                <h2 className="text-2xl font-bold text-slate-800 mb-2">
                    <MessageSquare className="w-6 h-6 inline mr-2 text-primary-600" />
                    Chat with Your Data
                </h2>
                <p className="text-slate-600">
                    Ask questions in natural language and get instant insights from your dataset
                </p>
            </div>

            {/* Chat Container */}
            <div className="card p-0 overflow-hidden">
                {/* Messages Area */}
                <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-slate-50 to-white">
                    {chatHistory.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-center">
                            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                                <MessageSquare className="w-8 h-8 text-primary-600" />
                            </div>
                            <h3 className="text-lg font-semibold text-slate-800 mb-2">Start a Conversation</h3>
                            <p className="text-slate-600 mb-6 max-w-md">
                                Ask questions about your data and I'll help you analyze it
                            </p>

                            {/* Example Questions */}
                            <div className="w-full max-w-2xl">
                                <p className="text-sm font-semibold text-slate-700 mb-3">Try asking:</p>
                                <div className="space-y-2">
                                    {exampleQuestions.map((q, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setMessage(q)}
                                            className="w-full text-left p-3 bg-white border border-slate-200 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-all text-sm text-slate-700"
                                        >
                                            {q}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <>
                            {chatHistory.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={`flex items-start space-x-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'
                                        }`}
                                >
                                    {msg.role === 'assistant' && (
                                        <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center flex-shrink-0">
                                            <Bot className="w-5 h-5 text-white" />
                                        </div>
                                    )}

                                    <div
                                        className={`max-w-[70%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                                                ? 'bg-primary-600 text-white'
                                                : 'bg-white border border-slate-200 text-slate-800'
                                            }`}
                                    >
                                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>

                                        {msg.visualization && (
                                            <div className="mt-3 p-3 bg-slate-50 rounded-lg">
                                                <p className="text-xs text-slate-500 mb-2">📊 Visualization</p>
                                                {msg.visualization.type === 'image' && msg.visualization.data && (
                                                    <img 
                                                        src={`data:image/png;base64,${msg.visualization.data}`}
                                                        alt="Generated visualization"
                                                        className="w-full rounded border border-slate-200"
                                                    />
                                                )}
                                            </div>
                                        )}

                                        {msg.data_result && msg.data_result.length > 0 && (
                                            <div className="mt-3 overflow-x-auto">
                                                <table className="text-xs w-full">
                                                    <thead className="bg-slate-100">
                                                        <tr>
                                                            {Object.keys(msg.data_result[0]).map((key) => (
                                                                <th key={key} className="px-2 py-1 text-left font-semibold">
                                                                    {key}
                                                                </th>
                                                            ))}
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {msg.data_result.slice(0, 5).map((row, i) => (
                                                            <tr key={i} className="border-t border-slate-200">
                                                                {Object.values(row).map((val, j) => (
                                                                    <td key={j} className="px-2 py-1">
                                                                        {String(val)}
                                                                    </td>
                                                                ))}
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                                {msg.data_result.length > 5 && (
                                                    <p className="text-xs text-slate-500 mt-2">
                                                        Showing 5 of {msg.data_result.length} rows
                                                    </p>
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {msg.role === 'user' && (
                                        <div className="w-8 h-8 bg-slate-300 rounded-full flex items-center justify-center flex-shrink-0">
                                            <User className="w-5 h-5 text-slate-600" />
                                        </div>
                                    )}
                                </div>
                            ))}

                            {isChatting && (
                                <div className="flex items-start space-x-3">
                                    <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3">
                                        <div className="flex space-x-2">
                                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </>
                    )}
                </div>

                {/* Input Area */}
                <div className="border-t border-slate-200 p-4 bg-white">
                    {chatError && (
                        <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                            {chatError}
                        </div>
                    )}

                    <div className="flex space-x-3">
                        <textarea
                            ref={inputRef}
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask a question about your data..."
                            className="flex-1 px-4 py-3 rounded-lg border-2 border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none resize-none"
                            rows="2"
                            disabled={isChatting}
                        />
                        <button
                            onClick={handleSend}
                            disabled={isChatting || !message.trim()}
                            className="btn-primary px-6 self-end"
                        >
                            {isChatting ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </button>
                    </div>

                    <p className="text-xs text-slate-500 mt-2">
                        Press Enter to send, Shift+Enter for new line
                    </p>
                </div>
            </div>

            {/* Info Card */}
            <div className="card bg-blue-50 border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">💡 Chat Features</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Ask questions in natural language</li>
                    <li>• Get statistical summaries and insights</li>
                    <li>• Generate visualizations on demand</li>
                    <li>• Query specific columns or relationships</li>
                    <li>• All responses are based on your uploaded data</li>
                </ul>
            </div>
        </div>
    );
}

export default ChatInterface;
