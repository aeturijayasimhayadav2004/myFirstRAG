#!/bin/bash

# Create keystore directory if it doesn't exist
mkdir -p keystore

# Generate a debug keystore
keytool -genkey -v -keystore keystore/debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"

echo "Debug keystore generated at keystore/debug.keystore"
