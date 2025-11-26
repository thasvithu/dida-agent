import { create } from 'zustand';

/**
 * Data store for managing dataset state and operations
 */
export const useDataStore = create((set, get) => ({
    // Upload state
    uploadedFile: null,
    sessionId: null,
    isUploading: false,
    uploadError: null,

    // Dataset info
    dataset: null,
    preview: [],
    columnNames: [],
    rows: 0,
    columns: 0,

    // Analysis state
    analysis: null,
    isAnalyzing: false,
    analysisError: null,

    // Cleaning state
    cleaningResult: null,
    isCleaning: false,
    cleaningError: null,

    // Feature engineering state
    featureEngineering: null,
    isEngineeringFeatures: false,
    featureEngineeringError: null,

    // Report state
    report: null,
    isGeneratingReport: false,
    reportError: null,

    // ML Preparation state
    mlPrep: null,
    isPreparingML: false,
    mlPrepError: null,

    // Chat state
    chatHistory: [],
    isChatting: false,
    chatError: null,

    // Actions
    uploadFile: async (file) => {
        set({ isUploading: true, uploadError: null });

        try {
            const formData = new FormData();
            formData.append('file', file);

            const sessionId = sessionStorage.getItem('dida_session_id') || crypto.randomUUID();
            sessionStorage.setItem('dida_session_id', sessionId);

            const response = await fetch('/api/upload/file', {
                method: 'POST',
                headers: {
                    'X-Session-ID': sessionId,
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();

            set({
                uploadedFile: file,
                sessionId: data.session_id,
                preview: data.preview,
                columnNames: data.column_names,
                rows: data.rows,
                columns: data.columns,
                isUploading: false,
                uploadError: null,
            });

            return { success: true, data };
        } catch (error) {
            set({
                isUploading: false,
                uploadError: error.message
            });
            return { success: false, error: error.message };
        }
    },

    uploadPastedData: async (data, delimiter = ',', hasHeader = true) => {
        set({ isUploading: true, uploadError: null });

        try {
            const sessionId = sessionStorage.getItem('dida_session_id') || crypto.randomUUID();
            sessionStorage.setItem('dida_session_id', sessionId);

            const response = await fetch('/api/upload/paste', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': sessionId,
                },
                body: JSON.stringify({
                    data,
                    delimiter,
                    has_header: hasHeader,
                }),
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const result = await response.json();

            set({
                uploadedFile: { name: 'pasted_data.csv' },
                sessionId: result.session_id,
                preview: result.preview,
                columnNames: result.column_names,
                rows: result.rows,
                columns: result.columns,
                isUploading: false,
                uploadError: null,
            });

            return { success: true, data: result };
        } catch (error) {
            set({
                isUploading: false,
                uploadError: error.message
            });
            return { success: false, error: error.message };
        }
    },

    analyzeDataset: async () => {
        set({ isAnalyzing: true, analysisError: null });

        try {
            const sessionId = get().sessionId || sessionStorage.getItem('dida_session_id');

            const response = await fetch('/api/analyze/', {
                method: 'POST',
                headers: {
                    'X-Session-ID': sessionId,
                },
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const data = await response.json();

            set({
                analysis: data,
                isAnalyzing: false,
                analysisError: null,
            });

            return { success: true, data };
        } catch (error) {
            set({
                isAnalyzing: false,
                analysisError: error.message
            });
            return { success: false, error: error.message };
        }
    },

    sendChatMessage: async (message) => {
        set({ isChatting: true, chatError: null });

        try {
            const sessionId = get().sessionId || sessionStorage.getItem('dida_session_id');
            const history = get().chatHistory;

            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': sessionId,
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    message,
                    history,
                }),
            });

            if (!response.ok) {
                throw new Error('Chat failed');
            }

            const data = await response.json();

            // Add user message and assistant response to history
            const newHistory = [
                ...history,
                { role: 'user', content: message, timestamp: new Date().toISOString() },
                {
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date().toISOString(),
                    visualization: data.visualization,
                    data_result: data.data_result,
                },
            ];

            set({
                chatHistory: newHistory,
                isChatting: false,
                chatError: null,
            });

            return { success: true, data };
        } catch (error) {
            set({
                isChatting: false,
                chatError: error.message
            });
            return { success: false, error: error.message };
        }
    },

    clearChatHistory: () => set({ chatHistory: [] }),

    cleanDataset: async () => {
        set({ isCleaning: true, cleaningError: null });
        try {
            const sessionId = get().sessionId || sessionStorage.getItem('dida_session_id');
            const response = await fetch('/api/clean/', {
                method: 'POST',
                headers: { 'X-Session-ID': sessionId, 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            if (!response.ok) throw new Error('Cleaning failed');
            const data = await response.json();
            set({ cleaningResult: data, isCleaning: false, preview: data.cleaned_preview });
            return { success: true, data };
        } catch (error) {
            set({ isCleaning: false, cleaningError: error.message });
            return { success: false, error: error.message };
        }
    },

    engineerFeatures: async (instructions = "") => {
        set({ isEngineeringFeatures: true, featureEngineeringError: null });
        try {
            const sessionId = get().sessionId || sessionStorage.getItem('dida_session_id');
            const response = await fetch('/api/feature-engineering/', {
                method: 'POST',
                headers: { 'X-Session-ID': sessionId, 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, instructions })
            });
            if (!response.ok) throw new Error('Feature engineering failed');
            const data = await response.json();
            set({ featureEngineering: data, isEngineeringFeatures: false, preview: data.preview });
            return { success: true, data };
        } catch (error) {
            set({ isEngineeringFeatures: false, featureEngineeringError: error.message });
            return { success: false, error: error.message };
        }
    },

    generateReport: async () => {
        set({ isGeneratingReport: true, reportError: null });
        try {
            const sessionId = get().sessionId || sessionStorage.getItem('dida_session_id');
            const response = await fetch('/api/report/', {
                method: 'POST',
                headers: { 'X-Session-ID': sessionId, 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            if (!response.ok) throw new Error('Report generation failed');
            const data = await response.json();
            set({ report: data, isGeneratingReport: false });
            return { success: true, data };
        } catch (error) {
            set({ isGeneratingReport: false, reportError: error.message });
            return { success: false, error: error.message };
        }
    },

    prepareForML: async (targetColumn, options = {}) => {
        set({ isPreparingML: true, mlPrepError: null });
        try {
            const sessionId = get().sessionId || sessionStorage.getItem('dida_session_id');
            const response = await fetch('/api/ml-prep/', {
                method: 'POST',
                headers: { 'X-Session-ID': sessionId, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    target_column: targetColumn,
                    test_size: options.testSize || 0.2,
                    random_state: options.randomState || 42,
                    scaling_strategy: options.scalingStrategy || 'standard',
                    encoding_strategy: options.encodingStrategy || 'auto'
                })
            });
            if (!response.ok) throw new Error('ML preparation failed');
            const data = await response.json();
            set({ mlPrep: data, isPreparingML: false });
            return { success: true, data };
        } catch (error) {
            set({ isPreparingML: false, mlPrepError: error.message });
            return { success: false, error: error.message };
        }
    },

    reset: () => set({
        uploadedFile: null,
        sessionId: null,
        dataset: null,
        preview: [],
        columnNames: [],
        rows: 0,
        columns: 0,
        analysis: null,
        cleaningResult: null,
        featureEngineering: null,
        report: null,
        chatHistory: [],
    }),
}));
