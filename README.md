# Container Log AI Monitor (MVP)

## Project Title
Design and Implementation of an Intelligent Container Log Monitoring System Using Machine Learning

---

## Goal
Monitor logs from multiple Docker containers running locally, detect abnormal or suspicious behaviour using a hybrid rule-based and machine learning approach, and present structured reports and actionable recommendations through a web dashboard.

This project is a Final Year Project (Projet de Fin d’Études) and is delivered as a functional MVP.

---

## Project Structure
- **lab/**: Docker Compose laboratory with four containers (normal, misconfigured, suspicious, noisy).
- **monitor/**: Runtime monitoring engine (log collection, parsing, feature extraction, rules, AI inference, reporting).
- **training/**: Dataset generation and PyTorch training scripts.
- **models/**: Trained and exported models (TorchScript).
- **dashboard/**: Streamlit web dashboard.
- **outputs/**: Generated reports (`latest_report.json`) and history (`history.jsonl`).

---

## Prerequisites
- Docker Engine with Docker Compose plugin
- Python 3.10 or later
- Git
- Linux/macOS recommended (Windows supported)

---

## Installation
```bash
git clone <repository-url>
cd container-log-ai-monitor

python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .\.venv\Scripts\Activate.ps1     # Windows PowerShell

pip install -r requirements.txt

