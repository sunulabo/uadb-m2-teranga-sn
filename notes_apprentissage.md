# Notes d'apprentissage — Teranga-SN
**NDIAYE Papa Malick | Eq.12**

Quelques réflexions personnelles au fil du développement.

---

## Semaine 1

### Pourquoi SHA-256 et pas juste supprimer le nom ?
Au départ je pensais qu'anonymiser = supprimer. Mais supprimer le `user_id`
complètement nous empêche de détecter si un même utilisateur revient plusieurs fois
(doublons, spam d'avis). SHA-256 + sel nous donne un identifiant stable mais
illisible : on peut compter les récurrences sans jamais connaître l'identité réelle.

### Ce qui m'a surpris dans Pandera
Je ne savais pas qu'on pouvait valider qu'une colonne **n'existe pas** dans un
DataFrame. C'est exactement ce dont on avait besoin pour vérifier que le PII
(`email_client`, `user_id`) a bien été supprimé avant d'écrire dans HBase.

### La saisonnalité sénégalaise
En explorant les données, j'ai réalisé que la haute saison touristique au Sénégal
(novembre-mars) coïncide avec l'hiver européen. C'est pour ça que le modèle Random
Forest utilise le mois comme feature — c'est la variable la plus prédictive.

### Watermark dans Spark Streaming
Sans watermark, Spark garde en mémoire l'état de **toutes** les fenêtres de temps
passées indéfiniment. Sur un flux long (24h/24), ça provoque un OutOfMemoryError.
Le watermark de `1 day` dit à Spark : "au-delà d'un jour de retard, ignore l'événement
et libère la mémoire de cette fenêtre."

---

## Questions à explorer en semaine 2
- Comment HBase gère-t-il les TTL ? Peut-on configurer une expiration automatique
  des alertes après 7 jours ?
- Est-ce que le lexique Wolof est suffisant ou faut-il ajouter des termes ?
- NiFi peut-il lire directement une API REST (TripAdvisor) ou faut-il passer par un
  script intermédiaire ?
