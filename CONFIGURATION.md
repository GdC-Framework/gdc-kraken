## 1) `config.json` (obligatoire)

Clés attendues :

- `SECRET_KEY`
  - Sert à la sécurité Django (sessions, CSRF, hachage, etc.).
- `PLATFORM`
  - Contrôle le mode de debug :
    - si `PLATFORM` vaut `"PROD"` => `DEBUG = False`
    - sinon => `DEBUG = True`
- `MISSIONS_PBO_STORAGE_PATH`
  - Chemin (relatif ou absolu) où sont stockés les fichiers `.pbo` une fois importés.
- `WSGI` (objet)
  - `PATH_SITE_PACKAGES`
    - En mode `"PROD"`, ajoute ce dossier à `site-packages` (via `site.addsitedir(...)`).
  - `PATH_GDC_KRAKEN`
    - Ajouté à `sys.path` à chaque démarrage WSGI (pour que les modules soient importables).
  - `PATH_GDC_STORM`
    - Ajouté à `sys.path` à chaque démarrage WSGI (pour que les modules soient importables).

Exemple : se baser sur `config.json.sample` puis créer le vrai `config.json` dans la racine.

## 2) Variables d'environnement (optionnelles)

Ces variables sont optionnelles car le code fournit une valeur par défaut :

- `MISSIONS_STORAGE_PATH`
  - Par défaut : `missions`
  - Sert pour `settings.MISSIONS_STORAGE_PATH` (lié à la zone de stockage “missions”).
- `MISSIONS_IMAGES_STORAGE_PATH`
  - Par défaut : `missions/images`
  - Sert pour `settings.MISSIONS_IMAGES_STORAGE_PATH` (images de missions / loadScreen / briefings selon le flux).

Exemple : se baser sur `.env.example` (ou exporte ces variables manuellement).

## 3) Donnees de developpement (DEV)

Pour generer des donnees fictives coherentes (maps, missions, joueurs, sessions) en mode DEV, utilise la commande Django :

- `python manage.py generate_fake_data --clear`
- Variante : `python manage.py generate_fake_data --clear --maps 6 --missions 15 --players 40 --sessions 25`

La commande peut aussi generer un `ApiToken` (affiche sa `key` dans la sortie console).

