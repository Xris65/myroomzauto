# MyRoomzAuto

Outil d'automatisation pour la réservation de bureaux sur **MyRoomz**. Ce projet intègre une gestion intelligente de la rotation des jetons pour garantir une exécution fluide sans intervention manuelle. Maximum testé (lancement 3x par semaine) sans intervention : 2 mois.

## 🚀 Fonctionnement
Le script effectue les étapes suivantes à chaque exécution :
1. **Authentification** : Utilisation du `Reset Token` (`MY_API_KEY`) actuel.
2. **Réservation** : Effectue la réservation pour le `WORKSPACE_ID` cible situé sur l'`FLOOR_ID`.
3. **Rotation du Token** : Récupération du nouveau jeton renvoyé par l'API (nécessaire car le jeton est à usage unique).
4. **Mise à jour automatique** : Utilisation du `GH_PAT` pour mettre à jour directement le secret GitHub `MY_API_KEY` afin que le prochain cycle soit déjà authentifié.

## ⚙️ Configuration (Secrets)

Pour configurer le projet, ajoute les variables suivantes dans tes **GitHub Secrets** (`Settings` > `Secrets and variables` > `Actions`) :

| Variable | Description |
| :--- | :--- |
| `MY_API_KEY` | *Reset Token* initial (récupéré via l'onglet *Network* de ton navigateur sur la requête /token juste après l'authentification sur myroomz). |
| `WORKSPACE_ID` | Identifiant du bureau à réserver. |
| `FLOOR_ID` | Identifiant de l'étage correspondant. |
| `GH_PAT` | *GitHub Personal Access Token* (nécessaire pour la mise à jour automatique des secrets). |

## 🛠 Paramétrage requis

### 1. Code source (`main.py`)
Assure-toi que ton script pointe correctement vers ton dépôt pour permettre la mise à jour des secrets. Il faudrait mettre à jour la ligne suivante dans le script **auto_reservation.py** :
```python
repo = "Xris65/myroomzauto" # Format: "pseudo/nom-du-depot"

### 2. Planification (.github/workflows/main.yml)
Modifie la section cron (utiliser [crowntab guru](https://crontab.guru) si pas habitué avec les cron) dans ton workflow pour définir la fréquence d'exécution (en heure UTC) :

on:
  schedule:
    - cron: '0 6 * * *' # Exemple : tous les jours à 06h00 UTC

## 🔒 Sécurité
Ce dépôt manipule des clés d'accès et un jeton GitHub (`GH_PAT`) ayant des droits d'écriture sur tes secrets. 
* **Utiliser des secrets** : Bien faire attention à utiliser des secrets et non pas des variables !
* **Permissions du PAT** : Assure-toi que ton jeton GitHub possède les permissions minimales requises pour modifier les secrets (`repo` ou accès spécifique aux secrets).
