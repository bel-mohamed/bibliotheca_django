# Bibliothèque - Système de Gestion de Bibliothèque

Un système complet de gestion de bibliothèque développé avec Django, conçu pour gérer efficacement les emprunts de livres, les utilisateurs et les pénalités.

## 🚀 Fonctionnalités

### 📚 Gestion des Livres
- **Ajout/Modification/Suppression** de livres
- **Recherche avancée** avec filtres (titre, auteur, catégorie, langue)
- **Gestion des exemplaires** (total et disponibles)
- **Support des images** de couverture
- **Gestion des auteurs** et des catégories

### 👥 Gestion des Utilisateurs
- **Deux rôles** : Bibliothécaire et Membre
- **Inscription en ligne** pour les nouveaux membres
- **Profils personnalisés** avec informations de contact
- **Authentification sécurisée**

### 📖 Gestion des Emprunts
- **Emprunt de livres** (limite de 5 par utilisateur)
- **Durée de 14 jours** par défaut
- **Suivi des retards** et calcul automatique des pénalités
- **Historique complet** des emprunts

### 💰 Système de Pénalités
- **Calcul automatique** : 0.50€ par jour de retard
- **Suivi des pénalités** payées et en attente
- **Gestion des paiements** par les bibliothécaires

### 📊 Tableaux de Bord
- **Pour les bibliothécaires** : statistiques complètes, rapports
- **Pour les membres** : emprunts actifs, réservations, pénalités
- **Rapports** : livres en retard, livres populaires, membres actifs

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Django 6.0+
- SQLite (base de données par défaut)

### Étapes d'installation

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd bibliotheca_project
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

6. **Démarrer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

7. **Accéder à l'application**
   - URL principale : http://127.0.0.1:8000/
   - Administration : http://127.0.0.1:8000/admin/

## 📁 Structure du Projet

```
bibliotheca_project/
├── bibliotheca_project/          # Configuration du projet
│   ├── __init__.py
│   ├── settings.py              # Paramètres Django
│   ├── urls.py                 # URLs principales
│   └── wsgi.py
├── library/                      # Application principale
│   ├── models.py                # Modèles de données
│   ├── views.py                 # Vues et logique métier
│   ├── forms.py                 # Formulaires
│   ├── urls.py                 # URLs de l'application
│   ├── admin.py                 # Administration Django
│   ├── tests.py                 # Tests unitaires
│   └── templates/
│       └── library/
│           ├── base.html         # Template de base
│           ├── home.html         # Page d'accueil
│           ├── login.html        # Page de connexion
│           ├── register.html     # Page d'inscription
│           ├── librarian/       # Templates bibliothécaire
│           └── member/          # Templates membre
├── static/                       # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
├── media/                        # Fichiers uploadés
│   └── book_covers/
├── manage.py                     # Script de gestion Django
└── db.sqlite3                   # Base de données SQLite
```

## 🔧 Configuration

### Variables d'environnement
Créer un fichier `.env` à la racine du projet :

```env
DEBUG=True
SECRET_KEY=votre-clé-secrète-ici
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Paramètres personnalisables (settings.py)
- `DEFAULT_BORROWING_DAYS` : Durée par défaut des emprunts (14 jours)
- `MAX_BORROWINGS_PER_USER` : Limite d'emprunts par utilisateur (5)
- `PENALTY_RATE_PER_DAY` : Taux de pénalité par jour (0.50€)

## 👤 Rôles et Permissions

### Bibliothécaire
- ✅ Gérer les livres (CRUD)
- ✅ Gérer les auteurs et catégories
- ✅ Gérer les utilisateurs
- ✅ Gérer tous les emprunts
- ✅ Gérer les pénalités
- ✅ Accéder aux rapports

### Membre
- ✅ Rechercher des livres
- ✅ Emprunter des livres (max 5)
- ✅ Réserver des livres indisponibles
- ✅ Consulter ses emprunts
- ✅ Retourner des livres
- ✅ Voir ses pénalités
- ✅ Gérer son profil

## 🧪 Tests

### Exécuter les tests
```bash
# Exécuter tous les tests
python manage.py test

# Exécuter les tests avec couverture
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Couverture de tests
- **Modèles** : Tests complets pour tous les modèles
- **Vues** : Tests pour toutes les fonctionnalités principales
- **Formulaires** : Tests de validation
- **Performance** : Tests de temps de réponse (< 2 secondes)

## 📊 Critères d'Acceptation

✅ **CA-01** : Toutes les exigences fonctionnelles prioritaires implémentées et testées
✅ **CA-02** : Tests unitaires couvrant au moins 70% du code source
✅ **CA-03** : Calcul correct des pénalités de retard dans 100% des cas testés
✅ **CA-04** : Recherches de livres retournant des résultats corrects en moins de 2 secondes
✅ **CA-05** : Aucune donnée utilisateur perdue en cas d'interruption normale du programme
✅ **CA-06** : Documentation technique complète et à jour (docstrings + README)
✅ **CA-07** : Diagrammes UML cohérents avec le code
✅ **CA-08** : Système fonctionnant sans erreur sur au moins deux plateformes différentes

## 🎯 Performance

### Optimisations implémentées
- **Recherche optimisée** avec `select_related` et `prefetch_related`
- **Pagination** pour gérer de grands volumes de données
- **Indexation** appropriée des champs de recherche
- **Cache** des requêtes fréquentes

### Exigences respectées
- ⏱️ **Temps de réponse** : < 2 secondes pour les recherches
- 📈 **Scalabilité** : Architecture modulaire et évolutive
- 🔒 **Sécurité** : Protection CSRF et validation des entrées

## 🔐 Sécurité

### Mesures de sécurité
- **Protection CSRF** sur tous les formulaires
- **Validation des entrées** utilisateur
- **Hachage des mots de passe** avec algorithmes sécurisés
- **Séparation des rôles** avec permissions appropriées
- **Protection contre les injections** SQL

## 🌐 Déploiement

### Production
1. **Variables d'environnement**
   ```env
   DEBUG=False
   ALLOWED_HOSTS=votre-domaine.com
   SECRET_KEY=clé-production-très-sécurisée
   ```

2. **Fichiers statiques**
   ```bash
   python manage.py collectstatic
   ```

3. **Base de données**
   - Configurer PostgreSQL/MySQL pour la production
   - Mettre à jour `DATABASES` dans settings.py

### Docker (optionnel)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 📝️ Documentation Technique

### Modèles de données
- **User** : Extension du modèle Django User avec rôle et infos bibliothèque
- **Book** : Livres avec auteurs, catégorie, exemplaires
- **Borrowing** : Emprunts avec dates, statut, pénalités
- **Penalty** : Pénalités avec statut de paiement
- **Reservation** : Réservations pour livres indisponibles

### Vues principales
- **Authentification** : login, register, logout
- **Tableaux de bord** : spécifiques par rôle
- **Gestion** : CRUD pour livres, auteurs, catégories
- **Emprunts** : création, retour, suivi

## 🤝 Contribuer

### Guide de contribution
1. Forker le projet
2. Créer une branche de fonctionnalité
3. Commiter les changements
4. Pousser vers la branche
5. Créer une Pull Request

### Normes de code
- **PEP 8** pour le style Python
- **Docstrings** pour toutes les fonctions/classes
- **Tests** pour toute nouvelle fonctionnalité
- **Commentaires** pour la logique complexe

## 📞 Support

### Documentation
- **Documentation Django** : https://docs.djangoproject.com/
- **Guide de développement** : Consulter les docstrings dans le code

### Contact
- **Issues** : Utiliser le système de suivi du projet
- **Documentation** : README.md et commentaires dans le code

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🚀 Démarrage Rapide

```bash
# 1. Installation
pip install django pillow

# 2. Migration
python manage.py makemigrations
python manage.py migrate

# 3. Superutilisateur
python manage.py createsuperuser

# 4. Démarrage
python manage.py runserver

# 5. Accès
# Navigateur : http://127.0.0.1:8000/
# Admin : http://127.0.0.1:8000/admin/
```

**Système prêt à l'emploi !** 🎉
