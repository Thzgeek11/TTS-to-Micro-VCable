from gtts import gTTS
import sounddevice as sd
import numpy as np
import threading
from pydub import AudioSegment
from io import BytesIO
import queue
import keyboard
import pyautogui
import time
import json  # Module pour gérer les fichiers JSON

# Queue pour la gestion des textes à convertir en parole
text_queue = queue.Queue()
# Événement pour indiquer le début de la saisie de texte
start_input_event = threading.Event()

def load_abbreviations(file_path):
    """
    Charger un dictionnaire d'abréviations à partir d'un fichier JSON.

    :param file_path: Chemin du fichier JSON contenant les abréviations
    :return: Dictionnaire avec les abréviations et leur signification
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Chargement des abréviations à partir d'un fichier JSON externe
abbreviations = load_abbreviations('abbreviations.json')

def apply_abbreviations(text):
    """
    Remplacer les abréviations dans le texte par leur forme complète.

    :param text: Texte à traiter
    :return: Texte avec les abréviations remplacées
    """
    for abbr, full in abbreviations.items():
        text = text.replace(abbr, full)
    return text

def play_audio(samples, samplerate, device):
    """
    Jouer un flux audio sur un périphérique spécifique.

    :param samples: Tableau numpy contenant les échantillons audio
    :param samplerate: Taux d'échantillonnage de l'audio
    :param device: Nom du périphérique audio de sortie
    """
    sd.play(samples, samplerate=samplerate, device=device)
    sd.wait()  # Attendre que la lecture se termine avant de continuer

def text_to_speech(text, lang='fr'):
    """
    Convertir un texte en parole et lire l'audio sur les périphériques de sortie.

    :param text: Texte à convertir en parole
    :param lang: Langue pour la synthèse vocale (par défaut 'fr' pour français)
    """
    # Appliquer les abréviations avant la conversion
    text = apply_abbreviations(text)

    # Créer un objet gTTS pour la conversion texte-parole
    tts = gTTS(text=text, lang=lang)

    # Sauvegarder l'audio converti en mémoire (buffer) au format MP3
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Convertir le MP3 en WAV pour lecture avec pydub
    sound = AudioSegment.from_file(mp3_fp, format="mp3")

    # Extraire les données audio sous forme de tableau numpy
    samples = np.array(sound.get_array_of_samples())

    # Si l'audio est en stéréo, remodeler pour 2 canaux
    if sound.channels == 2:
        samples = samples.reshape((-1, 2))

    # Détecter les périphériques de sortie "CABLE Input" et par défaut
    cable_input_device = None
    default_device = sd.query_devices(kind='output')['name']  # Périphérique par défaut (généralement les haut-parleurs)

    for device in sd.query_devices():
        if "CABLE Input" in device['name']:
            cable_input_device = device['name']
            break

    # Créer des threads pour lire l'audio simultanément sur les deux périphériques
    threads = []

    if cable_input_device:
        threads.append(threading.Thread(target=play_audio, args=(samples, sound.frame_rate, cable_input_device)))
    
    # Jouer l'audio sur les haut-parleurs (périphérique par défaut)
    threads.append(threading.Thread(target=play_audio, args=(samples, sound.frame_rate, default_device)))

    # Démarrer tous les threads pour jouer l'audio
    for thread in threads:
        thread.start()

    # Attendre que tous les threads aient terminé
    for thread in threads:
        thread.join()

def input_text():
    """
    Capturer le texte saisi par l'utilisateur avec une confirmation.

    La saisie est activée via une combinaison de touches, puis le texte est capturé et peut être corrigé 
    avec des abréviations avant d'être converti en parole.
    """
    input_buffer = ""
    global start_input_event

    print("Appuyez sur Alt gauche pour commencer à saisir du texte.")

    while True:
        event = keyboard.read_event()  # Lire l'événement du clavier
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'alt' and (keyboard.is_pressed('alt') and not keyboard.is_pressed('alt gr')):
                print("Saisie activée. Tapez votre texte (appuyez sur Enter pour confirmer, Alt+Q pour annuler la saisie, Alt+M pour quitter) :")
                start_input_event.set()  # Activer l'événement pour commencer la saisie

                # Désactiver la saisie clavier dans d'autres applications pour éviter des interférences
                pyautogui.FAILSAFE = False
                while start_input_event.is_set():
                    event = keyboard.read_event()  # Lire l'événement du clavier
                    if event.event_type == keyboard.KEY_DOWN:
                        if event.name == 'enter':
                            if input_buffer:
                                # Ajouter un espace avant les remplacements d'abréviations
                                input_buffer += ' '
                                # Appliquer les remplacements d'abréviations avant d'ajouter à la queue
                                corrected_text = apply_abbreviations(input_buffer.lower())
                                print(f"\nTexte corrigé : '{corrected_text}'")
                                text_queue.put(corrected_text)
                                input_buffer = ""
                            start_input_event.clear()  # Désactiver la saisie
                            pyautogui.FAILSAFE = True
                        elif event.name == 'backspace':
                            input_buffer = input_buffer[:-1]
                            print(f"\rTexte actuel : '{input_buffer}'", end="")
                        elif event.name == 'space':
                            input_buffer += ' '
                            print(f"\rTexte actuel : '{input_buffer}'", end="")
                        elif event.name == 'q' and (keyboard.is_pressed('alt')):
                            text_queue.put('quit')
                            start_input_event.clear()  # Désactiver la saisie
                            pyautogui.FAILSAFE = True
                            exit
                        elif event.name == 'm' and (keyboard.is_pressed('alt')):
                            exit()
                        elif not event.name in ['shift', 'ctrl', 'alt', 'capslock', '&', '"', ]:
                            # Ajouter le caractère au buffer de texte
                            if len(event.name) == 1:
                                input_buffer += event.name
                            else:
                                # Gérer les caractères spéciaux ici, si nécessaire
                                pass
                            print(f"\rTexte actuel : '{input_buffer}'", end="")

if __name__ == "__main__":
    # Démarrer le thread pour capturer le texte de l'utilisateur
    input_thread = threading.Thread(target=input_text)
    input_thread.start()

    while True:
        # Attendre que du texte soit disponible dans la queue
        text = text_queue.get()

        if text.lower() == 'quit':
            break

        # Convertir le texte en parole et jouer l'audio
        text_to_speech(text)

    # Attendre que le thread de saisie soit terminé
    input_thread.join()
