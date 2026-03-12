

## 🚀 Neural TTS & Voice Cloning API

A high-performance Text-to-Speech API built with **FastAPI**, featuring standard neural voices via `edge-tts` and advanced **Zero-Shot Voice Cloning** using `Coqui XTTS-v2`.

### 📋 Prerequisites

Before setting up the project, ensure your system meets the following requirements:

#### 1. Hardware Recommendations

* **GPU:** NVIDIA GPU with 4GB+ VRAM (Highly Recommended for real-time cloning).
* **RAM:** 8GB Minimum (16GB Recommended).
* **Disk Space:** ~3GB for model weights and dependencies.

#### 2. System Software

* **OS:** Ubuntu 22.04 / 24.04 (Linux is preferred for AI/CUDA compatibility).
* **Python 3.11:** The "sweet spot" for AI libraries. *Note: Python 3.12 is currently not supported by some core dependencies.*
* **FFmpeg:** Required for audio processing and format conversion.
```bash
sudo apt update && sudo apt install ffmpeg

```


* **CUDA Toolkit (Optional):** If using an NVIDIA GPU, ensure CUDA 11.8 or 12.1 is installed.

---

### 🛠️ Quick Start

#### 1. Clone & Environment Setup

```bash
git clone https://github.com/CliffMathebula/python-tts-system
cd python-tts-system

# Create a Python 3.11 virtual environment
python3.11 -m venv venv311
source venv311/bin/activate

```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
# Install Torch with CUDA 12.1 support
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
# Install requirements
pip install -r requirements.txt

```

#### 3. Run the Server

```bash
python main.py

```

*Note: On the first run, the system will download the 2GB XTTS-v2 model. You will be prompted to accept the CPML license.*

---

### 🎙️ API Capabilities

| Feature | Engine | Use Case |
| --- | --- | --- |
| **Standard TTS** | Edge-TTS | Fast, high-quality narrations (ZA/US voices). |
| **Voice Cloning** | XTTS-v2 | Professional-grade cloning from a 10s audio sample. |
| **Multi-Language** | Neural Engine | Supports English, Spanish, French, and more. |

---

### 📜 License

This project uses **Coqui XTTS-v2**, which is released under the **Coqui Public Model License (CPML)**. Please ensure you read and agree to their terms for non-commercial use.

---

### Tips for your Portfolio:

* **Add a "Demo" Section:** If you can, record a 10-second clip of a cloned voice and upload it to the repo (or a link) so people can hear the quality immediately.
* **Architecture Diagram:** Mentioning that you use a **FastAPI** wrapper around a **PyTorch** backend shows you understand how to productionize AI models.

**Would you like me to help you write a `setup.sh` script that automates all these prerequisite checks and installations for the user?**