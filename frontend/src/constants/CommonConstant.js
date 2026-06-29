export const SPLASH_DEV_API_URL = process.env.REACT_APP_SPLASH_DEV_API_URL || 'http://localhost:8000/api';

export const ENDPOINTS = {
    startConversation: '/conversations/start',
    sendMessage: '/messages',
    getHistory: '/conversations/load',
};
