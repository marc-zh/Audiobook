from google.cloud import texttospeech
import os

# API-SCHLÜSSEL EINTRAGEN
API_KEY = "platz_halter"

# Ausgabeordner für die Audiodateien
OUTPUT_FOLDER = "C:\\platzhalter"  # Ordner für die Audiodateien

# Stimmkonfiguration
VOICE_NAME = "en-US-Chirp3-HD-Callirrhoe"  # Premium HD-Stimme
LANGUAGE_CODE = "en-US"  # Sprachcode

# Ausgabeordner erstellen, falls nicht vorhanden
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


def text_to_speech(text, output_filename):
    """Konvertiert Text zu Sprache mit hardkodierten Einstellungen"""

    # Client initialisieren mit API-Schlüssel
    client = texttospeech.TextToSpeechClient()
    # API-Schlüssel über Umgebungsvariable setzen
    os.environ["GOOGLE_API_KEY"] = API_KEY

    # Text-Input konfigurieren
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Hardkodierte Stimmenauswahl
    voice = texttospeech.VoiceSelectionParams(
        language_code=LANGUAGE_CODE,
        name=VOICE_NAME
    )

    # Hardkodierte Audioeinstellungen - MP3 mit guter Qualität
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        sample_rate_hertz=24000  # Höhere Samplerate für bessere Qualität
    )

    # API-Anfrage senden
    try:
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Vollständiger Ausgabepfad
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Audio-Datei speichern
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio gespeichert als: {output_path}')

        return output_path
    except Exception as e:
        print(f"Fehler bei der API-Anfrage: {e}")
        return None


def generate_missing_parts():
    """Generiert nur die fehlenden Teile (12, 23, 24, 27, 42, 45)"""

    # *** HIER IHREN TEXT EINFÜGEN - genau wie im ursprünglichen Skript ***
    direkter_text = """"""  # Hier Ihren vollständigen Text einfügen

    # Länge des Texts prüfen
    print(f"Gesamter Text enthält {len(direkter_text)} Zeichen")

    # Text in 4000-Zeichen-Abschnitte aufteilen
    MAX_CHUNK_SIZE = 4000  # chunk_size
    chunks = [direkter_text[i:i + MAX_CHUNK_SIZE] for i in range(0, len(direkter_text), MAX_CHUNK_SIZE)]

    # Liste der fehlenden Teile
    missing_parts = [] # z.b 12, 23, 24, 27, 42, 45

    # Nur die fehlenden Teile verarbeiten
    for part_number in missing_parts:
        if part_number <= len(chunks):
            index = part_number - 1  # 0-basierter Index
            chunk = chunks[index]
            output_file = f"teil_{part_number}.mp3"
            print(f"Verarbeite fehlenden Teil {part_number}...")
            path = text_to_speech(chunk, output_file)
            if not path:
                print(f"Fehler bei Teil {part_number}, versuche mit kleinerer Größe...")
                # Versuche mit einem kleineren Chunk
                half_size = len(chunk) // 2
                # Erste Hälfte
                first_half = chunk[:half_size]
                output_file = f"teil_{part_number}_a.mp3"
                text_to_speech(first_half, output_file)
                # Zweite Hälfte
                second_half = chunk[half_size:]
                output_file = f"teil_{part_number}_b.mp3"
                text_to_speech(second_half, output_file)
        else:
            print(f"Teil {part_number} existiert nicht (nur {len(chunks)} Teile insgesamt)")


# HAUPTPROGRAMM - Nur die fehlenden Teile generieren
if __name__ == "__main__":
    generate_missing_parts()

    import os
    import glob
    import io


    def merge_mp3_files_binary(input_folder, output_filename="a_complete_audiobook.mp3"):
        """
        Präzisere Variante zum Zusammenfügen von MP3-Dateien auf Binärebene.
        """
        print(f"Beginne mit dem Zusammenfügen aller Audiodateien aus {input_folder}...")

        # Alle MP3-Dateien im Eingabeordner finden
        mp3_files = glob.glob(os.path.join(input_folder, "teil_*.mp3"))

        # Dateinamen nach Nummer sortieren
        def sort_key(filename):
            basename = os.path.basename(filename)
            if '_a.mp3' in basename or '_b.mp3' in basename:
                main_num = int(basename.split('_')[1])
                sub_part = 0 if '_a.mp3' in basename else 1
                return (main_num, sub_part)
            else:
                num = int(basename.split('_')[1].split('.')[0])
                return (num, -1)

        sorted_files = sorted(mp3_files, key=sort_key)

        if not sorted_files:
            print("Keine Audiodateien gefunden!")
            return False

        print(f"Gefundene Audiodateien: {len(sorted_files)}")

        # Ausgabedatei erstellen
        output_path = os.path.join(input_folder, output_filename)

        # MP3-Dateien zusammenfügen
        try:
            with open(output_path, 'wb') as outfile:
                # Erste Datei vollständig kopieren (mit Header)
                first_file = sorted_files[0]
                print(f"Kopiere erste Datei: {os.path.basename(first_file)}")
                with open(first_file, 'rb') as infile:
                    outfile.write(infile.read())

                # Bei den weiteren Dateien versuchen, nur die Audiodaten ohne ID3-Header zu kopieren
                for file in sorted_files[1:]:
                    print(f"Füge hinzu: {os.path.basename(file)}")
                    with open(file, 'rb') as infile:
                        # MP3-Daten lesen
                        data = infile.read()

                        # Nach dem MP3-Frame-Header suchen (typischerweise beginnt mit 0xFF 0xFB)
                        frame_start = -1
                        for i in range(len(data) - 1):
                            if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:  # 0xE0 = 0b11100000
                                frame_start = i
                                break

                        if frame_start != -1:
                            # Nur die Daten ab dem ersten MP3-Frame-Header schreiben
                            outfile.write(data[frame_start:])
                        else:
                            # Falls kein Frame-Header gefunden wurde, alles nach den ersten 128 Bytes schreiben
                            # (typische Größe eines ID3v1-Headers)
                            outfile.write(data[128:])

            print(f"Fertiges Hörbuch gespeichert als: {output_path}")
            return True

        except Exception as e:
            print(f"Fehler beim Zusammenfügen: {e}")
            return False


    # Aufruf
    if __name__ == "__main__":
        # Pfad zum Ordner mit den MP3-Dateien
        audio_folder = "C:\\your\path"

        # Zusammenfügen der Dateien
        merge_mp3_files_binary(audio_folder)
