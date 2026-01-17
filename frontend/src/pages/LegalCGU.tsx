/**
 * Page Conditions Générales d'Utilisation (CGU)
 */
import { Box, Container, VStack, Heading, Text, Divider } from '@chakra-ui/react'
import { useEffect } from 'react'

const LegalCGU = () => {
  // S'assurer que la page se rend immédiatement
  useEffect(() => {
    const pathname = window.location.pathname
    // Scroll en haut au chargement
    window.scrollTo({ top: 0, behavior: 'instant' })
    // Logger pour déboguer
    console.log('✅ LegalCGU component mounted', { pathname, timestamp: new Date().toISOString() })
    // Vérifier qu'on est bien sur /legal/cgu
    if (pathname !== '/legal/cgu') {
      console.error('❌ ERREUR: LegalCGU component rendu sur une mauvaise route!', { pathname })
      // Si on n'est pas sur la bonne route, rediriger
      if (!pathname.startsWith('/legal')) {
        window.location.href = '/legal/cgu'
        return
      }
    }
  }, [])

  return (
    <Box py={{ base: 8, md: 12 }} minH="80vh" w="100%" bg="gray.50" px={{ base: 4, md: 6 }}>
      <Container maxW="900px" px={{ base: 4, md: 6 }}>
        <VStack spacing={8} align="stretch">
          <VStack spacing={4} align="start">
            <Heading size="2xl" color="gray.900" fontWeight="800">
              Conditions Générales d'Utilisation
            </Heading>
            <Text color="gray.600" fontSize="sm">
              Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}
            </Text>
          </VStack>

          <Divider />

          <VStack spacing={6} align="stretch">
            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                1. Objet
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Les présentes Conditions Générales d'Utilisation (CGU) régissent l'utilisation de la plateforme Kaïrox, une plateforme d'apprentissage immersive avec intelligence artificielle accessible à l'adresse https://kairos-frontend-hjg9.onrender.com.
              </Text>
              <Text color="gray.700" lineHeight="1.8" mt={4}>
                L'utilisation de la plateforme implique l'acceptation pleine et entière des présentes CGU.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                2. Acceptation des CGU
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                En créant un compte ou en utilisant la plateforme Kaïrox, vous reconnaissez avoir lu, compris et accepté les présentes CGU.
              </Text>
              <Text color="gray.700" lineHeight="1.8">
                Si vous n'acceptez pas ces conditions, vous ne devez pas utiliser la plateforme.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                3. Description du service
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Kaïrox est une plateforme éducative qui propose :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• Des modules d'apprentissage interactifs dans diverses matières (Mathématiques, Physique, Chimie, Informatique, etc.)</Text>
                <Text>• Des visualisations 2D/3D interactives générées par IA</Text>
                <Text>• Un tuteur IA pour l'assistance pédagogique</Text>
                <Text>• Un système de gamification (badges, quêtes, classements)</Text>
                <Text>• Des quiz et évaluations adaptatifs</Text>
                <Text>• Un suivi de progression personnalisé</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                4. Inscription et compte utilisateur
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text><strong>4.1 Création de compte</strong></Text>
                <Text>Pour utiliser la plateforme, vous devez créer un compte en fournissant des informations exactes et à jour.</Text>
                
                <Text mt={4}><strong>4.2 Responsabilité du compte</strong></Text>
                <Text>Vous êtes responsable de :</Text>
                <Text>• La confidentialité de vos identifiants de connexion</Text>
                <Text>• Toutes les activités effectuées sous votre compte</Text>
                <Text>• La notification immédiate de toute utilisation non autorisée</Text>
                
                <Text mt={4}><strong>4.3 Âge minimum</strong></Text>
                <Text>Vous devez avoir au moins 13 ans pour créer un compte. Les utilisateurs mineurs doivent obtenir l'autorisation de leurs parents ou tuteurs légaux.</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                5. Utilisation de la plateforme
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text><strong>5.1 Utilisation autorisée</strong></Text>
                <Text>Vous vous engagez à utiliser la plateforme uniquement à des fins légales et éducatives, conformément aux présentes CGU.</Text>
                
                <Text mt={4}><strong>5.2 Utilisations interdites</strong></Text>
                <Text>Il est strictement interdit de :</Text>
                <Text>• Utiliser la plateforme à des fins frauduleuses ou illégales</Text>
                <Text>• Tenter d'accéder à des zones non autorisées du système</Text>
                <Text>• Perturber ou nuire au fonctionnement de la plateforme</Text>
                <Text>• Transmettre des virus, malwares ou codes malveillants</Text>
                <Text>• Copier, reproduire ou revendre le contenu sans autorisation</Text>
                <Text>• Utiliser des robots, scripts automatisés ou outils de scraping</Text>
                <Text>• Harceler, menacer ou nuire à d'autres utilisateurs</Text>
                <Text>• Publier du contenu offensant, discriminatoire ou illégal</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                6. Propriété intellectuelle
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Tous les contenus de la plateforme (textes, images, vidéos, logiciels, bases de données, etc.) sont la propriété exclusive de Kaïrox ou de ses partenaires et sont protégés par les lois sur la propriété intellectuelle.
              </Text>
              <Text color="gray.700" lineHeight="1.8">
                L'utilisation de la plateforme ne vous confère aucun droit de propriété sur ces contenus. Toute reproduction, modification, distribution ou utilisation commerciale est strictement interdite sans autorisation écrite préalable.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                7. Contenu généré par l'utilisateur
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                En utilisant la plateforme, vous pouvez générer du contenu (questions, réponses, feedback, etc.). Vous conservez vos droits sur ce contenu, mais vous accordez à Kaïrox une licence non exclusive, mondiale, gratuite et perpétuelle pour :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• Utiliser, reproduire et modifier ce contenu sur la plateforme</Text>
                <Text>• Améliorer nos services et algorithmes d'IA</Text>
                <Text>• Analyser et générer des statistiques anonymisées</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                8. Disponibilité du service
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Kaïrox s'efforce d'assurer une disponibilité maximale de la plateforme. Cependant :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• Des interruptions peuvent survenir pour maintenance, mises à jour ou raisons techniques</Text>
                <Text>• Nous ne garantissons pas une disponibilité à 100%</Text>
                <Text>• Nous nous réservons le droit de modifier, suspendre ou interrompre le service à tout moment</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                9. Limitation de responsabilité
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Kaïrox ne pourra être tenu responsable de :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• Les dommages directs ou indirects résultant de l'utilisation ou de l'impossibilité d'utiliser la plateforme</Text>
                <Text>• La perte de données, de profits ou d'opportunités</Text>
                <Text>• Les erreurs, inexactitudes ou omissions dans le contenu</Text>
                <Text>• Les interruptions de service ou problèmes techniques</Text>
                <Text>• Les actions de tiers ou utilisateurs non autorisés</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                10. Résiliation
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text><strong>10.1 Par l'utilisateur</strong></Text>
                <Text>Vous pouvez supprimer votre compte à tout moment depuis les paramètres de votre profil.</Text>
                
                <Text mt={4}><strong>10.2 Par Kaïrox</strong></Text>
                <Text>Nous nous réservons le droit de suspendre ou supprimer votre compte en cas de :</Text>
                <Text>• Violation des présentes CGU</Text>
                <Text>• Activité frauduleuse ou suspecte</Text>
                <Text>• Inactivité prolongée (plus de 2 ans)</Text>
                <Text>• Demande des autorités compétentes</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                11. Modifications des CGU
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Kaïrox se réserve le droit de modifier les présentes CGU à tout moment. Les modifications seront publiées sur cette page avec une date de mise à jour. Votre utilisation continue de la plateforme après publication des modifications vaut acceptation des nouvelles CGU.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                12. Droit applicable et juridiction
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Les présentes CGU sont régies par le droit français. Tout litige relatif à leur interprétation ou à leur exécution relève de la compétence exclusive des tribunaux français.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                13. Contact
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>Pour toute question concernant les présentes CGU :</Text>
                <Text><strong>Email :</strong> support@kairos.education</Text>
                <Text><strong>Téléphone :</strong> +33 6 89 30 64 32</Text>
              </VStack>
            </Box>
          </VStack>
        </VStack>
      </Container>
    </Box>
  )
}

export default LegalCGU
