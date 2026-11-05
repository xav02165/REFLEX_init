# REFLEX_init
# 📊 Projet Reflex Initiation — Dashboard Dataviz

Ce projet est un guide pratique pour installer et configurer un tableau de bord (dashboard) frontend de Data Visualization en utilisant le framework **Reflex** (Python pur, compilé en React/Next.js sous le capot).

---

## 🛠️ Prérequis Système

Avant de commencer, assurez-vous d'avoir installé sur votre machine :
* **Python 3.8 à 3.14**
* **Node.js & npm** (indispensables pour la compilation du frontend)

Sur Linux (Ubuntu/Debian), vous pouvez installer Node.js avec :
```bash
sudo apt update && sudo apt install nodejs npm
```

---

## 🚀 Étape 1 : Installation et Initialisation

1. **Créer le dossier du projet et s'y déplacer :**
   ```bash
   mkdir Reflex_initiation
   cd Reflex_initiation
   ```

2. **Créer et activer l'environnement virtuel Python :**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Installer Reflex :**
   ```bash
   pip install reflex
   ```

4. **Initialiser le template de l'application :**
   ```bash
   reflex init
   ```

---

## 🔧 Étape 2 : Résolution des Bugs de Configuration (Retours d'Expérience)

Lors de la première configuration, plusieurs erreurs classiques de jeunesse du framework ont été corrigées. Voici comment les éviter :

### 1. Erreur PostCSS / Tailwind (`Cannot find module '@tailwindcss/postcss'`)
Si le framework se lance sans styles graphiques (style HTML brut des années 90) ou crache une erreur Vite/PostCSS, l'environnement frontend `.web` a besoin d'être réinitialisé et forcé à installer les dépendances CSS.
* **Solution :** Supprimer le dossier temporaire corrompu et forcer l'installation des paquets Node.js manquants.
  ```bash
  # Supprimer le dossier web généré
  rm -rf .web

  # Lancer pour forcer la recréation du dossier (s'il s'arrête, faites la suite)
  reflex run

  # Aller dans le dossier généré et forcer l'install des modules CSS
  cd .web
  npm install -D @tailwindcss/postcss postcss tailwindcss
  cd ..
  ```

### 2. Typage strict de `spacing` (Radix UI)
L'utilisation de valeurs CSS brutes comme `spacing="16px"` provoque un plantage du compilateur Reflex (`TypeError: Invalid var passed for prop VStack.spacing`).
* **Règle d'or :** Reflex utilise le système de design de Radix UI. L'espacement doit être une chaîne de caractères comprise entre `"0"` et `"9"`.
* **Équivalence :** Utilisez **`spacing="4"`** pour obtenir un espacement propre équivalent à `16px`.

### 3. Changement de nom Recharts Tooltip
Dans le composant de graphique `rx.recharts.line_chart`, le composant d'infobulle a changé de nom.
* **Correction :** Remplacer `rx.recharts.graph_tooltip()` par **`rx.recharts.graphing_tooltip()`**.

---

## 🎨 Étape 3 : Configuration Moderne du Thème (`rxconfig.py`)

Depuis la version 0.9.x de Reflex, définir le thème dans `rx.App(theme=...)` est obsolète (*DeprecationWarning*). Le thème global se configure désormais de manière centralisée dans le fichier **`rxconfig.py`** à la racine :

```python
import reflex as rx

config = rx.Config(
    app_name="Reflex_initiation",
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",       # Mode clair par défaut
                has_background=True,
                radius="large",           # Arrondi des cartes et boutons
                accent_color="indigo",    # Couleur d'accentuation principale
            )
        )
    ],
)
```

---

## 🏃‍♂️ Étape 4 : Lancement du Serveur de Développement

Une fois les configurations appliquées et le dossier épuré, démarrez l'application à l'aide de la commande suivante :

```bash
reflex run
```

L'application compilera vos fichiers Python en une application Next.js ultra-rapide. Vous pourrez la visionner sur votre navigateur à l'adresse :
👉 **`http://localhost:3000`**
