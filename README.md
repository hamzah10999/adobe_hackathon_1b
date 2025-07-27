
# 📄 Document Intelligence System

This project is an intelligent document analyzer powered by a lightweight language model (TinyLlama) and NLTK. It extracts personalized insights from unstructured text using personas like "Travel Planner", "Legal Expert", and more.

---

## 🚀 Features

- Lightweight model (TinyLlama in GGUF format)
- Persona-based document understanding
- Customizable jobs (e.g., travel planning, summaries, legal advice)
- Supports JSON output
- Fully Dockerized for easy deployment

---

## 📁 Project Structure

```

├── main.py                 # Entry point for running the system
├── requirements.txt        # Python dependencies
├── setup.sh                # Shell script to download model and setup environment
├── Dockerfile              # Docker config to containerize the project
├── input/                  # Folder for input documents
├── output/                 # Folder for storing result JSON
└── models/                 # Folder for downloaded TinyLlama model (.gguf)

````

---

## ⚙️ Setup Instructions

You can run this project in **two ways**:

### 🧪 Option 1: Run Locally (Mac/Linux)

> Recommended for quick testing on your machine.

```bash
# Clone the repository
git clone https://github.com/zealot-zew/Adobe-1b.git
cd Adobe-1b

# Run setup (downloads model, creates virtualenv, installs deps)
bash setup.sh

# Run the system
python main.py \
  --input-dir ./input \
  --persona "Travel Planner" \
  --job "Plan a 4-day trip for 10 college friends" \
  --output ./output/result.json
````

---

### 🐳 Option 2: Run with Docker

> No Python or local setup needed. Just Docker.

#### ✅ Step 1: Build Docker Image

```bash
docker build -t adobe-1b .
```

#### ✅ Step 2: Run the App



```bash
chmod -R 777 output

docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  adobe-1b \
  --input-dir ./input \
  --persona "Travel Planner" \
  --job "Plan a 4-day trip for 10 college friends" \
  --output ./output/result.json

```
---

## 📦 What `setup.sh` Does

The `setup.sh` script automates setup:

* Installs `wget` if not installed (for macOS)
* Creates `input`, `output`, and `models` folders
* Downloads TinyLlama model (.gguf format)
* Sets up a Python virtual environment
* Installs all Python dependencies
* Downloads NLTK tokenizer (`punkt`)

---

## 🛠 Requirements

If you're not using Docker, you'll need:

* Python 3.8+
* pip
* wget
* Virtualenv (optional but recommended)

---

## ✍️ Example Use Cases

* `Legal Expert`: Summarize legal documents
* `Finance Advisor`: Extract spending patterns from receipts
* `Travel Planner`: Create itineraries from unstructured text

---

## 📌 Custom Jobs

You can modify the persona and job like this:

```bash
python main.py \
  --input-dir ./input \
  --persona "Legal Expert" \
  --job "Summarize key clauses in this contract" \
  --output ./output/legal_summary.json
```
