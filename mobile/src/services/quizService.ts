import api from './api';
import { Quiz, QuizQuestion } from '../types';

export const quizService = {
  getByModule: async (moduleId: string): Promise<Quiz> => {
    const response = await api.get(`/quiz/module/${moduleId}`);
    return response.data;
  },

  submitAnswer: async (quizId: string, questionId: string, answer: string | string[]) => {
    const response = await api.post(`/quiz/${quizId}/submit`, {
      question_id: questionId,
      answer,
    });
    return response.data;
  },
};



