# RBean 2600

Parse le RBean de 2600 pour récupérer les notes de chaque projet et afficher des stats.

## Installation des dépendances

```bash
python3 -m pip install -Ur requirements.txt
```

## Utilisation

### Configuration

Éditer le fichier `.env` pour configurer les paramètres de connexion.

```bash
# .env
LOGIN="<prenom.nom>@ecole2600.com"
PASSWORD="<XXXX>"
```

### Récupération des notes

Crée un fichier `skills.json` contenant les notes de chaque projet.

```bash
python3 get_rbean_skills.py
```

### Affichage des stats

Charges les données depuis `skills.json` et calcule les totaux/pourcentages pour chaque projet.

```bash
python3 analyze.py
```
