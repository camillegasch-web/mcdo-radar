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


## Version « Sélection éditoriale & Podcasts » (octobre 2026)

Le radar permet d'utiliser cinq **filtres éditoriaux** indépendants des rubriques : « Toutes les actualités », « À mettre dans ma newsletter », « Campagnes inspirantes », « Chiffres & études RH » et « Impact potentiel pour McDo ».

La pertinence automatique est **indicative** : les scores /100 et les angles proposés sont des heuristiques calculées uniquement sur le titre, la rubrique, la date et le média. Le radar **ne lit pas le contenu intégral** et les scores ne mesurent ni véracité ni qualité journalistique. Les suggestions ne doivent être utilisées dans une newsletter qu'après vérification des sources.

Le classement des médias est en trois niveaux (priorité 1 = cœur des sujets McDo/RH/créa ; 2 = inspirations adjacentes ; 3 = veille complémentaire), et non un classement de fiabilité. Pour chaque article, le radar affiche sa priorité de source et une justification.

### Sources supplémentaires

- Restauration & franchise : France Snacking, L’Express Franchise, L’Hôtellerie Restauration, Le Journal des Entreprises, actu.fr, ici, LSA.
- Publicité et campagnes : Little Black Book, Marketing Dive, Creative Boom, Digiday, Social Media Today, Ads of the World, Cannes Lions.
- RH et travail : Maddyness, LinkedIn Talent Solutions, Dares, France Travail, Great Place To Work et ChooseMyCompany.
- Local : la collecte nationale complète toujours ces recherches avec la presse locale accessible dans Google Actualités.

### Podcasts & interviews

Le nouvel onglet « Podcasts & interviews » collecte des épisodes **publiés et datés** depuis les flux RSS publics des émissions retrouvées dans le répertoire Apple Podcasts : Passion DRH, Bougeons les lignes (si accessible), Le Super Daily, Le Talk Franchise, En toute franchise, Génération Do It Yourself et Marketing Mania. Les podcasts que le répertoire ne retrouve pas ou dont le RSS ne répond pas ne sont pas inventés ; ils apparaissent dans les erreurs de collecte. Des articles podcast de Parlons RH peuvent également être affichés quand le titre et le lien montrent qu'il s'agit d'un épisode.

**Limites :** l'accès à Spotify privé, à l'ensemble des épisodes historiques ou à des émissions non indexées n'est pas assuré. Le système renvoie vers les pages des épisodes plutôt que de télécharger leur audio.
