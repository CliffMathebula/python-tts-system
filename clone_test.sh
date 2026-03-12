#!/bin/bash

# 1. Ask for the text
read -p "What should the cloned voice say? " CLONE_TEXT

# 2. Ask for the path to the voice sample
read -p "Enter path to your voice sample (e.g., sample.wav): " SAMPLE_PATH

# Check if the sample file exists
if [ ! -f "$SAMPLE_PATH" ]; then
    echo "❌ Error: File $SAMPLE_PATH not found!"
    exit 1
fi

echo "Generating cloned audio... (This may take a moment)"

# 3. Run the POST command
curl -X 'POST' \
  'http://localhost:8000/clone' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F "text=$CLONE_TEXT" \
  -F "voice_sample=@$SAMPLE_PATH" \
  -F "language=en" \
  --output test_clone.wav

echo "------------------------------------------"
echo "Success! Playing cloned audio..."

# 4. Play the result immediately
# Note: Since the output is a .wav file, we use 'aplay' (built-in to Ubuntu) 
# or 'ffplay'. mpg123 is primarily for .mp3 files.
aplay test_clone.wav 2>/dev/null || ffplay -nodisp -autoexit test_clone.wav 2>/dev/null

echo "------------------------------------------"