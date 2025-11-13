#!/bin/bash

echo "════════════════════════════════════════════════════════════════════"
echo "   🔑 OpenAI API Key Setup"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bash_profile"
else
    SHELL_RC="$HOME/.profile"
fi

echo "📝 This will add your OpenAI API key to: $SHELL_RC"
echo ""

# Check if key already exists in file
if grep -q "OPENAI_API_KEY" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  OPENAI_API_KEY already exists in $SHELL_RC"
    echo ""
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 0
    fi
    # Remove old key
    sed -i.bak '/export OPENAI_API_KEY=/d' "$SHELL_RC"
fi

# Prompt for API key
echo "Enter your OpenAI API key:"
read -s OPENAI_KEY
echo ""

if [ -z "$OPENAI_KEY" ]; then
    echo "❌ No API key provided"
    exit 1
fi

# Add to shell config
echo "" >> "$SHELL_RC"
echo "# OpenAI API Key for Harrison's RAG" >> "$SHELL_RC"
echo "export OPENAI_API_KEY='$OPENAI_KEY'" >> "$SHELL_RC"

# Set for current session
export OPENAI_API_KEY="$OPENAI_KEY"

echo "✅ API key saved to $SHELL_RC"
echo ""
echo "🔄 To use in current terminal, run:"
echo "   source $SHELL_RC"
echo ""
echo "💡 In new terminal windows, it will be available automatically!"
echo ""
echo "════════════════════════════════════════════════════════════════════"

