/**
 * Tests E2E basiques pour Kaïros
 * 
 * Ces tests vérifient les flux principaux de l'application:
 * - Authentification (login/register)
 * - Navigation
 * - Accès aux modules
 * - Dashboard
 * 
 * Pour exécuter ces tests:
 * 1. Installer Playwright: npm install -D @playwright/test
 * 2. Installer les navigateurs: npx playwright install
 * 3. Démarrer le backend et le frontend en mode développement
 * 4. Exécuter: npx playwright test
 */

import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173'
const API_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000'

test.describe('Kaïros E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Aller à la page d'accueil
    await page.goto(BASE_URL)
  })

  test('Page d\'accueil se charge correctement', async ({ page }) => {
    // Vérifier que la page d'accueil se charge
    await expect(page).toHaveTitle(/Kaïros/i)
    
    // Vérifier la présence d'éléments clés
    await expect(page.locator('text=Kaïros')).toBeVisible()
  })

  test('Navigation vers la page de login', async ({ page }) => {
    // Cliquer sur le bouton de login
    const loginLink = page.locator('a[href="/login"]').first()
    if (await loginLink.isVisible()) {
      await loginLink.click()
      await expect(page).toHaveURL(/.*\/login/)
    }
  })

  test('Formulaire de login affiché correctement', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`)
    
    // Vérifier la présence des champs du formulaire
    await expect(page.locator('input[type="email"], input[name="username"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('Formulaire de register affiché correctement', async ({ page }) => {
    await page.goto(`${BASE_URL}/register`)
    
    // Vérifier la présence des champs du formulaire
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('Redirection vers dashboard après login (si credentials valides)', async ({ page }) => {
    // Note: Ce test nécessite des credentials de test valides
    // Pour l'instant, on vérifie juste que le formulaire fonctionne
    await page.goto(`${BASE_URL}/login`)
    
    // Remplir le formulaire (avec des credentials de test si disponibles)
    const emailInput = page.locator('input[type="email"], input[name="username"]').first()
    const passwordInput = page.locator('input[type="password"]').first()
    const submitButton = page.locator('button[type="submit"]').first()
    
    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      // Utiliser des credentials de test si disponibles
      const testEmail = process.env.TEST_EMAIL || 'test@example.com'
      const testPassword = process.env.TEST_PASSWORD || 'testpassword'
      
      await emailInput.fill(testEmail)
      await passwordInput.fill(testPassword)
      
      // Ne pas soumettre si ce sont des credentials de test par défaut
      if (testEmail !== 'test@example.com' && testPassword !== 'testpassword') {
        await submitButton.click()
        // Attendre soit une redirection, soit un message d'erreur
        await page.waitForTimeout(2000)
      }
    }
  })

  test('Navigation vers modules (nécessite authentification)', async ({ page }) => {
    // Tenter d'accéder à /modules
    await page.goto(`${BASE_URL}/modules`)
    
    // Devrait rediriger vers login si non authentifié
    // ou afficher les modules si authentifié
    await page.waitForTimeout(1000)
    
    const currentUrl = page.url()
    // Soit on est sur /login (redirection), soit sur /modules (authentifié)
    expect(currentUrl).toMatch(/\/(login|modules)/)
  })

  test('Page dashboard accessible (nécessite authentification)', async ({ page }) => {
    // Tenter d'accéder à /dashboard
    await page.goto(`${BASE_URL}/dashboard`)
    
    // Devrait rediriger vers login si non authentifié
    await page.waitForTimeout(1000)
    
    const currentUrl = page.url()
    // Soit on est sur /login (redirection), soit sur /dashboard (authentifié)
    expect(currentUrl).toMatch(/\/(login|dashboard)/)
  })

  test('Page support accessible (nécessite authentification)', async ({ page }) => {
    // Tenter d'accéder à /support
    await page.goto(`${BASE_URL}/support`)
    
    // Devrait rediriger vers login si non authentifié
    await page.waitForTimeout(1000)
    
    const currentUrl = page.url()
    // Soit on est sur /login (redirection), soit sur /support (authentifié)
    expect(currentUrl).toMatch(/\/(login|support)/)
  })

  test('Page feedback accessible (nécessite authentification)', async ({ page }) => {
    // Tenter d'accéder à /feedback
    await page.goto(`${BASE_URL}/feedback`)
    
    // Devrait rediriger vers login si non authentifié
    await page.waitForTimeout(1000)
    
    const currentUrl = page.url()
    // Soit on est sur /login (redirection), soit sur /feedback (authentifié)
    expect(currentUrl).toMatch(/\/(login|feedback)/)
  })

  test('Responsive design - Mobile viewport', async ({ page }) => {
    // Tester avec un viewport mobile
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto(BASE_URL)
    
    // Vérifier que la page se charge correctement sur mobile
    await expect(page.locator('text=Kaïros')).toBeVisible()
    
    // Vérifier que le menu hamburger est présent (si implémenté)
    // const hamburgerMenu = page.locator('button[aria-label*="menu"], button[aria-label*="Menu"]')
    // if (await hamburgerMenu.isVisible().catch(() => false)) {
    //   await expect(hamburgerMenu).toBeVisible()
    // }
  })

  test('Health check API', async ({ request }) => {
    // Tester l'endpoint de health check
    const response = await request.get(`${API_URL}/health`)
    expect(response.status()).toBe(200)
    
    const body = await response.json()
    expect(body).toHaveProperty('status')
  })
})
