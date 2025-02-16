#!/bin/bash

COVERAGE_PATH="./coverage/lcov-report/index.html"

if [ -f "$COVERAGE_PATH" ]; then
  echo -e "\n✅ Coverage report generated! Open it in your browser:\n"
  echo -e "👉 file://$(realpath "$COVERAGE_PATH")\n"

  if command -v xdg-open > /dev/null; then
    xdg-open "$COVERAGE_PATH" # For Linux
  elif command -v open > /dev/null; then
    open "$COVERAGE_PATH" # For macOS
  elif command -v start > /dev/null; then
    start "$COVERAGE_PATH" # For Windows (Git Bash)
  else
    echo "❌ Could not detect a command to open the browser. Please open the file manually."
  fi
else
  echo -e "\n❌ Coverage report not found. Run tests with coverage enabled.\n"
fi
