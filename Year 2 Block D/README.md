# Emotion MVP - Multilingual Emotion Classification Pipeline

A production-ready emotion classification system that processes audio, video, and text to detect emotional content. Built with MLOps best practices and deployed on Microsoft Azure ML.

## 🎯 Project Overview

Developed for Content Intelligence Agency to analyze emotional content in TV shows and video media. The system automatically transcribes, translates, and classifies emotions from multimedia inputs, helping content creators understand viewer engagement patterns.

## ✨ Features

- **Multi-format Input:** Audio (MP3, WAV, M4A), Video (MP4), Text (TXT, CSV), YouTube URLs
- **Multilingual Support:** Automatic language detection and translation (English, French, Dutch)
- **Emotion Classification:** 6 base emotions (anger, disgust, fear, happiness, sadness, surprise)
- **Intensity Analysis:** Quantitative emotion intensity scoring with categorical labels
- **Multiple Interfaces:** CLI, REST API (FastAPI), Web Application (React)
- **Cloud Deployment:** Azure ML with automated pipelines
- **Docker Support:** Fully containerized application

## 🛠️ Technologies Used

### Machine Learning & NLP
- **OpenAI Whisper** - Audio transcription
- **Transformers/Hugging Face** - BERT emotion classification
- **Helsinki-NLP (Opus-MT)** - Multilingual translation
- **PyTorch** - Deep learning framework

### MLOps & Cloud
- **Microsoft Azure ML** - Model training, registry, deployment
- **MLflow** - Experiment tracking and versioning
- **Docker & Docker Compose** - Containerization
- **Apache Airflow** - Pipeline orchestration
- **GitHub Actions** - CI/CD automation

### Application Stack
- **FastAPI** - REST API framework
- **React + TypeScript** - Web frontend
- **Poetry** - Dependency management
- **pytest** - Testing framework

## 📁 Project Structure
```
emotion-detection-mlops/
├── emotion_mvp/              # Core Python package
│   ├── pipeline.py          # Main processing pipeline
│   ├── transcriber.py       # Whisper audio transcription
│   ├── translator.py        # Language translation
│   ├── classifier.py        # Emotion classification
│   ├── cli.py              # Command-line interface
│   └── api/                # FastAPI application
├── Frontend/                # React web application
├── docker/                  # Docker configurations
├── Azure_edo/              # Azure ML pipelines
│   └── airflow/            # Airflow DAGs
├── tests/                  # Test suite
├── pyproject.toml         # Poetry dependencies
├── docker-compose.yml     # Container orchestration
└── README.md
```

## 🚀 Quick Start

### Installation
```bash
# Using Poetry
poetry install
poetry env activate
emotion-cli --help

# Using pip
pip install -r requirements.txt
python -m emotion_mvp.cli --help

# Using Docker
docker-compose up
```

### Basic Usage
```bash
# Classify text
emotion-cli predict-any "I am feeling really happy today!"

# Process audio file
emotion-cli predict-any audio.mp3

# Analyze YouTube video
emotion-cli predict-any "https://www.youtube.com/watch?v=VIDEO_ID"

# Start API server
uvicorn emotion_mvp.api.main:app --host 0.0.0.0 --port 8000
```

### Output Format

Results are saved as CSV files with:
- Start/end timestamps
- Transcribed text
- Translation (if applicable)
- Predicted emotion
- Confidence score
- Intensity rating (neutral/mild/moderate/strong/intense)

## ☁️ Azure ML Deployment

### Automated Pipelines

**Data Pipeline:**
- Automated data ingestion and preprocessing
- Versioned datasets stored as Azure ML data assets
- Scheduled and trigger-based execution

**Training Pipeline:**
- Weekly automated retraining on new data
- Hyperparameter optimization
- Model evaluation and registration
- Experiment tracking with MLflow

**Deployment Pipeline:**
- Multi-strategy deployment (real-time, batch)
- Automated testing and validation
- Manual approval gates for production
- CI/CD integration with GitHub Actions

### Monitoring & Continuous Improvement

- **Performance Monitoring:** Real-time accuracy and latency tracking
- **Drift Detection:** Automated alerts for model degradation
- **User Feedback Loop:** Collect corrections for model improvement
- **Automated Retraining:** Triggered by performance thresholds or new data

## 🏆 MLOps Best Practices Implemented

✅ **Modular Python package** with CLI, API, and web interface  
✅ **Docker containerization** for reproducible deployments  
✅ **Automated CI/CD** with GitHub Actions  
✅ **Data and model versioning** with Azure ML  
✅ **Experiment tracking** with MLflow  
✅ **Comprehensive testing** with pytest  
✅ **Production-ready code** following PEP8 standards  
✅ **Professional documentation** with Sphinx  
✅ **Monitoring dashboards** for deployed models  
✅ **Continuous retraining** based on feedback  

## 🎓 Learning Outcomes

Through this project, I developed expertise in:
- **MLOps lifecycle management** from development to production
- **Cloud computing** with Microsoft Azure ML
- **Containerization** with Docker and orchestration
- **API development** with FastAPI
- **Frontend development** with React and TypeScript
- **CI/CD pipelines** with GitHub Actions
- **Data engineering** and pipeline design
- **Model monitoring** and continuous improvement
- **Agile/Scrum** project management with Azure DevOps
- **Team collaboration** across 5-person development team

## 👥 Team

**Team NLP-1:**
- Musaed Alfareh
- Michon Goddijn
- Edoardo Pierezza
- Rafał Stańczyszyn
- Christopher Schreuder

**Project Management:** Agile Scrum with 5 two-week sprints using Azure DevOps

## 🙏 Acknowledgments

- **Content Intelligence Agency & Banijay Benelux** - Project client
- **BUas Faculty** - Dean van Aswegen, Jason Harty, Dr. Tsegaye Tashu
- **Product Owners** - Technical guidance and sprint reviews

## 📄 License

This project was completed as part of academic coursework at Breda University of Applied Sciences.

---

*Year 2, Block D - MLOps Engineer | June 2025*

**Tags:** `mlops` `azure-ml` `emotion-detection` `nlp` `fastapi` `docker` `ci-cd` `react` `typescript` `python`