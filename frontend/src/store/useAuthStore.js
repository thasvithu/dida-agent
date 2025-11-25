import { create } from 'zustand';

/**
 * Authentication store for managing OpenAI API keys
 */
export const useAuthStore = create((set, get) => ({
    apiKey: null,
    hasSessionKey: false,
    hasSystemKey: false,
    isValidating: false,
    validationError: null,

    setApiKey: (apiKey) => set({ apiKey }),

    validateAndSetKey: async (apiKey) => {
        set({ isValidating: true, validationError: null });

        try {
            const sessionId = get().getSessionId();
            const response = await fetch('/api/auth/set-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': sessionId,
                },
                body: JSON.stringify({ api_key: apiKey }),
            });

            const data = await response.json();

            if (data.valid) {
                set({
                    apiKey,
                    hasSessionKey: true,
                    isValidating: false,
                    validationError: null
                });
                return { success: true, message: data.message };
            } else {
                set({
                    isValidating: false,
                    validationError: data.message
                });
                return { success: false, message: data.message };
            }
        } catch (error) {
            const errorMsg = 'Failed to validate API key';
            set({
                isValidating: false,
                validationError: errorMsg
            });
            return { success: false, message: errorMsg };
        }
    },

    removeApiKey: async () => {
        try {
            const sessionId = get().getSessionId();
            await fetch('/api/auth/remove-key', {
                method: 'DELETE',
                headers: {
                    'X-Session-ID': sessionId,
                },
            });

            set({
                apiKey: null,
                hasSessionKey: false,
                validationError: null
            });
        } catch (error) {
            console.error('Failed to remove API key:', error);
        }
    },

    checkKeyStatus: async () => {
        try {
            const sessionId = get().getSessionId();
            const response = await fetch('/api/auth/key-status', {
                headers: {
                    'X-Session-ID': sessionId,
                },
            });

            const data = await response.json();
            set({
                hasSessionKey: data.has_session_key,
                hasSystemKey: data.has_system_key
            });
        } catch (error) {
            console.error('Failed to check key status:', error);
        }
    },

    getSessionId: () => {
        let sessionId = sessionStorage.getItem('dida_session_id');
        if (!sessionId) {
            sessionId = crypto.randomUUID();
            sessionStorage.setItem('dida_session_id', sessionId);
        }
        return sessionId;
    },
}));
