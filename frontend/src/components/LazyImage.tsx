/**
 * Composant d'image avec lazy loading optimisé
 */
import { useState, useEffect, useRef } from 'react'
import { Image, ImageProps, Skeleton, Box } from '@chakra-ui/react'

interface LazyImageProps extends ImageProps {
  src: string
  alt: string
  placeholder?: string
}

export const LazyImage = ({ src, alt, placeholder, ...props }: LazyImageProps) => {
  const [imageSrc, setImageSrc] = useState<string>(src)
  const [isLoaded, setIsLoaded] = useState(false)
  const [isInView, setIsInView] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Intersection Observer pour détecter quand l'image entre dans le viewport
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true)
            observer.disconnect()
          }
        })
      },
      {
        rootMargin: '50px', // Commencer à charger 50px avant que l'image soit visible
        threshold: 0.01, // Déclencher dès qu'un pixel est visible
      }
    )

    const currentRef = containerRef.current
    if (currentRef) {
      observer.observe(currentRef)
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef)
      }
      observer.disconnect()
    }
  }, [])

  useEffect(() => {
    if (isInView && !isLoaded) {
      const img = new window.Image()
      img.src = src
      img.onload = () => {
        setImageSrc(src)
        setIsLoaded(true)
      }
      img.onerror = () => {
        // En cas d'erreur, utiliser le src original
        setIsLoaded(true)
      }
    }
  }, [isInView, src, isLoaded])

  // Si l'image est déjà dans le viewport au chargement, charger immédiatement
  useEffect(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect()
      const isVisible = rect.top < window.innerHeight + 50 && rect.bottom > -50
      if (isVisible && !isInView) {
        setIsInView(true)
      }
    }
  }, [])

  if (!isLoaded && !isInView) {
    return (
      <Box ref={containerRef} display="inline-block" {...props}>
        <Skeleton 
          height={props.height || '200px'} 
          width={props.width || '100%'} 
          borderRadius={props.borderRadius}
        />
      </Box>
    )
  }

  return (
    <Box ref={containerRef} display="inline-block">
      <Image
        src={imageSrc}
        alt={alt}
        loading="lazy"
        {...props}
      />
    </Box>
  )
}
