#!/bin/bash

# List of models to test
MODELS=("gemma2:27b" "llama3.2:latest" "mistral-nemo:latest" "phi3:3.8b" "phi3:14b" "aya-expanse:32b")

# Directories containing email files
SAFE_DIR="../data/safe"
MALICIOUS_DIR="../data/malicious"

for MODEL in "${MODELS[@]}"; do
  echo "🧠 Testing model: $MODEL"
  
  echo "😇 Processing SAFE emails..."
  SAFE_OUTPUT_FILE="test_safe_${MODEL//:/_}.log"
  : > "$SAFE_OUTPUT_FILE"
  for FILE in "$SAFE_DIR"/*; do
    if [[ -f "$FILE" ]]; then
      echo "📩 Processing $FILE"
      python main.py -m "$MODEL" "$FILE" >> "$SAFE_OUTPUT_FILE"
    fi
  done
  
  echo "😈 Processing MALICIOUS emails..."
  MALICIOUS_OUTPUT_FILE="test_malicious_${MODEL//:/_}.log"
  : > "$MALICIOUS_OUTPUT_FILE"
  for FILE in "$MALICIOUS_DIR"/*; do
    if [[ -f "$FILE" ]]; then
      echo "📩 Processing $FILE"
      python main.py -m "$MODEL" "$FILE" >> "$MALICIOUS_OUTPUT_FILE"
    fi
  done
done



echo "✅ Testing complete."
