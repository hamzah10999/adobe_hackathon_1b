#!/bin/bash

echo "🔧 Setting up Document Intelligence System in Docker..."

# Step 0: Create required folders
mkdir -p models input output

# Step 1: Download TinyLlama model
echo "⬇️  Downloading TinyLlama model..."
wget -O models/tinyllama-1.1b-chat-v1.0.Q4_0.gguf \
  "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf"

# Step 2: Install Python dependencies globally (no venv)
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: Download NLTK tokenizer
echo "🧠 Downloading NLTK tokenizer..."
python -c "import nltk; nltk.download('punkt')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Run the system with:"

echo "python main.py --input-dir ./input --persona 'Travel Planner' --job 'Plan a 4-day trip for 10 college friends' --output ./output/result.json"
