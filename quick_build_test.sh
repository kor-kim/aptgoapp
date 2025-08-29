#!/bin/bash
# Quick build verification for Android aptgoapp project
# Tests that the changes compile correctly

echo "🔧 Android aptgoapp Build Verification"
echo "======================================"

# Change to project directory
cd /Users/dragonship/파이썬/aptgoapp

# Check if gradlew exists
if [ ! -f "./gradlew" ]; then
    echo "❌ Error: gradlew not found in project directory"
    exit 1
fi

# Make gradlew executable
chmod +x ./gradlew

echo "📦 Building Android project..."

# Clean build
echo "🧹 Cleaning previous build..."
./gradlew clean

# Build the project
echo "🏗️ Compiling Android app..."
./gradlew assembleDebug

# Check build result
if [ $? -eq 0 ]; then
    echo "✅ Build successful! APK ready for emulator testing."
    echo ""
    echo "📱 Generated APK location:"
    find . -name "*.apk" -type f | head -5
    echo ""
    echo "🚀 Ready for emulator testing with:"
    echo "   - Login: newtest1754832743"
    echo "   - Password: admin123"
    echo "   - Server: https://aptgo.org/"
else
    echo "❌ Build failed. Check error messages above."
    exit 1
fi