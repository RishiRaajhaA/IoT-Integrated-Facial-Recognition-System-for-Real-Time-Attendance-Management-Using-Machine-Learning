# 🧠 IoT Integrated Facial Recognition System for Real-Time Attendance Management

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![Django](https://img.shields.io/badge/Framework-Django-success)
![IoT](https://img.shields.io/badge/IoT-MQTT-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📌 Overview

This is a smart attendance tracking system using **facial recognition** and **IoT**. It eliminates the need for physical interaction and ensures secure, real-time attendance logging through face detection and recognition. Ideal for academic and corporate environments, this system integrates:

- **MTCNN** for real-time face detection
- **InceptionResNetV1** for face recognition
- **Django** for backend processing
- **MQTT protocol** for device communication

---

## 🚀 Features

- 🎯 Accurate face detection & recognition
- 🎥 Smart Wi-Fi camera integration
- 🔄 Real-time data sync via MQTT
- 📋 Admin and student portal via Django
- 🌐 Scalable and secure system design

---

## 🧠 Tech Stack

| Layer            | Technology                       |
|------------------|-----------------------------------|
| Face Detection   | MTCNN (TensorFlow/Keras)         |
| Feature Embedding| InceptionResNetV1 (FaceNet)      |
| Backend          | Django (Python)                  |
| Frontend         | HTML/CSS (via Django templates)  |
| Database         | SQLite / MySQL                   |
| IoT Messaging    | MQTT (Mosquitto broker)          |

---

## 🛠 Folder Structure

```plaintext
.
├── app1/                 # Django app with business logic
│   ├── migrations/
│   └── __pycache__/
├── media/                # Uploaded images (students, student_images)
├── ppt/                  # Project presentation
│   └── ML_Final.pptx
├── Project101/           # Django project config
│   ├── static/
│   │   └── videos/
│   └── __pycache__/
├── screenshots/          # Add demo images of the UI or system
├── templates/            # Frontend HTML templates
├── venv/                 # Virtual environment (ignored via .gitignore)
├── requirements.txt      # Python dependencies
├── manage.py             # Django project manager
└── README.md             # This file
