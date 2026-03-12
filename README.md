

```markdown
# 🚀 Neural TTS & Voice Cloning API

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

### 🏗️ System Architecture

The platform is designed with a decoupled architecture to separate lightweight edge-streaming from heavy neural processing:

* **API Layer:** FastAPI provides an asynchronous interface for handling metadata and audio uploads.
* **Edge-TTS Integration:** Low-latency neural voices (ZA/US) provided via Microsoft's cloud-based engine.
* **Neural Engine (XTTS-v2):** A GPT-based local model that uses a 10-second reference sample to clone unique vocal characteristics.
* **Execution Provider:** Automatically detects NVIDIA CUDA cores for GPU acceleration, falling back to CPU if necessary.

---

### 🛠️ Quick Start (Local Setup)

#### 1. Clone & Environment Setup

```bash
git clone [https://github.com/CliffMathebula/python-tts-system.git](https://github.com/CliffMathebula/python-tts-system.git)
cd python-tts-system

# Create a Python 3.11 virtual environment
python3.11 -m venv venv311
source venv311/bin/activate

```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
# Install Torch with CUDA 12.1 support
pip install torch torchaudio --index-url [https://download.pytorch.org/whl/cu121](https://download.pytorch.org/whl/cu121)
# Install requirements
pip install -r requirements.txt

```

#### 3. Run the Server

```bash
python main.py

```

*Note: On the first run, the system will download the 2GB XTTS-v2 model. You will be prompted to accept the CPML license (Type 'y').*

---

### 🐳 Docker Setup (Recommended)

This project includes a production-ready Dockerfile optimized for GPU acceleration.

#### 1. Build the Image

```bash
docker build -t python-tts-system .

```

#### 2. Run the Container

**With GPU Support (Requires NVIDIA Container Toolkit):**

```bash
docker run --gpus all -p 8000:8000 python-tts-system

```

**CPU Only Mode:**

```bash
docker run -p 8000:8000 python-tts-system

```

---

### 🧪 Testing the API

Once the server is running, you can use the included shell scripts to test the endpoints.

#### Standard TTS Test

```bash
chmod +x speak.sh
./speak.sh

```

#### Voice Cloning Test

Ensure you have a 10-second `.wav` file ready as a reference (e.g., `sample.wav`).

```bash
chmod +x clone_test.sh
./clone_test.sh

```

---

### 🎙️ API Capabilities

| Feature | Engine | Use Case |
| --- | --- | --- |
| **Standard TTS** | Edge-TTS | Fast, high-quality narrations (ZA/US voices). |
| **Voice Cloning** | XTTS-v2 | Professional-grade cloning from a 10s audio sample. |
| **Multi-Language** | Neural Engine | Supports English, Spanish, French, and more. |

---

### 💡 Portfolio Highlights

* **Architecture:** Utilizes a FastAPI wrapper around a PyTorch backend, demonstrating the ability to productionize complex AI models.
* **DevOps Ready:** Fully containerized with Docker support for both CUDA-accelerated and CPU-only environments.
* **Demo:** (Optional) Add a link here to a recording of a 10-second clip of a cloned voice to showcase audio quality.

---

### 📜 License

This project uses **Coqui XTTS-v2**, which is released under the **Coqui Public Model License (CPML)**. Please ensure you read and agree to their terms for non-commercial use.

```