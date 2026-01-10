/**
 * Utilitaire pour monitorer les performances des expériences immersives
 */
export class PerformanceMonitor {
  private fps: number = 0
  private frameCount: number = 0
  private lastTime: number = performance.now()
  private fpsHistory: number[] = []
  private memoryUsage: number = 0
  private isMonitoring: boolean = false

  startMonitoring() {
    this.isMonitoring = true
    this.monitor()
  }

  stopMonitoring() {
    this.isMonitoring = false
  }

  private monitor() {
    if (!this.isMonitoring) return

    const currentTime = performance.now()
    const deltaTime = currentTime - this.lastTime
    this.frameCount++

    if (deltaTime >= 1000) {
      this.fps = Math.round((this.frameCount * 1000) / deltaTime)
      this.fpsHistory.push(this.fps)
      
      // Garder seulement les 60 dernières valeurs
      if (this.fpsHistory.length > 60) {
        this.fpsHistory.shift()
      }

      this.frameCount = 0
      this.lastTime = currentTime

      // Vérifier l'utilisation mémoire si disponible
      if ('memory' in performance) {
        const memory = (performance as any).memory
        this.memoryUsage = Math.round(memory.usedJSHeapSize / 1048576) // MB
      }
    }

    requestAnimationFrame(() => this.monitor())
  }

  getFPS(): number {
    return this.fps
  }

  getAverageFPS(): number {
    if (this.fpsHistory.length === 0) return 0
    const sum = this.fpsHistory.reduce((a, b) => a + b, 0)
    return Math.round(sum / this.fpsHistory.length)
  }

  getMinFPS(): number {
    if (this.fpsHistory.length === 0) return 0
    return Math.min(...this.fpsHistory)
  }

  getMemoryUsage(): number {
    return this.memoryUsage
  }

  getStats() {
    return {
      currentFPS: this.fps,
      averageFPS: this.getAverageFPS(),
      minFPS: this.getMinFPS(),
      memoryUsageMB: this.memoryUsage,
      isHealthy: this.fps >= 30 && this.getMinFPS() >= 20
    }
  }

  reset() {
    this.fps = 0
    this.frameCount = 0
    this.fpsHistory = []
    this.memoryUsage = 0
    this.lastTime = performance.now()
  }
}

// Instance singleton
export const performanceMonitor = new PerformanceMonitor()
















