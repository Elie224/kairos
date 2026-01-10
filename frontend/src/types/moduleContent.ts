/**
 * Types TypeScript stricts pour le contenu des modules
 */

export interface Lesson {
  title: string
  content?: string  // Optionnel maintenant, car le contenu vient des ressources
  summary?: string  // Résumé/description de la leçon
  resource_ids?: string[]  // IDs des ressources associées à cette leçon
  sections?: Section[]
  order?: number
}

export interface Section {
  title?: string
  content?: string
  heading?: string
  paragraphs?: string[]
  bulletPoints?: string[]
  type?: 'text' | 'image' | 'video' | 'interactive'
  order?: number
}

export type SceneType = 
  | 'gravitation' 
  | 'geometric_shapes' 
  | 'chemical_reaction'
  | 'english_grammar'
  | 'mechanics'
  | 'default'

export interface ModuleContent {
  scene?: SceneType
  lessons?: Lesson[]
  text?: string
  // Propriétés additionnelles pour différents types de contenu
  [key: string]: unknown
}

