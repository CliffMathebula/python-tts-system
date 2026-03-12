#!/bin/bash
echo "🚀 Starting Neural TTS Setup..."

# Check for Python 3.11
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 not found. Please install it: sudo apt install python3.11"
    exit 1
fi

# Create venv
echo "📦 Creating Virtual Environment (venv311)..."
python3.11 -m venv venv311
source venv311/bin/activate

# Install core AI engine
echo "📥 Installing Torch and Neural dependencies..."
pip install --upgrade pip
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Final permissions
chmod +x clone_test.sh speak.sh make_sample.py

echo "✅ Setup complete! To start, run:"
echo "source venv311/bin/activate"
echo "python main.py"
