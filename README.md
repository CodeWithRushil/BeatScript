# BeatScript 🎧

**Syncing sound, light, and lyrics**

A full-stack project that extracts YouTube video titles using a Chrome extension, fetches synced lyrics from an API, and displays them in real-time on both the terminal and an Arduino-powered LED system.

---

## 🚀 Features

* Chrome Extension to detect YouTube video titles automatically
* Flask backend API to process and manage requests
* Fetches synced lyrics (LRC format) from an online API
* Real-time lyric synchronization with timestamps
* Automatic transliteration (Hindi → Hinglish) for better readability
* Arduino LED display integration for live lyric output

---

## 📁 Project Structure

```
BeatScript/
│
├── extension/                 
│   ├── manifest.json
│   ├── content.js
│   ├── icons/
│
├── backend/                   
│   ├── beatScript.bat          
│   ├── lyrics_engine.py    
│   ├── requirements.txt
│
├── arduino/beatScript                  
│   ├── beatScript.ino
│
├── .gitignore
├── README.md
```

---

## ⚙️ Setup Instructions

### 🔹 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Run the backend:

* On Windows: double-click `beatScript.bat`
* Or via terminal:

```bash
python lyrics_engine.py
```
---

### 🌐 Server

The backend runs at:

```
http://localhost:5000
```

💡 **Note:**

* `localhost` works if you're running everything on the same system
* If accessing from another device on the same network, replace `localhost` with your machine’s IPv4 address (e.g., `http://192.168.x.x:5000`)
---

### 🔹 2. Load Chrome Extension

1. Open `chrome://extensions/`
2. Enable **Developer Mode**
3. Click **Load Unpacked**
4. Select the `extension/` folder

---

### 🔹 3. Arduino Setup

* Upload `beatScript.ino` to your Arduino board
* Ensure correct COM port in `lyrics_engine.py`:

```python
ser = serial.Serial('COM7', 9600)
```

---

## 🔄 How It Works

1. User plays a YouTube video
2. Extension detects the video title
3. Title is sent to Flask backend
4. Backend fetches synced lyrics (LRC format)
5. Lyrics are parsed and timed
6. Output is:

   * Printed in terminal 🎵 
   * Sent to Arduino LEDs 💡

---

## 🛠 Tech Stack

* **Frontend**: Chrome Extension (JavaScript)
* **Backend**: Python, Flask
* **Libraries**: requests, pyserial, pyfiglet, colorama
* **Hardware**: Arduino (LED display)

---

## ⚠️ Notes

* Replace API URL with `localhost` for local development
* Ensure backend is running before using the extension
* Arduino must be connected to the correct port

---

## 📌 Future Improvements

* Deploy backend for public access
* Add GUI dashboard
* Improve lyric accuracy and fallback handling
* Support multiple languages

---

## 👨‍💻 Author

**Rushil Sharma**

---

## ⭐ Show Your Support

If you like this project, consider giving it a ⭐ on GitHub!
