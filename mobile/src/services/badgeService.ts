import api from './api';
import { Badge } from '../types';

export const badgeService = {
  getAll: async (): Promise<Badge[]> => {
    const response = await api.get('/badges');
    return response.data;
  },

  getUserBadges: async (userId?: string): Promise<Badge[]> => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/badges/user', { params });
    return response.data;
  },
};



