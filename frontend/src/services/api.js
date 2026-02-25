import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  createSession: async () => {
    const response = await api.post('/chat/session');
    return response.data;
  },

  sendMessage: async (sessionId, message) => {
    const response = await api.post('/chat/message', {
      session_id: sessionId,
      message: message,
    });
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/chat/session/${sessionId}`);
    return response.data;
  },

  scrapePrices: async (laptopName) => {
    const response = await api.post('/scraper/prices', {
      laptop_name: laptopName,
    }, {
      timeout: 60000, // 60 seconds — scraping takes time
    });
    return response.data;
  },
};

export default api;