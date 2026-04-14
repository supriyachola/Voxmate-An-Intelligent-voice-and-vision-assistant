---

## 📄 Research Publication

We are proud to present that this project has been accepted and published in:

🎓 **NCIIT 2025 – National Conference on Innovations in Information Technology**

📌 Paper Title:  
**“Voxmate: An Intelligent Voice & Vision Based Smart Assistant”**

🧠 This research focuses on:
- Multimodal AI integration (Voice + Vision)
- Real-time authentication and interaction
- Intelligent automation using LLMs
- Secure and scalable assistant architecture

📖 Status: **Published / Accepted (NCIIT 2025)**

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

## Out put 
<img width="704" height="517" alt="image" src="https://github.com/user-attachments/assets/7b6c8f7a-acd8-4230-ad8f-857b4cdc6abc" />
<img width="773" height="631" alt="image" src="https://github.com/user-attachments/assets/439e7a4c-1cc5-4a1a-ac5c-b19851514166" />
<img width="878" height="572" alt="image" src="https://github.com/user-attachments/assets/3e785d1e-73fd-4518-b8f6-287bfce83d1c" />
<img width="988" height="766" alt="image" src="https://github.com/user-attachments/assets/1a4c5d72-3786-444f-8708-ed4989fa42ae" />
<img width="692" height="538" alt="image" src="https://github.com/user-attachments/assets/2553f8f7-9dfc-45f6-8c88-30935672ecaf" />
<img width="552" height="836" alt="image" src="https://github.com/user-attachments/assets/94c2642e-cbfd-4cec-b35b-d0715230b0bf" />


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
---
