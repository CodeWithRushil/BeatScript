from pyfiglet import Figlet
from colorama import Fore, Style, init
import time
import os
import logging
from flask import Flask, request
from flask_cors import CORS
import requests
import serial
import threading
import time
import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

init(autoreset=True)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)

# Configure your serial port and baud rate here
ser = serial.Serial('COM7', 9600)
time.sleep(2)
ser.flush()

current_song = None
is_playing = False

OFFSET = 2.0

def show_banner():
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('Rushil Sharma'))
    print(Fore.YELLOW + "♬ BeatScript — Syncing sound, light, and lyrics")
    print(Fore.GREEN + "-------------------------------------")
    print(Fore.WHITE + "Status: Starting...\n")

def loading():
    for i in range(4):
        print(Fore.YELLOW + "Loading" + "."*i)
        time.sleep(0.5)

def clean_title(title):
    title = title.replace("- YouTube", "")
    title = re.sub(r"\(.*?\)", "", title)

    remove_words = ["Lyrical", "Official", "Video", "HD"]
    for word in remove_words:
        title = title.replace(word, "")

    title = title.split("|")[0]
    return title.strip()

def convert_text(text):
    try:
        t = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        t = t.replace(".", "")
        t = t.replace("'", "")
        t = t.lower()
        replacements = {
            "aa": "a",
            "ii": "i",
            "uu": "u",
            "aii": "ai",
            "ae": "e",
            "aae": "aaye",
            "aai": "aayi",
            "rahaa": "raha",
            "rahii": "rahi",
            "nahii": "nahi",
            "kyaa": "kya",
            "haii": "hai",
            "zindagii": "zindagi",
        }
        for k, v in replacements.items():
            t = t.replace(k, v)
        t = " ".join(t.split())
        if len(t) > 0:
            t = t[0].upper() + t[1:]
        return t
    except:
        return text

def get_lrc(song):
    url = f"https://lrclib.net/api/search?q={song}"
    res = requests.get(url).json()
    for item in res:
        if item.get("syncedLyrics"):
            return item["syncedLyrics"]
    return None

def parse_lrc(lrc):
    lines = []
    for line in lrc.split("\n"):
        if "]" in line:
            try:
                time_part, text = line.split("]")
                t = time_part[1:]
                mins, secs = t.split(":")
                total = int(mins)*60 + float(secs)
                text = text.strip()
                if "♪" in text or "♫" in text:
                    text = "(Instrumental)"
                elif not all(ord(c) < 128 for c in text):
                    text = convert_text(text)
                if text == "":
                    continue
                lines.append((total, text))
            except:
                pass

    return lines

def play(parsed, expected_song):
    colors = [Fore.YELLOW, Fore.RED, Fore.CYAN, Fore.GREEN]
    i=0
    lines=0
    global is_playing, current_song
    start = time.time()
    for t, text in parsed:
        while time.time() - start < t + OFFSET:
            if current_song != expected_song:
                print(f"Killing old playback thread for: {expected_song}")
                return 
            time.sleep(0.01) 
        if current_song != expected_song:
            return
        print(colors[i] + f"♪ {text}")
        lines += 1
        if lines % 4 == 0:
            i = (i + 1) % len(colors)
            print('\n', end='')
        if ser:
            ser.write((text + "\n").encode())
    if current_song == expected_song:
        is_playing = False
        print("Song finished.")

@app.route('/title', methods=['POST'])
def receive_title():
    global current_song, is_playing
    data = request.json
    title = clean_title(data['title'])
    if title != current_song:
        print(Fore.CYAN + f"\nᯓ 𝄞 Detected Song: {title}")
        print(Fore.GREEN + "♫ LEDs & Lyrics Running...\n")
        current_song = title
        is_playing = True
        lrc = get_lrc(title)
        if lrc:
            if ser:
                ser.write(("TITLE:" + title + "\n").encode())
            time.sleep(6)
            parsed = parse_lrc(lrc)
            playback_thread = threading.Thread(target=play, args=(parsed, title))
            playback_thread.daemon = True
            playback_thread.start()
        else:
            print("No lyrics found.")
            if ser:
                ser.write("NO_LYRICS\n".encode())
            is_playing = False
    return {"status": "ok"}

os.system('cls')
loading()
show_banner()
app.run(host="0.0.0.0", port=5000, use_reloader=False)