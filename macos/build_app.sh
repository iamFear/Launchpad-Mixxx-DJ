#!/bin/bash
# Build a double-clickable Launchpad-Mixxx-DJ.app wrapping the emulator.
# Usage: bash macos/build_app.sh   (output: dist/Launchpad-Mixxx-DJ.app)
set -e
cd "$(dirname "$0")/.."
APP="dist/Launchpad-Mixxx-DJ.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp -R src "$APP/Contents/Resources/src"

PYTHON_BIN="$(command -v python3)"
cat > "$APP/Contents/MacOS/Launchpad-Mixxx-DJ" <<EOF
#!$PYTHON_BIN
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "Resources", "src"))
from launchpad_mixxx.emulator import main
main()
EOF
chmod +x "$APP/Contents/MacOS/Launchpad-Mixxx-DJ"

cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>Launchpad-Mixxx-DJ</string>
    <key>CFBundleIdentifier</key><string>dj.launchpad.mixxx-bridge</string>
    <key>CFBundleVersion</key><string>0.1.0</string>
    <key>CFBundleShortVersionString</key><string>0.1.0</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleExecutable</key><string>Launchpad-Mixxx-DJ</string>
    <key>NSHighResolutionCapable</key><true/>
    <key>LSMinimumSystemVersion</key><string>13.0</string>
</dict>
</plist>
EOF
echo "Built $APP ($(du -sh "$APP" | cut -f1)) with $PYTHON_BIN"
