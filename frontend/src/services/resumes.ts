import api from './api';
import { Resume, ResumeListItem } from '../types';

export const resumeService = {
  async upload(file: File, onProgress?: (percent: number) => void): Promise<Resume> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await api.post<Resume>('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    });
    return res.data;
  },

  async list(): Promise<ResumeListItem[]> {
    const res = await api.get<ResumeListItem[]>('/resumes');
    return res.data;
  },

  async get(id: number): Promise<Resume> {
    const res = await api.get<Resume>(`/resumes/${id}`);
    return res.data;
  },

  async delete(id: number): Promise<{ message: string }> {
    const res = await api.delete<{ message: string }>(`/resumes/${id}`);
    return res.data;
  },
};
