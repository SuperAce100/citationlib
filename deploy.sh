#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
print_status() {
    echo -e "${GREEN}==>${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
else
    print_error "Virtual environment not found. Please create one first."
    exit 1
fi

# Check if all required tools are installed
print_status "Checking required packages..."
pip install --quiet --upgrade pip build twine

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build package
print_status "Building package..."
python -m build

# Function to handle package upload
upload_package() {
    local repo=$1
    local repo_url=$2
    
    print_status "Uploading to $repo..."
    if python -m twine upload --repository $repo dist/*; then
        print_status "Successfully uploaded to $repo!"
    else
        print_error "Failed to upload to $repo"
        exit 1
    fi
}

# Ask user where to upload
echo
echo "Where would you like to upload the package?"
echo "1) TestPyPI (test.pypi.org)"
echo "2) PyPI (pypi.org)"
echo "3) Both TestPyPI and PyPI"
echo "4) Exit without uploading"
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        upload_package "testpypi" "https://test.pypi.org/legacy/"
        print_status "Test installation command:"
        echo "pip install --index-url https://test.pypi.org/simple/ citationlib"
        ;;
    2)
        upload_package "pypi" "https://upload.pypi.org/legacy/"
        print_status "Installation command:"
        echo "pip install citationlib"
        ;;
    3)
        upload_package "testpypi" "https://test.pypi.org/legacy/"
        echo
        upload_package "pypi" "https://upload.pypi.org/legacy/"
        print_status "Installation commands:"
        echo "TestPyPI: pip install --index-url https://test.pypi.org/simple/ citationlib"
        echo "PyPI: pip install citationlib"
        ;;
    4)
        print_status "Build completed. Exiting without upload."
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Deactivate virtual environment
deactivate

print_status "Deployment process completed!" 