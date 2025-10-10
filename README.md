📌 Project Overview
This repository contains an end-to-end ML Ops workflow that uses MLflow, Docker, Jenkins, DVC, and Google Cloud Platform (GCP) to build, train, deploy, and serve a machine learning model.

🚀 1. Local Development Setup
# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Push project to GitHub
git init
git add .
git commit -m "Initial commit - ML Ops project"
git branch -M main
git remote add origin https://github.com/<user>/ML_OPS_Project2.git
git push -u origin main

📝 2. Core Python Modules

logger.py → Centralized logging
custom_exception.py → Unified error handling
common_functions.py → YAML reader & data loader
data_ingestion.py → Downloads raw CSV from GCP bucket & splits train/test
data_preprocessing.py → Cleans data, encodes, balances classes (SMOTE), feature selection
model_training.py → Trains LightGBM with hyperparameter tuning, logs metrics in MLflow
application.py → Flask app to serve predictions

Run modules locally:
python src/data_ingestion.py
python src/data_preprocessing.py
python src/model_training.py
python application.py

🐳 3. Docker Setup
FROM python:slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install --no-cache-dir -e .
RUN python src/model_training.py
EXPOSE 5000
CMD ["python", "application.py"]
Build & run:
docker build -t ml-ops-app .
docker run -p 5000:5000 ml-ops-app

🔧 4. Jenkins in Docker (DinD)
Create custom Jenkins image with Docker installed.
custom_jenkins/Dockerfile
FROM jenkins/jenkins:lts
USER root
RUN apt-get update -y && apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && echo "deb [arch=amd64] https://download.docker.com/linux/debian bullseye stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update -y && apt-get install -y docker-ce docker-ce-cli containerd.io && apt-get clean
RUN groupadd -f docker && usermod -aG docker jenkins
RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker
USER jenkins
Build & run Jenkins:
cd custom_jenkins
docker build -t jenkins-dind .
docker run -d --name jenkins-dind \
  --privileged \
  -p 8080:8080 -p 50000:50000 \
  -v //var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  jenkins-dind

📦 5. Jenkins Pipeline (CI/CD)
Jenkinsfile
pipeline {
    agent any
    environment {
        PROJECT_ID = 'my-gcp-project'
        IMAGE = "gcr.io/${PROJECT_ID}/ml-ops-app:${env.BUILD_ID}"
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/<user>/ML_OPS_Project2.git'
            }
        }
        stage('Setup venv') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                sh '. venv/bin/activate && pytest -q'
            }
        }
        stage('Build Docker') {
            steps {
                sh "docker build -t ${IMAGE} ."
            }
        }
        stage('Push to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa', variable: 'GCLOUD_KEY')]) {
                    sh 'gcloud auth activate-service-account --key-file=$GCLOUD_KEY'
                    sh 'gcloud auth configure-docker --quiet'
                    sh "docker push ${IMAGE}"
                }
            }
        }
    }
}

☁️ 6. Deploy to GCP (Cloud Run)
gcloud run deploy ml-ops-app \
  --image gcr.io/my-gcp-project/ml-ops-app:latest \
  --region us-central1 \
  --platform managed \

🔗 7. DVC for Data Versioning
Initialize DVC and track datasets:
# Install DVC
pip install dvc[gdrive]   # or dvc[s3], dvc[azure] based on storage

# Initialize DVC in the repo
dvc init

# Add data to DVC tracking
dvc add data/raw_dataset.csv

# Commit DVC metadata
git add data/raw_dataset.csv.dvc .dvc/config
git commit -m "Track raw dataset with DVC"

# Push data to remote storage
dvc remote add -d myremote gdrive://<folder-id>
dvc push

Pull data in another environment:
dvc pull
Reproduce pipeline stages:
dvc repro

🔍 Mermaid Diagram: Full ML Ops Pipeline

<img width="559" height="2268" alt="image" src="https://github.com/user-attachments/assets/4acca5e7-1365-4c6e-8ec1-1302229ee366" />

✅ Final Flow
Local dev → run ingestion, preprocessing, training, Flask app
Push code to GitHub
Jenkins (DinD) → build venv, run tests, build Docker, push to GCR
Deploy to Cloud Run
MLflow logs experiments and artifacts
DVC manages dataset versions
Flask app serves predictions
