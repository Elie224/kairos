export enum Subject {
  MATHEMATICS = 'mathematics',
  COMPUTER_SCIENCE = 'computer_science',
}

export enum Difficulty {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
}

export interface Module {
  id: string;
  title: string;
  description: string;
  subject: Subject;
  difficulty?: Difficulty;
  estimated_time: number;
  created_at?: string;
  updated_at?: string;
}

export interface Progress {
  id: string;
  user_id: string;
  module_id: string;
  completed: boolean;
  progress_percentage: number;
  last_accessed?: string;
  time_spent?: number;
}

export interface Quiz {
  id: string;
  module_id: string;
  title: string;
  questions: QuizQuestion[];
  time_limit?: number;
}

export interface QuizQuestion {
  id: string;
  question: string;
  type: 'multiple_choice' | 'true_false' | 'text';
  options?: string[];
  correct_answer: string | string[];
  points: number;
}

export interface Exam {
  id: string;
  module_id: string;
  title: string;
  description: string;
  duration: number; // en minutes
  questions: QuizQuestion[];
  passing_score: number;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon_url?: string;
  earned_at?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  modelUsed?: string;
}

export interface ChatStreamOptions {
  moduleId?: string;
  language?: string;
  expertMode?: boolean;
  researchMode?: boolean;
  onChunk?: (chunk: string) => void;
  onComplete?: (fullResponse: string) => void;
  onError?: (error: Error) => void;
}



