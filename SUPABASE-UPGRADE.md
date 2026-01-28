# Supabase SDK Upgrade Guide

## Issue

The newer Supabase API uses a different key format:
- **Old format:** JWT tokens starting with `eyJ...` (200+ chars)
- **New format:** Keys like `sb_publishable_...` (shorter)

Your key is the new format, but we're using the old Supabase SDK (2.3.4).

---

## Solution: Upgrade Supabase SDK

### Step 1: Upgrade the package

Run this command in your terminal:

```bash
cd "/Users/anas/Documents/Ops on Opus/Content Automation"
source venv/bin/activate
pip install --upgrade supabase
```

This will install the latest version (likely 2.13+ or newer).

---

### Step 2: Verify the installation

```bash
pip show supabase
```

Should show version 2.10.0 or higher.

---

### Step 3: Test the connection

```bash
python main.py test
```

Should now connect successfully to Supabase!

---

## Alternative: Specific Version

If you want a specific stable version:

```bash
pip install --upgrade "supabase==2.13.0"
```

---

## What Changed in Newer Supabase SDK

### Key Format
- **Old:** JWT tokens (anon key)
- **New:** Publishable API keys (`sb_publishable_...`)

### Import Changes (if any)
The newer SDK might have slightly different imports, but the basic usage remains the same:

```python
from supabase import create_client, Client

client = create_client(
    supabase_url="https://xxx.supabase.co",
    supabase_key="sb_publishable_..."  # New format works!
)
```

---

## If You Get Import Errors

If after upgrading you see import errors, we may need to update the code. Common changes:

### Old SDK (2.3.4):
```python
from supabase import create_client, Client
```

### New SDK (2.10+):
```python
from supabase import create_client, Client
# Usually the same, but check the docs if issues
```

---

## Compatibility Check

Our current code should work with both old and new SDK versions because we use the standard `create_client()` pattern.

**The database.py code:**
```python
from supabase import create_client, Client

self.client: Client = create_client(
    settings.supabase_url,
    settings.supabase_key
)
```

This is compatible with both SDK versions.

---

## Troubleshooting

### SSL Certificate Error (macOS)

If you see SSL errors when installing:

**Option 1:** Update certificates
```bash
/Applications/Python\ 3.14/Install\ Certificates.command
```

**Option 2:** Use pip with trusted host (not recommended for production)
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade supabase
```

**Option 3:** Install via requirements.txt
```bash
pip install --upgrade -r requirements.txt
```

---

## Summary

1. ✅ Your Supabase key format is **correct** for newer versions
2. ✅ Updated `requirements.txt` to `supabase>=2.10.0`
3. ⚙️ **You need to run:** `pip install --upgrade supabase`
4. ✅ Code should work with both old and new SDK versions

**Run the upgrade command now!** 🚀
