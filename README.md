# Exercia Blog — Setup Vercel

Blog statique Astro pour blog.exercia.org

## Structure

```
src/
  layouts/
    Layout.astro          # Layout global (nav + footer)
    ArticleLayout.astro   # Layout article de blog
  pages/
    index.astro           # Page d'accueil du blog
    reforme-crpe-2026-bac3.astro
    exercices-maths-crpe-themes-les-plus-tombes.astro
    preparer-crpe-reconversion-3-mois.astro
    crpe-epreuve-application-arts-plastiques.astro
    crpe-epreuve-application-choisir-discipline.astro
    crpe-francais-fautes-orthographe.astro
public/
  robots.txt
```

## Déploiement sur Vercel

### 1. Importer le projet
- Va sur vercel.com → "Add New Project"
- Importe ce repo depuis GitHub
- Vercel détecte automatiquement Astro

### 2. Variables d'environnement
Aucune variable d'environnement requise.

### 3. Configurer le domaine
- Dans Vercel → Settings → Domains
- Ajoute : blog.exercia.org

### 4. Configurer OVH DNS
Dans OVH → Zone DNS → Ajouter une entrée :
```
Type : CNAME
Sous-domaine : blog
Cible : cname.vercel-dns.com
TTL : Par défaut
```

## Ajouter un nouvel article

1. Crée un fichier `src/pages/mon-article.astro`
2. Utilise le layout ArticleLayout avec les props :
   - title
   - description  
   - pubDate (format: "2026-03-12")
   - category
   - readTime
3. Ajoute l'article dans le tableau `articles` dans `src/pages/index.astro`
4. Déploie (push sur GitHub → Vercel déploie automatiquement)

## Développement local

```bash
npm install
npm run dev
```
