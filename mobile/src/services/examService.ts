import api from './api';
import { Exam } from '../types';

export const examService = {
  getAll: async (): Promise<Exam[]> => {
    const response = await api.get('/exams');
    return response.data;
  },

  getById: async (id: string): Promise<Exam> => {
    const response = await api.get(`/exams/${id}`);
    return response.data;
  },

  startExam: async (id: string) => {
    const response = await api.post(`/exams/${id}/start`);
    return response.data;
  },

  submitExam: async (id: string, answers: Record<string, string | string[]>) => {
    const response = await api.post(`/exams/${id}/submit`, {
      answers,
    });
    return response.data;
  },
};



