// frontend/services/authService.ts
// LifeLink AI — Authentication Service
// Architecture Reference: ARCHITECTURE.md Section 15 & Section 18

import { api } from '@/lib/api';
import { ApiSuccessResponse, User } from '@/types';

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponseData {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export const authService = {
  async register(payload: RegisterPayload): Promise<ApiSuccessResponse<User>> {
    const response = await api.post<ApiSuccessResponse<User>>('/auth/register', payload);
    return response.data;
  },

  async login(payload: LoginPayload): Promise<ApiSuccessResponse<LoginResponseData>> {
    const response = await api.post<ApiSuccessResponse<LoginResponseData>>('/auth/login', payload);
    return response.data;
  },

  async getMe(): Promise<ApiSuccessResponse<User>> {
    const response = await api.get<ApiSuccessResponse<User>>('/auth/me');
    return response.data;
  },

  async logout(): Promise<ApiSuccessResponse<{ user_id?: string }>> {
    const response = await api.post<ApiSuccessResponse<{ user_id?: string }>>('/auth/logout');
    return response.data;
  },
};

export default authService;
