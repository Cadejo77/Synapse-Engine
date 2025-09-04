#!/bin/bash

echo "=== YAMLPromptMaster Demo ==="
echo
echo "Generating 3 diverse prompts to show the system capabilities:"
echo

npm run gen -- --count 3

echo
echo "=== JSON Output Example ==="
echo "Here's what the structured metadata looks like:"
echo

npm run gen -- --count 1 --json

echo
echo "=== Key Benefits Demo ==="
echo "Notice how each prompt includes:"
echo "• Consistent structure and quality"
echo "• Rich detail across all dimensions" 
echo "• Proper relationship handling"
echo "• Style and composition elements"
echo "• Metadata tags for processing"
echo
echo "This level of systematic quality is difficult to achieve with regular chat!"