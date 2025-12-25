#!/bin/bash
# Script to set up SSH for GitHub

echo "Your SSH public key:"
cat ~/.ssh/id_ed25519.pub
echo ""
echo "=========================================="
echo "Copy the key above, then:"
echo "1. Go to: https://github.com/settings/keys"
echo "2. Click 'New SSH key'"
echo "3. Title: MacBook"
echo "4. Paste the key"
echo "5. Click 'Add SSH key'"
echo ""
echo "After adding the key, run:"
echo "  cd /Users/hae/Documents/Vidmore"
echo "  git remote set-url origin git@github.com:candoo10001/yutu.git"
echo "  git push -u origin main"

