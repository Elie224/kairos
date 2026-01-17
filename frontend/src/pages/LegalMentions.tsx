/**
 * Page Mentions Légales - Conformité RGPD
 */
import { Box, Container, VStack, Heading, Text, Divider } from '@chakra-ui/react'

const LegalMentions = () => {
  return (
    <Box py={{ base: 8, md: 12 }} minH="80vh">
      <Container maxW="900px">
        <VStack spacing={8} align="stretch">
          <VStack spacing={4} align="start">
            <Heading size="2xl" color="gray.900" fontWeight="800">
              Mentions Légales
            </Heading>
            <Text color="gray.600" fontSize="sm">
              Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}
            </Text>
          </VStack>

          <Divider />

          <VStack spacing={6} align="stretch">
            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                1. Éditeur du site
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text><strong>Nom :</strong> Kaïrox</Text>
                <Text><strong>Description :</strong> Plateforme d'apprentissage immersive avec intelligence artificielle</Text>
                <Text><strong>Site web :</strong> https://kairos-frontend-hjg9.onrender.com</Text>
                <Text><strong>Email :</strong> support@kairos.education</Text>
                <Text><strong>Téléphone :</strong> +33 6 89 30 64 32</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                2. Directeur de publication
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Le directeur de publication est le représentant légal de Kaïrox.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                3. Hébergement
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text><strong>Hébergeur :</strong> Render</Text>
                <Text><strong>Adresse :</strong> Render.com</Text>
                <Text>Le site est hébergé sur les serveurs de Render, conformément aux normes de sécurité en vigueur.</Text>
              </VStack>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                4. Propriété intellectuelle
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                L'ensemble du contenu de ce site (textes, images, vidéos, logos, icônes, etc.) est la propriété exclusive de Kaïrox, sauf mention contraire.
              </Text>
              <Text color="gray.700" lineHeight="1.8">
                Toute reproduction, représentation, modification, publication, adaptation de tout ou partie des éléments du site, quel que soit le moyen ou le procédé utilisé, est interdite sans autorisation écrite préalable de Kaïrox.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                5. Protection des données personnelles
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Conformément au Règlement Général sur la Protection des Données (RGPD) et à la loi Informatique et Libertés, vous disposez d'un droit d'accès, de rectification, de suppression et d'opposition aux données personnelles vous concernant.
              </Text>
              <Text color="gray.700" lineHeight="1.8">
                Pour exercer ces droits, vous pouvez nous contacter à l'adresse : support@kairos.education
              </Text>
              <Text color="gray.700" lineHeight="1.8" mt={4}>
                Pour plus d'informations, consultez notre <strong>Politique de confidentialité</strong>.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                6. Cookies
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Ce site utilise des cookies pour améliorer l'expérience utilisateur et analyser le trafic. En continuant à naviguer sur ce site, vous acceptez l'utilisation de cookies conformément à notre politique de confidentialité.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                7. Responsabilité
              </Heading>
              <Text color="gray.700" lineHeight="1.8" mb={4}>
                Kaïrox s'efforce de fournir des informations exactes et à jour. Cependant, nous ne pouvons garantir l'exactitude, la complétude ou l'actualité des informations diffusées sur le site.
              </Text>
              <Text color="gray.700" lineHeight="1.8">
                L'utilisation du site se fait sous votre propre responsabilité. Kaïrox ne pourra être tenu responsable des dommages directs ou indirects résultant de l'utilisation du site.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                8. Liens externes
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Le site peut contenir des liens vers des sites externes. Kaïrox n'exerce aucun contrôle sur ces sites et décline toute responsabilité quant à leur contenu ou leur accessibilité.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                9. Droit applicable
              </Heading>
              <Text color="gray.700" lineHeight="1.8">
                Les présentes mentions légales sont régies par le droit français. Tout litige relatif à l'utilisation du site sera de la compétence exclusive des tribunaux français.
              </Text>
            </Box>

            <Divider />

            <Box>
              <Heading size="lg" color="gray.900" mb={4} fontWeight="700">
                10. Contact
              </Heading>
              <VStack spacing={2} align="start" color="gray.700" lineHeight="1.8">
                <Text>Pour toute question concernant les présentes mentions légales, vous pouvez nous contacter :</Text>
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

export default LegalMentions
