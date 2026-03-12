#!/bin/bash

# 1. Fetch voices from your local API and store them in an array
echo "Fetching available voices..."
VOICES_JSON=$(curl -s -G 'http://localhost:8000/voices')

# Use python to extract just the names into a clean list
VOICE_NAMES=($(echo "$VOICES_JSON" | python3 -c "import sys, json; print(' '.join([v['name'] for v in json.load(sys.stdin)]))"))

# 2. Display the list to the user
echo "------------------------------------------"
echo "  SELECT A VOICE FROM THE LIST"
echo "------------------------------------------"
for i in "${!VOICE_NAMES[@]}"; do
  echo "$((i+1))) ${VOICE_NAMES[$i]}"
done
echo "------------------------------------------"

# 3. Get user selection
read -p "Enter the number of your choice: " CHOICE_NUM
SELECTED_VOICE=${VOICE_NAMES[$((CHOICE_NUM-1))]}

if [ -z "$SELECTED_VOICE" ]; then
    echo "Invalid selection. Exiting."
    exit 1
fi

echo "Selected: $SELECTED_VOICE"

# 4. Get the text to speak
echo ""
read -p "What should $SELECTED_VOICE say? " SPEECH_TEXT

# 5. URL Encode the text
ENCODED_TEXT=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$SPEECH_TEXT'''))")

# 6. Run the POST command
echo "Generating audio..."
curl -X 'POST' \
  "http://localhost:8000/speak?text=$ENCODED_TEXT&voice=$SELECTED_VOICE" \
  -H 'accept: application/json' \
  --output test.mp3

echo "------------------------------------------"
echo "Success! Audio saved to test.mp3"