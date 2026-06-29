import axios from 'axios';
import { SPLASH_DEV_API_URL, ENDPOINTS } from '../../../constants/CommonConstant';

// Initialize Axios client with standard settings
const apiClient = axios.create({
    baseURL: SPLASH_DEV_API_URL,
    timeout: 60000,
});

// Request Interceptor: Attach authentication tokens and slide session validation
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response Interceptor: Wipes local authorization configurations if 401 occurs
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const splashSendMessage = async (payload) => {
    try {
        const response = await apiClient.post(ENDPOINTS.sendMessage, payload);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.message || 'Network dispatch pipeline failed');
    }
};

export const splashStartConversation = async () => {
    // Standard mock start call matching API config specs
    return { status: 'success', conversation_id: 'conv_' + Date.now() };
};
