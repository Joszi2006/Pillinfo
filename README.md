# Drug-Info-Chatbot

## 📌 Problem
Many people struggle to understand the medications they are prescribed or buy over-the-counter. Drug packaging can be confusing, medical terms are hard to interpret, and misuse of medication leads to health risks. In regions with limited healthcare access, quick and reliable drug information is even harder to obtain.

## 💡 Solution
Drug Info Chatbot is an AI-powered assistant that helps users identify drugs and learn their correct usage. Users can provide a drug name (or upload an image of its packaging), and the chatbot returns information such as:
What the drug is used for
Common dosages
Potential side effects
Safety instructions
This project combines natural language processing (NLP) and computer vision (CV) techniques to make healthcare information more accessible and reliable.

## ⚙️ Features
🔍 Drug Identification: Recognize drugs by name or packaging image
💊 Usage Information: Purpose, dosage, and safety instructions
⚠️ Side Effects: Provide common risks or interactions
🤖 Chatbot Interface: Simple Q&A style interaction

## 🛠️ Tech Stack
Python
NLP (Hugging Face Transformers / spaCy)
Computer Vision (OpenCV, TensorFlow/PyTorch for image recognition)
Flask / FastAPI (for chatbot backend)
StreamlitUI for a simple web interface

## 🚀 How It Works
User enters a drug name or uploads an image of the drug package
The system processes the input with NLP (text) or CV (image)
Relevant medical information is retrieved from a trusted dataset/API - DailyMed/RxNorm
The chatbot presents results in a simple, user-friendly format

## 🎯 Future Improvements
Integrate with a real medical database (e.g., FDA API, DrugBank)
Support multilingual queries
Add voice input/output for accessibility