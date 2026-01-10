import api from './api';
import { Module, Subject, Difficulty } from '../types';

export const moduleService = {
  getAll: async (subject?: Subject, difficulty?: Difficulty): Promise<Module[]> => {
    const params: any = {};
    if (subject) params.subject = subject;
    if (difficulty) params.difficulty = difficulty;

    const response = await api.get('/modules', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Module> => {
    const response = await api.get(`/modules/${id}`);
    return response.data;
  },

  getProgress: async (moduleId: string) => {
    const response = await api.get(`/progress/${moduleId}`);
    return response.data;
  },

  updateProgress: async (moduleId: string, progress: number, completed: boolean) => {
    const response = await api.post('/progress', {
      module_id: moduleId,
      progress_percentage: progress,
      completed,
    });
    return response.data;
  },
};



