import axios, { AxiosInstance } from 'axios';
import { setupInterceptors } from './interceptors';

// Set the API base URL
const API_URL = process.env.VUE_APP_API_URL || 'http://backend:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 15000,
});

setupInterceptors(api);

export default api;