# TTS To Micro (VCable) - Convertisseur de Texte en Parole avec V-Cable

**TTS To Micro (VCable)** est un programme Python qui convertit du texte en parole en utilisant la bibliothèque `gTTS` (Google Text-to-Speech) et joue l'audio simultanément sur plusieurs périphériques, y compris le périphérique virtuel **Virtual Cable (V-Cable)**. Ce programme est conçu pour une utilisation simple et rapide, intégrant des fonctionnalités pratiques telles que la gestion des abréviations et une interface utilisateur de saisie de texte interactive.

## Fonctionnalités principales

- **Conversion de texte en parole** : Utilise `gTTS` pour convertir du texte en fichiers audio.
- **Lecture audio multi-périphérique** : Joue l'audio sur un périphérique de sortie principal (comme les haut-parleurs) et sur **Virtual Cable** en même temps.
- **Gestion des abréviations** : Remplace automatiquement les abréviations dans le texte par leur version complète grâce à un fichier JSON configurable (`abbreviations.json`).
- **Interface de saisie de texte interactive** : Capture le texte de l'utilisateur via le clavier avec confirmation de saisie, permet l'utilisation de raccourcis clavier pour démarrer la saisie, confirmer l'entrée, ou quitter le programme sans devoir être dans la fenêtre.

## Utilisation

1. **Configurer les abréviations** : Modifiez le fichier `abbreviations.json` pour ajouter ou modifier les abréviations. Exemple de fichier :

    ```json
    {
        "mtn": "maintenant",
        "ct": "c'était",
        "cam": "caméra",
        "alor": "alors",
        "dsl": "désolé"
    }
    ```

2. **Lancer le programme** : Exécutez le script principal.

3. **Saisir du texte** :
    - Appuyez sur `Alt` pour commencer la saisie.
    - Entrez votre texte.
    - Appuyez sur `Enter` pour confirmer et entendre le texte converti en parole.

4. **Quitter** :
    - Appuyez sur `Alt + Q` pour quitter le programme.

## Installation

Pour utiliser ce programme, assurez-vous d'avoir installé les dépendances nécessaires. Le fichier `requirements.txt` est déjà fourni. Installez les dépendances en utilisant la commande suivante :

```bash
pip install -r requirements.txt
