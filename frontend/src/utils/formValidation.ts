/**
 * Utilitaires de validation de formulaire
 */

export interface ValidationResult {
  isValid: boolean
  error?: string
}

/**
 * Valide un email
 */
export function validateEmail(email: string): ValidationResult {
  if (!email) {
    return { isValid: false, error: 'L\'email est requis' }
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Format d\'email invalide' }
  }

  return { isValid: true }
}

/**
 * Valide un nom d'utilisateur
 */
export function validateUsername(username: string): ValidationResult {
  if (!username) {
    return { isValid: false, error: 'Le nom d\'utilisateur est requis' }
  }

  if (username.length < 3) {
    return { isValid: false, error: 'Le nom d\'utilisateur doit contenir au moins 3 caractères' }
  }

  if (username.length > 20) {
    return { isValid: false, error: 'Le nom d\'utilisateur ne peut pas dépasser 20 caractères' }
  }

  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return { isValid: false, error: 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscores' }
  }

  return { isValid: true }
}

/**
 * Valide un mot de passe
 */
export function validatePassword(password: string): ValidationResult {
  if (!password) {
    return { isValid: false, error: 'Le mot de passe est requis' }
  }

  if (password.length < 6) {
    return { isValid: false, error: 'Le mot de passe doit contenir au moins 6 caractères' }
  }

  if (password.length > 128) {
    return { isValid: false, error: 'Le mot de passe ne peut pas dépasser 128 caractères' }
  }

  return { isValid: true }
}

/**
 * Valide la confirmation du mot de passe
 */
export function validatePasswordConfirmation(password: string, confirmPassword: string): ValidationResult {
  if (!confirmPassword) {
    return { isValid: false, error: 'Veuillez confirmer votre mot de passe' }
  }

  if (password !== confirmPassword) {
    return { isValid: false, error: 'Les mots de passe ne correspondent pas' }
  }

  return { isValid: true }
}

/**
 * Valide un numéro de téléphone
 */
export function validatePhone(phone: string): ValidationResult {
  if (!phone) {
    return { isValid: true } // Optionnel
  }

  const cleanedPhone = phone.replace(/[\s\-\(\)]/g, '')
  const internationalFormat = /^\+[1-9]\d{9,14}$/.test(cleanedPhone)
  const frenchFormat = /^0[1-9]\d{8}$/.test(cleanedPhone)

  if (!internationalFormat && !frenchFormat) {
    return { isValid: false, error: 'Format invalide. Utilisez +33 6 12 34 56 78 ou 0612345678' }
  }

  return { isValid: true }
}

/**
 * Valide un nom (prénom ou nom de famille)
 */
export function validateName(name: string, fieldName: string = 'nom'): ValidationResult {
  if (!name) {
    return { isValid: true } // Optionnel
  }

  if (name.length < 2) {
    return { isValid: false, error: `Le ${fieldName} doit contenir au moins 2 caractères` }
  }

  if (name.length > 50) {
    return { isValid: false, error: `Le ${fieldName} ne peut pas dépasser 50 caractères` }
  }

  if (!/^[a-zA-ZÀ-ÿ\s'-]+$/.test(name)) {
    return { isValid: false, error: `Le ${fieldName} ne peut contenir que des lettres, espaces, tirets et apostrophes` }
  }

  return { isValid: true }
}
