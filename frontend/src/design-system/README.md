# Kaïrox Design System

## Vue d'ensemble

Le design system de Kaïrox est conçu pour créer une expérience utilisateur cohérente et professionnelle à travers toute l'application.

## Tokens de Design

### Couleurs

Les couleurs sont automatiquement extraites du logo et génèrent des palettes complètes :

- **Brand** : Couleur principale du logo (50-900)
- **Secondary** : Couleur secondaire du logo
- **Accent** : Couleur d'accent du logo

### Espacements

```typescript
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 48px
3xl: 64px
```

### Typographie

- **Font Family** : Inter (système)
- **Tailles** : xs (12px) à 6xl (60px)
- **Poids** : 100 (hairline) à 900 (black)
- **Line Heights** : none (1) à loose (2)

### Ombres

- **xs** à **2xl** : Ombres standards
- **glow** : Effet de lueur
- **inner** : Ombre interne

### Transitions

- **fast** : 150ms
- **base** : 250ms
- **slow** : 350ms
- **bounce** : 500ms avec effet rebond

## Composants

### AnimatedBox

Composant Box avec animations intégrées.

```tsx
<AnimatedBox animation="fadeInUp" delay={0.2}>
  {children}
</AnimatedBox>
```

### PageSection

Section de page avec variantes prédéfinies.

```tsx
<PageSection variant="gradient" py={{ base: 12, md: 20 }}>
  {content}
</PageSection>
```

### FeatureCard

Carte de fonctionnalité avec icône et description.

```tsx
<FeatureCard
  icon={FiEye}
  title="Titre"
  description="Description"
  delay={0.1}
/>
```

### StatCard

Carte de statistique avec valeur et label.

```tsx
<StatCard
  icon={FiUsers}
  value="100K+"
  label="Utilisateurs"
  delay={0.2}
/>
```

## Animations

Toutes les animations sont optimisées pour la performance :

- Utilisation de `will-change` pour l'accélération GPU
- Transitions avec `cubic-bezier` pour des mouvements naturels
- Support des préférences de réduction de mouvement

## Accessibilité

- Contraste de couleurs conforme WCAG AA
- Tailles de touch minimales (44px)
- Focus visible pour la navigation clavier
- Support des lecteurs d'écran

## Responsive Design

Breakpoints :
- **base** : 0px (Mobile)
- **sm** : 480px (Grand mobile)
- **md** : 768px (Tablette)
- **lg** : 992px (Desktop)
- **xl** : 1280px (Grand desktop)
- **2xl** : 1536px (Très grand desktop)

## Bonnes Pratiques

1. **Utiliser les tokens** : Toujours utiliser les tokens du design system plutôt que des valeurs codées en dur
2. **Animations subtiles** : Les animations doivent améliorer l'expérience sans distraire
3. **Cohérence** : Utiliser les mêmes espacements, couleurs et typographie partout
4. **Performance** : Optimiser les animations pour les appareils mobiles
5. **Accessibilité** : Toujours considérer l'accessibilité lors de la création de composants

