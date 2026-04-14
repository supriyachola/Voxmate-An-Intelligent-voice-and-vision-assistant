# Voxmate 🤖🎙️👁️  
**An Intelligent Voice & Vision Based Smart Assistant**

Voxmate is a secure, real-time **multimodal AI assistant** that integrates **facial authentication**, **voice interaction**, **live audio–video streaming**, and **intelligent automation** into a single unified system.

This project is based on the IEEE research paper  
**“Voxmate: An Intelligent Voice & Vision Based Smart Assistant”** :contentReference[oaicite:0]{index=0}

---

## ✨ Key Highlights

- 🔐 Face-based biometric authentication before task execution  
- 🎙️ Natural voice interaction with real-time speech recognition  
- 📹 Live audio–video streaming using WebRTC  
- 🧠 Intent understanding using a lightweight LLM  
- ⚙️ Modular automation (Email, Web, IoT, System tools)  
- 🔊 Multimodal feedback (voice, text, visual)

---

## 🧩 System Architecture

User (Voice + Face)
↓
Input Layer (Camera & Mic)
↓
Authentication Layer (DeepFace)
↓
Communication Layer (LiveKit + WebRTC)
↓
Reasoning Layer (Speech → Intent → Decision)
↓
Automation Tools (Email | Web | IoT | System)
↓
Multimodal Feedback (Voice | Text | Visual)

> The layered architecture ensures **security, low latency, and modular scalability**.

---

## 📁 Project Structure

voxmate/
│
├── backend/
│ ├── main.py # FastAPI entry point
│ ├── auth/
│ │ ├── face_verify.py # DeepFace authentication
│ │ └── database.py # User embeddings storage
│ │
│ ├── ai/
│ │ ├── speech_to_text.py # Google Realtime AI
│ │ ├── intent_engine.py # LLM-based intent reasoning
│ │ └── tts.py # Text-to-speech
│ │
│ ├── tools/
│ │ ├── email_tool.py
│ │ ├── web_tool.py
│ │ ├── iot_tool.py
│ │ └── system_tool.py
│ │
│ └── utils/
│ ├── logger.py
│ └── config.py
│
├── frontend/
│ └── livekit_ui/ # LiveKit Agents Playground
│
├── iot/
│ └── esp32/
│ └── led_control.ino
│
├── requirements.txt
├── .env.example
└── README.md


---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- OpenCV
- NumPy
- DeepFace

### AI & Speech
- Google Realtime Speech-to-Text
- Lightweight LLM (intent classification)

### Communication
- LiveKit
- WebRTC

### Automation
- SMTP (Email)
- MQTT (IoT)
- Python subprocess (System tools)

### Hardware
- Webcam
- Microphone
- ESP32 (IoT devices)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/voxmate.git
cd voxmate
