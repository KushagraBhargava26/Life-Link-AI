// frontend/lib/api.ts
// LifeLink AI — Axios API Client
// Architecture Reference: ARCHITECTURE.md Section 15 (Frontend Architecture) & Section 23 (Service Communication)
//
// Configures an Axios client instance with standard request/response envelopes
// and token interceptor stubs for JWT propagation.

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10s default timeout
});

export const apiClient = api;

// Request Interceptor — inject Bearer token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      try {
        const { useAuthStore } = require('@/store/authStore');
        const token = useAuthStore.getState().accessToken;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (e) {
        // ignore if store not initialized
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor — handle global errors
api.interceptors.response.use(
  (response) => {
    // Return standard success envelope response data
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    // Phase 1.2+: Handle token refresh on 401 response
    // if (error.response?.status === 401 && !originalRequest._retry) {
    //   originalRequest._retry = true;
    //   const newAccessToken = await refreshAccessToken();
    //   if (newAccessToken) {
    //     api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
    //     return api(originalRequest);
    //   }
    // }
    return Promise.reject(error);
  }
);
