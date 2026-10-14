# McDo Radar — veille éditoriale

**Site public :** https://camillegasch-web.github.io/mcdo-radar/

Radar quotidien McDonald's France : actualités nationales, locales, recrutement et marque employeur McDo, concurrence (Burger King, KFC, Quick et Five Guys), signaux sensibles, inspirations RH et campagnes de recrutement intersectorielles.

## Comment ça marche ?

- **Chaque jour :** GitHub Actions consulte des recherches Google Actualités en français (RSS), conserve un historique de 90 jours et met à jour les articles du radar.
- **Dans le radar :** choisissez une rubrique, filtrez par mots-clés et période, ajoutez des articles au panier newsletter, puis copiez votre sélection.
- **Pour un article :** « Lire l’article » ouvre sa source. Vérifiez les informations avant de les reprendre dans une newsletter.
- **Signaux sensibles :** ce sont des titres repérés automatiquement ; un signal n'est pas une information vérifiée sur la réputation de la marque.

Les données sont conservées dans `docs/data/news.json` et `docs/data/news.js`.
Le script est `scripts/update_news.py` et son exécution est planifiée par `.github/workflows/veille-quotidienne.yml`, vers 8h15 (heure d’hiver) ou 9h15 (heure d’été) à Paris, sans garantie d’horaire exact.

**Vérifier les mises à jour :** https://github.com/camillegasch-web/mcdo-radar/actions
**Configurer l'hébergement :** https://github.com/camillegasch-web/mcdo-radar/settings/pages (Source : GitHub Actions).

La collecte est distincte de la publication : une indisponibilité de GitHub Pages ne bloque pas les données. Le radar ne constitue ni un outil exhaustif de surveillance médias, ni une analyse automatique de sentiment. Il ne couvre pas les articles payants ou les publications privées sur les réseaux sociaux.
