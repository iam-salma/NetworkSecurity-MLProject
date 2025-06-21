# 🛡️ Phishing URL Detection

This project implements a robust machine learning model designed to accurately detect phishing URLs by analyzing a diverse set of URL and website features. The goal is to enhance cybersecurity by identifying potentially malicious URLs before they can cause harm.

## 📊 Data Description

The input dataset (located in the `valid_data/` directory) contains engineered features representing various characteristics of URLs. Each feature is encoded as:

- `1` → Positive or benign attribute  
- `0` → Neutral or unknown attribute  
- `-1` → Negative or suspicious attribute

These feature vectors are used by the model to classify each URL as:

- `1` → Phishing  
- `0` → Legitimate

## 🔁 Project Workflow

1. Load and preprocess the validated URL feature dataset i.e. valid_data/test.csv
2. Use a trained machine learning model to assess phishing risk.
3. Saves predictions to `predicted_output/output.csv` for review and further analysis.

## 📈 Insights & Performance Report

- ✅ **Accuracy**: ~92%
- 📌 **Precision and Recall**: Over 90%
- 🔍 **Key Predictors**: SSL certificate status, URL length, domain registration length
- 📦 Handles a broad spectrum of phishing tactics for generalized robustness

This model serves as an automated solution for phishing URL detection, enabling proactive defense in cybersecurity systems.

## 🚀 Deployment

The model and application were containerized and deployed using:

- **Docker**: For consistent containerized environment
- **AWS ECR**: To store and manage Docker images
- **AWS EC2**: As the hosting server to run the container in production
