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
import requests

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

CONSONANTS = {
    'क': 'k',  'ख': 'kh', 'ग': 'g',   'घ': 'gh',  'ङ': 'ng',
    'च': 'ch', 'छ': 'chh','ज': 'j',   'झ': 'jh',  'ञ': 'n',
    'ट': 't',  'ठ': 'th', 'ड': 'd',   'ढ': 'dh',  'ण': 'n',
    'त': 't',  'थ': 'th', 'द': 'd',   'ध': 'dh',  'न': 'n',
    'प': 'p',  'फ': 'ph', 'ब': 'b',   'भ': 'bh',  'म': 'm',
    'य': 'y',  'र': 'r',  'ल': 'l',   'व': 'v',
    'श': 'sh', 'ष': 'sh', 'स': 's',   'ह': 'h',
    'क़': 'q',  'ख़': 'kh', 'ग़': 'gh',  'ज़': 'z',
    'ड़': 'r',  'ढ़': 'rh', 'फ़': 'f',   'य़': 'y'
}

VOWELS_STANDALONE = {
    'अ': 'a',  'आ': 'aa', 'इ': 'i',  'ई': 'ii',
    'उ': 'u',  'ऊ': 'uu', 'ए': 'e',  'ऐ': 'ai',
    'ओ': 'o',  'औ': 'au', 'ऋ': 'ri',
}

VOWEL_SIGNS = {
    'ा': 'aa', 'ि': 'i',  'ी': 'i',  'ु': 'u',
    'ू': 'u',  'े': 'e',  'ै': 'ai', 'ो': 'o',
    'ौ': 'au', 'ृ': 'ri',
}

NUKTA_MAP = {
    'क': 'q',  'ख': 'kh', 'ग': 'gh', 'ज': 'z',
    'ड': 'r',  'ढ': 'rh', 'फ': 'f',  'य': 'y',
}

NUKTA       = '\u093C'
ANUSVARA    = '\u0902' 
CHANDRABINDU= '\u0901'   
VISARGA     = '\u0903'   
HALANT      = '\u094D'   

WORD_FIXES = {
    'rahaa':    'raha',    'rahii':    'rahi',
    'nahii':    'nahi',    'kyaa':     'kya',
    'haii':     'hai',     'teraa':    'tera',
    'meraa':    'mera',
    'karana':   'karna',   'mujhase':  'mujhse',
    'tumhase':  'tumhse',  'sabase':   'sabse',
    'usakaa':   'uska',    'usakee':   'uski',
    'isase':    'isse',    'isako':    'isko',
}

def _transliterate_word(deva_word: str) -> str:
    chars = list(deva_word)
    n = len(chars)
    syllables = [] 
    i = 0
    while i < n:
        ch = chars[i]
        if ch in CONSONANTS or (i + 1 < n and chars[i + 1] == NUKTA and ch in NUKTA_MAP):
            if i + 1 < n and chars[i + 1] == NUKTA and ch in NUKTA_MAP:
                roman_cons = NUKTA_MAP[ch]
                i += 2
            else:
                roman_cons = CONSONANTS[ch]
                i += 1
            while i + 1 < n and chars[i] == HALANT and chars[i + 1] in CONSONANTS:
                conj_cons = chars[i + 1]
                if i + 2 < n and chars[i + 2] == NUKTA and conj_cons in NUKTA_MAP:
                    roman_cons += NUKTA_MAP[conj_cons]
                    i += 3
                else:
                    roman_cons += CONSONANTS[conj_cons]
                    i += 2
            if i < n and chars[i] == HALANT:
                syllables.append((roman_cons, '', False))        
                i += 1
            elif i < n and chars[i] in VOWEL_SIGNS:
                vsign = VOWEL_SIGNS[chars[i]]; i += 1
                nasal = ''
                if i < n and chars[i] in (ANUSVARA, CHANDRABINDU):
                    nasal = 'n'; i += 1
                syllables.append((roman_cons, vsign + nasal, False))
            elif i < n and chars[i] in (ANUSVARA, CHANDRABINDU):
                syllables.append((roman_cons, 'an', False)); i += 1
            else:
                syllables.append((roman_cons, 'a', True))       
            continue
        if ch in VOWELS_STANDALONE:
            v = VOWELS_STANDALONE[ch]; i += 1
            nasal = ''
            if i < n and chars[i] in (ANUSVARA, CHANDRABINDU):
                nasal = 'n'; i += 1
            syllables.append(('', v + nasal, False))
            continue

        if ch in (ANUSVARA, CHANDRABINDU):
            syllables.append(('', 'n', False)); i += 1; continue
        if ch == VISARGA:
            syllables.append(('', 'h', False)); i += 1; continue
        if '\u0966' <= ch <= '\u096F':                           
            syllables.append(('', str(ord(ch) - ord('\u0966')), False)); i += 1; continue
        syllables.append(('', ch, False)); i += 1               

    result = []
    total = len(syllables)
    for j, (cons, vowel, is_inh) in enumerate(syllables):
        if is_inh and j == total - 1:
            result.append(cons)          
        else:
            result.append(cons + vowel)
    word = ''.join(result)
    if word.endswith('aa'):
        word = word[:-2] + 'a'
    word = word.replace('chchh', 'chh')
    word = word.replace('chch',  'chh')
    word = word.replace('shsh',  'sh')
    return word

def clean_title(title):
    title = title.replace("- YouTube", "")
    title = re.sub(r"\(.*?\)", "", title)

    remove_words = ["Lyrical", "Official", "Video", "HD"]
    for word in remove_words:
        title = title.replace(word, "")

    title = title.split("|")[0]
    return title.strip()

def convert_text(text: str) -> str:
    try:
        tokens = text.split()
        roman_tokens = []
        for token in tokens:
            # Pass through already-ASCII tokens (English words, numbers)
            if all(ord(c) < 128 for c in token):
                roman_tokens.append(token)
            else:
                roman_tokens.append(_transliterate_word(token))

        t = ' '.join(roman_tokens)
        t = t.replace('.', '').replace("'", '')
        t = t.lower()

        # Apply word-level normalizations (whole-word matches only)
        for k, v in WORD_FIXES.items():
            t = re.sub(r'\b' + re.escape(k) + r'\b', v, t)

        t = ' '.join(t.split())
        if t:
            t = t[0].upper() + t[1:]
        return t

    except Exception as e:
        return text

def is_roman_script(text):
    if re.search(r'[\u0900-\u097F\u0A00-\u0A7F]', text):
        return False
    return True

def get_lrc(song):
    url = f"https://lrclib.net/api/search?q={song}"
    try:
        res = requests.get(url).json()
    except requests.RequestException:
        return None
    best_fallback = None
    for item in res:
        lyrics = item.get("syncedLyrics")
        if lyrics:
            if best_fallback is None:
                best_fallback = lyrics
            if is_roman_script(lyrics):
                return lyrics
    return best_fallback

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