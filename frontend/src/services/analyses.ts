import api from './api';
import { Analysis, AnalysisListItem } from '../types';

export const analysisService = {
  async create(data: { resume_id: number; job_title: string; job_description: string }): Promise<Analysis> {
    const res = await api.post<Analysis>('/analyses', data);
    return res.data;
  },

  async list(): Promise<AnalysisListItem[]> {
    const res = await api.get<AnalysisListItem[]>('/analyses');
    return res.data;
  },

  async get(id: number): Promise<Analysis> {
    const res = await api.get<Analysis>(`/analyses/${id}`);
    return res.data;
  },

  async delete(id: number): Promise<{ message: string }> {
    const res = await api.delete<{ message: string }>(`/analyses/${id}`);
    return res.data;
  },

  async downloadReport(id: number, filename?: string): Promise<void> {
    const res = await api.get(`/analyses/${id}/report`, {
      responseType: 'blob',
    });
    const blob = new Blob([res.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename || `Resume_Analysis_Report_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
