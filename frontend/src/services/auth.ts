import api from './api';
import { User, AuthResponse } from '../types';

export const authService = {
  async register(data: { full_name: string; email: string; password: string }): Promise<AuthResponse> {
    const res = await api.post<AuthResponse>('/auth/register', data);
    return res.data;
  },

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    const res = await api.post<AuthResponse>('/auth/login', data);
    return res.data;
  },

  async getMe(): Promise<User> {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },

  async updateProfile(data: { full_name: string }): Promise<User> {
    const res = await api.put<User>('/auth/me', data);
    return res.data;
  },

  async changePassword(data: { current_password: string; new_password: string }): Promise<{ message: string }> {
    const res = await api.put<{ message: string }>('/auth/password', data);
    return res.data;
  },

  async deleteAccount(): Promise<{ message: string }> {
    const res = await api.delete<{ message: string }>('/auth/account');
    return res.data;
  },
};
