/**
 * Page Politique de Confidentialité - Conformité RGPD
 */
import { Box, Container, VStack, Heading, Text, Divider } from '@chakra-ui/react'
import { useEffect } from 'react'

const LegalPrivacy = () => {
  // S'assurer que la page se rend immédiatement
  useEffect(() => {
    // Scroll en haut au chargement
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [])

  return (
    <Box py={{ base: 8, md: 12 }} minH="80vh" w="100%">
      <Container maxW="900px">
        <VStack spacing={8} align="stretch">
          <VStack spacing={4} align="start">
            <Heading size="2xl" color="gray.900" fontWeight="800">
              Politique de Confidentialité
            </Heading>
            <Text color="gray.600" fontSize="sm">
              Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}
            </Text>
          </VStack>

          <Divider />

          <VStack spacing={6} align="stretch">
            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                1. Introduction
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Kaïrox ("nous", "notre", "nos") s'engage à protéger la confidentialité et la sécurité de vos données personnelles.
              </Text>
              <Text color="gray.700" lineHeight="1.8">
                Cette politique de confidentialité explique comment nous collectons, utilisons, stockons et protégeons vos informations personnelles conformément au Règlement Général sur la Protection des Données (RGPD) et à la loi Informatique et Libertés.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                2. Données collectées
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Nous collectons les données suivantes lorsque vous utilisez notre plateforme :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text><strong>Données d'identification :</strong> nom, prénom, nom d'utilisateur, adresse email</Text>
                <Text><strong>Données de contact :</strong> numéro de téléphone, pays</Text>
                <Text><strong>Données de connexion :</strong> adresse IP, logs de connexion, cookies</Text>
                <Text><strong>Données pédagogiques :</strong> progression, résultats aux quiz, historique d'apprentissage</Text>
                <Text><strong>Données de gamification :</strong> badges, points, quêtes, classements</Text>
                <Text><strong>Données de communication :</strong> messages échangés avec le tuteur IA, feedback</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                3. Finalités du traitement
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Nous utilisons vos données personnelles pour :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• Fournir et améliorer nos services d'apprentissage</Text>
                <Text>• Personnaliser votre expérience pédagogique</Text>
                <Text>• Générer des recommandations adaptées à votre niveau</Text>
                <Text>• Gérer votre compte et votre authentification</Text>
                <Text>• Analyser votre progression et vos performances</Text>
                <Text>• Vous contacter concernant votre compte ou nos services</Text>
                <Text>• Respecter nos obligations légales et réglementaires</Text>
                <Text>• Prévenir la fraude et assurer la sécurité de la plateforme</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                4. Base légale du traitement
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• <strong>Consentement :</strong> pour l'utilisation de cookies et le marketing</Text>
                <Text>• <strong>Exécution d'un contrat :</strong> pour la fourniture de nos services</Text>
                <Text>• <strong>Obligation légale :</strong> pour la conservation de certaines données</Text>
                <Text>• <strong>Intérêt légitime :</strong> pour l'amélioration de nos services et la sécurité</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                5. Conservation des données
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Nous conservons vos données personnelles :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• <strong>Pendant la durée de votre compte :</strong> tant que votre compte est actif</Text>
                <Text>• <strong>Après suppression du compte :</strong> 3 ans pour les données de facturation, conformément aux obligations légales</Text>
                <Text>• <strong>Données anonymisées :</strong> peuvent être conservées indéfiniment à des fins statistiques</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                6. Partage des données
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Nous ne vendons jamais vos données personnelles. Nous pouvons partager vos données avec :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• <strong>Prestataires de services :</strong> hébergement (Render), services d'IA (OpenAI), analytics</Text>
                <Text>• <strong>Autorités légales :</strong> si requis par la loi ou une ordonnance judiciaire</Text>
              </VStack>
              <Text color="gray.700" lineHeight="1.8" mt={4}>
                Tous nos prestataires sont soumis à des obligations strictes de confidentialité et de sécurité.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                7. Sécurité des données
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Nous mettons en œuvre des mesures techniques et organisationnelles appropriées pour protéger vos données :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• Chiffrement des données sensibles (mots de passe, communications)</Text>
                <Text>• Authentification sécurisée (HTTPS, tokens)</Text>
                <Text>• Accès restreint aux données personnelles</Text>
                <Text>• Surveillance et détection d'intrusions</Text>
                <Text>• Sauvegardes régulières</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                8. Vos droits
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Conformément au RGPD, vous disposez des droits suivants :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• <strong>Droit d'accès :</strong> obtenir une copie de vos données personnelles</Text>
                <Text>• <strong>Droit de rectification :</strong> corriger vos données inexactes</Text>
                <Text>• <strong>Droit à l'effacement :</strong> supprimer vos données ("droit à l'oubli")</Text>
                <Text>• <strong>Droit à la limitation :</strong> limiter le traitement de vos données</Text>
                <Text>• <strong>Droit à la portabilité :</strong> récupérer vos données dans un format structuré</Text>
                <Text>• <strong>Droit d'opposition :</strong> vous opposer au traitement de vos données</Text>
                <Text>• <strong>Droit de retirer votre consentement :</strong> à tout moment</Text>
              </VStack>
              <Text color="gray.700" lineHeight="1.8" mt={4}>
                Pour exercer ces droits, contactez-nous à : <strong>support@kairos.education</strong>
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                9. Cookies
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Nous utilisons des cookies pour :
              </Text>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>• Assurer le fonctionnement de la plateforme (cookies essentiels)</Text>
                <Text>• Mémoriser vos préférences (cookies de préférences)</Text>
                <Text>• Analyser l'utilisation du site (cookies analytiques)</Text>
              </VStack>
              <Text color="gray.700" lineHeight="1.8" mt={4}>
                Vous pouvez gérer vos préférences de cookies dans les paramètres de votre navigateur.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                10. Transferts internationaux
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Certaines de vos données peuvent être transférées vers des pays hors de l'Union Européenne (notamment pour les services d'IA). Ces transferts sont encadrés par des garanties appropriées conformes au RGPD.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                11. Modifications
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Nous pouvons modifier cette politique de confidentialité à tout moment. Les modifications seront publiées sur cette page avec une date de mise à jour. Nous vous encourageons à consulter régulièrement cette page.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                12. Contact
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>Pour toute question concernant cette politique de confidentialité ou vos données personnelles :</Text>
                <Text><strong>Email :</strong> support@kairos.education</Text>
                <Text><strong>Téléphone :</strong> +33 6 89 30 64 32</Text>
                <Text mt={4}>
                  Vous avez également le droit d'introduire une réclamation auprès de la CNIL (Commission Nationale de l'Informatique et des Libertés) si vous estimez que vos droits ne sont pas respectés.
                </Text>
              </VStack>
            </Box>
          </VStack>
        </VStack>
      </Container>
    </Box>
  )
}

export default LegalPrivacy
