#!/bin/bash
# Fix SSL certificate issues on macOS

echo "🔧 Fixing SSL Certificate Issues..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Install certifi
echo "📦 Installing certifi package..."
pip install --upgrade certifi

# Try to find and run Python's certificate installer
echo ""
echo "🔍 Looking for Python certificate installer..."

# Check common Python installation paths
PYTHON_CERT_INSTALLER=""

if [ -f "/Applications/Python 3.14/Install Certificates.command" ]; then
    PYTHON_CERT_INSTALLER="/Applications/Python 3.14/Install Certificates.command"
elif [ -f "/Library/Frameworks/Python.framework/Versions/3.14/Install Certificates.command" ]; then
    PYTHON_CERT_INSTALLER="/Library/Frameworks/Python.framework/Versions/3.14/Install Certificates.command"
fi

if [ -n "$PYTHON_CERT_INSTALLER" ]; then
    echo "✅ Found certificate installer: $PYTHON_CERT_INSTALLER"
    echo "📥 Running certificate installer..."
    bash "$PYTHON_CERT_INSTALLER"
else
    echo "⚠️  Python certificate installer not found"
    echo "   Certifi package installed as alternative"
fi

echo ""
echo "🧪 Testing SSL setup..."
python -c "
import ssl
import certifi
print('✅ SSL Default Context:', ssl.create_default_context().check_hostname)
print('✅ Certifi Path:', certifi.where())
print('')
print('SSL setup complete!')
"

echo ""
echo "✅ SSL fix complete!"
echo ""
echo "Now run: python scripts/test_rss.py"
