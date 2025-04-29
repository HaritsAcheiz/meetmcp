#!/bin/bash
set -e

# Print environment information for debugging
echo "Starting MCP Client application..."
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"

# Activate virtual environment
echo "Activating virtual environment..."
source ./.venv/bin/activate

# Verify Streamlit is available
if ! command -v streamlit &> /dev/null; then
    echo "ERROR: Streamlit command not found. Please check the virtual environment installation."
    exit 1
fi

echo "Streamlit version: $(streamlit --version)"

# Execute Streamlit with proper arguments
echo "Starting Streamlit server..."
exec streamlit run mcp_client_ui.py "$@"