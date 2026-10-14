# McDo Radar — veille quotidienne créative, RH et McDonald's

**Site public :** https://camillegasch-web.github.io/mcdo-radar/

## Contenu

- **France** — actualités de McDonald's France et de sa communication.
- **Local** — restaurants, franchises, recrutements et presse régionale.
- **RH McDo** — emplois, managers, formation, alternance et conditions de travail.
- **Concurrence** — Burger King, KFC, Quick et Five Guys.
- **Inspiration RH** — campagnes de recrutement, image employeur, tendances RH, études, expérience candidat, marque employeur dans tous les secteurs.
- **Campagnes créatives** — publicité, activations de marques, affichage, films, campagnes social media, tendances et idées de communication de tous secteurs.
- **Signaux sensibles** — retombées potentiellement sensibles, à vérifier humainement.
- **Sources suivies** — catalogue des médias spécialisés interrogés.
- **Ma sélection newsletter** — articles choisis et copiables avec leur date, leur média et le lien source.

## Médias ciblés

**Créa / publicité :** Creapills, L'ADN, Dans Ta Pub (fondé par Gabriel Teisson), Stratégies, CB News, J'ai un pote dans la com, La Réclame, INfluencia, Marketing Magazine, Les Gens d'Internet, Blog du Modérateur, Siècle Digital, The Drum, Adweek, Campaign.

**RH / emploi :** HelloWorkplace / HelloWork, Culture RH, Parlons RH, myRHline, Focus RH, RH Matin, Welcome to the Jungle, ANDRH, Apec, Liaisons Sociales, Courrier Cadres.

**LinkedIn :** recherches ciblées sur les publications **publiques éventuellement indexées**, notamment Gabriel Teisson et Dans Ta Pub. Un fil LinkedIn personnel, privé ou non indexé ne peut pas être suivi de façon exhaustive avec ce dispositif.

Ces médias sont ciblés par recherche Google Actualités avec filtre de domaine, ou par RSS direct quand celui-ci est disponible. **Cibler une source ne signifie pas que toutes ses publications sont récupérées** ; certains sites ne publient pas de flux ou bloquent la collecte automatisée.

## Collecte et publication

- GitHub Actions lance `scripts/update_news.py` chaque jour à **07:15 UTC**, soit environ **08:15 (hiver)** et **09:15 (été)** en France. Les horaires GitHub Actions ne sont pas garantis.
- Les résultats publics sont sauvegardés dans `docs/data/news.json` et `docs/data/news.js` sur une fenêtre maximale de **180 jours** (2300 articles maximum).
- Les données sont organisées par rubrique ; une campagne créative de recrutement peut se retrouver dans les rubriques **Campagnes créatives** et **Inspiration RH**.
- La page de collecte indique le nombre de requêtes disponibles et la dernière mise à jour.
- Le site est publié via GitHub Pages à chaque collecte réussie.
- Pour vérifier les exécutions : https://github.com/camillegasch-web/mcdo-radar/actions
- Pour configurer le site : https://github.com/camillegasch-web/mcdo-radar/settings/pages (source GitHub Actions).
- Les favoris sont conservés uniquement dans le navigateur où ils ont été choisis.

**Limites :** cette veille est large mais non exhaustive : elle n'inclut pas tous les abonnements presse, toutes les publications des plateformes sociales, les articles protégés par paywall ou les messages privés. Les titres et dates sont fournis par les flux ; lire et vérifier les articles avant de les utiliser dans une newsletter ou une recommandation. Le classement est automatisé, pas éditorialisé par un journaliste.
