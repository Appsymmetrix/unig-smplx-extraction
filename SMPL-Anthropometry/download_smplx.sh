#!/bin/bash

set -e  # stop script if any command fails

echo "🚀 Downloading SMPLX model from S3..."

# Create target directory
mkdir -p models/smplx

# Temporary download location
ZIP_FILE="smplx_models.zip"

# Download from S3 (IAM auth required)
aws s3 cp s3://unig-smplx-models/smplx_models.zip $ZIP_FILE

echo "📦 Unzipping..."
unzip -o $ZIP_FILE -d models/smplx

echo "🧹 Cleaning up..."
rm $ZIP_FILE

echo "✅ All files have been moved to: models/smplx/"
echo "Done!"
