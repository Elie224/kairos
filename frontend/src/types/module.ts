/**
 * Types TypeScript pour les modules
 */
import { ModuleContent } from './moduleContent'

export interface Module {
  id: string
  title: string
  description: string
  subject: string
  difficulty?: string
  estimated_time: number
  learning_objectives?: string[]
  content?: ModuleContent
  created_at?: string
  updated_at?: string
}

export interface ModuleFilters {
  subject: string
  searchQuery: string
}

export interface GroupedModules {
  [subject: string]: Module[]
}


