# Troubleshooting Guide - TA Content Quality Analysis MCP

🔧 **Complete troubleshooting guide** for getting the Content Quality Analysis MCP working with Claude Desktop

---

## 📋 Quick Checklist

Before diving into specific issues, verify these basics:

✅ **Claude Desktop installed** and running  
✅ **Node.js 18+** installed (`node --version`)  
✅ **Python 3.8+** installed (`python3 --version`)  
✅ **chromadb installed** (`pip3 install chromadb`)  
✅ **MCP server files** in correct location  
✅ **Claude Desktop config** properly formatted  

---

## 🚨 Common Issues & Exact Solutions

### "ta-content-quality-analysis server is disconnected"

This is the most common issue. Here's what we learned fixes it:

#### ✅ **Solution 1: Exact File Paths Required**
Your Claude Desktop config MUST use absolute paths, not relative ones:

**❌ Wrong:**
```json
{
  "mcpServers": {
    "ta-content-quality-analysis": {
      "command": "node",
      "args": ["src/index.js"]
    }
  }
}
```

**✅ Correct:**
```json
{
  "mcpServers": {
    "ta-content-quality-analysis": {
      "command": "node",
      "args": ["/Users/andrewansley/Desktop/ta-content-quality-analysis/src/index.js"],
      "env": {
        "PYTHON_PATH": "/Users/andrewansley/Desktop/ta-content-quality-analysis/venv312/bin/python"
      }
    }
  }
}
```

#### ✅ **Solution 2: Python Virtual Environment Required**
MCP servers need a dedicated Python virtual environment with chromadb installed:

```bash
# Create virtual environment (exactly venv312)
cd /Users/andrewansley/Desktop/ta-content-quality-analysis
python3 -m venv venv312

# Activate and install dependencies
source venv312/bin/activate
pip install chromadb

# Verify installation
venv312/bin/python -c "import chromadb; print('ChromaDB installed successfully')"
```

#### ✅ **Solution 3: Environment Variable Pattern**
Claude Desktop configs need the `PYTHON_PATH` environment variable pointing to the venv Python:

```json
"env": {
  "PYTHON_PATH": "/Users/andrewansley/Desktop/ta-content-quality-analysis/venv312/bin/python"
}
```

---

## 🎯 Step-by-Step Verification

### Step 1: Verify MCP Server Structure
Your folder should look exactly like this:
```
/Users/andrewansley/Desktop/ta-content-quality-analysis/
├── src/
│   └── index.js
├── tools/
│   └── content-quality-analyzer.py
├── venv312/
│   ├── bin/
│   │   └── python
│   └── [other venv files]
├── package.json
└── TROUBLESHOOTING.md
```

### Step 2: Test Python Script Directly
```bash
cd /Users/andrewansley/Desktop/ta-content-quality-analysis
./venv312/bin/python tools/content-quality-analyzer.py --help
```

**Expected output:** Help text showing available options
**If error:** Check chromadb installation in venv

### Step 3: Test Node.js Server
```bash
cd /Users/andrewansley/Desktop/ta-content-quality-analysis
node src/index.js
```

**Expected output:** "Content Quality Analysis MCP server running on stdio"
**If error:** Check package.json dependencies

### Step 4: Verify Claude Desktop Config Location
**Mac:** `/Users/[username]/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

### Step 5: Test Config Syntax
```bash
# Validate JSON syntax
cat "/Users/andrewansley/Library/Application Support/Claude/claude_desktop_config.json" | python3 -m json.tool
```

**Expected:** Clean JSON output
**If error:** Fix JSON syntax issues

---

## 📂 Exact File Locations

### Required File Structure:
```
ta-content-quality-analysis/
├── src/index.js                    # MCP server (EXACT path in config)
├── tools/content-quality-analyzer.py # Python analyzer
├── venv312/bin/python              # Virtual environment Python
├── package.json                    # Node dependencies
└── node_modules/                   # Installed after npm install
```

### Claude Desktop Config Location:
```bash
# Mac
/Users/[USERNAME]/Library/Application Support/Claude/claude_desktop_config.json

# Windows  
C:\Users\[USERNAME]\AppData\Roaming\Claude\claude_desktop_config.json
```

---

## 🔧 Complete Working Configuration

### Perfect Claude Desktop Config:
```json
{
  "mcpServers": {
    "ta-content-quality-analysis": {
      "command": "node",
      "args": ["/Users/andrewansley/Desktop/ta-content-quality-analysis/src/index.js"],
      "env": {
        "PYTHON_PATH": "/Users/andrewansley/Desktop/ta-content-quality-analysis/venv312/bin/python"
      }
    }
  }
}
```

### Key Configuration Rules:
1. **Absolute paths only** - never use relative paths
2. **venv312 directory name** - matches working pattern
3. **PYTHON_PATH environment variable** - points to venv python
4. **No extra environment variables** - keep it simple

---

## 🐛 Debugging Commands

### Check if MCP server is reachable:
```bash
# Navigate to project
cd /Users/andrewansley/Desktop/ta-content-quality-analysis

# Test direct execution
node src/index.js

# Test Python path
ls -la venv312/bin/python

# Test Python imports
./venv312/bin/python -c "import chromadb; print('OK')"
```

### Check Claude Desktop logs:
**Mac:**
```bash
tail -f ~/Library/Logs/Claude/claude.log
```

**Windows:**
```cmd
type "%USERPROFILE%\AppData\Local\Claude\Logs\claude.log"
```

### Validate JSON config:
```bash
cat "/Users/andrewansley/Library/Application Support/Claude/claude_desktop_config.json" | jq .
```

---

## 🔧 Tools Connect But Fail to Execute

### "MCP server connected but tools return errors"

If your MCP server shows as connected in Claude Desktop but the tools fail when you try to use them:

#### ✅ **Test Python Script Directly**
First verify the Python analyzer works standalone:
```bash
cd /Users/andrewansley/Desktop/ta-content-quality-analysis
./venv312/bin/python tools/content-quality-analyzer.py --help
```

**Expected:** Help text with usage information
**If fails:** Check chromadb installation in venv

#### ✅ **Test with Your Chroma Database**
```bash
# List collections (replace path with your chroma location)
./venv312/bin/python tools/content-quality-analyzer.py --chroma-dir /Users/andrewansley/Desktop/chroma-test

# Test analysis
./venv312/bin/python tools/content-quality-analyzer.py your_collection_name --chroma-dir /Users/andrewansley/Desktop/chroma-test --mode auto --verbose
```

#### ✅ **Fix Default Paths in MCP Server**
The MCP server needs to know where your Chroma database is located. Update the default paths in `src/index.js`:

```javascript
// Change from:
chroma_directory = '.',

// To your actual chroma path:
chroma_directory = '/Users/andrewansley/Desktop/chroma-test',
```

#### ✅ **Test MCP Server Startup**
```bash
cd /Users/andrewansley/Desktop/ta-content-quality-analysis
echo "test" | node src/index.js
```

**Expected:** "Content Quality Analysis MCP server running on stdio"
**If fails:** Check Node.js dependencies with `npm install`

#### ✅ **Auto-Save Feature**
The Python analyzer now automatically saves results to JSON files locally:

**How it works:**
- Every successful analysis automatically saves to: `collection_mode_timestamp.json`
- Files are saved in the MCP server directory: `/Users/andrewansley/Desktop/ta-content-quality-analysis/`
- No need to specify save parameters - it happens automatically
- Contains full analysis data for further processing

**Example saved file:**
```
dallas_plumbing_homepage_website_20250827_164545.json
```

**Note:** The `save_results` parameter was removed from MCP tools since auto-save handles this better

---

## ⚡ Quick Fixes

### "Python not found"
```bash
# Recreate venv with correct name
cd /Users/andrewansley/Desktop/ta-content-quality-analysis
rm -rf venv312
python3 -m venv venv312
source venv312/bin/activate
pip install chromadb
```

### "Module chromadb not found"
```bash
# Install in the correct venv
cd /Users/andrewansley/Desktop/ta-content-quality-analysis
./venv312/bin/pip install chromadb
```

### "JSON config errors"
Use an online JSON validator to check your config file syntax.

### "Permission denied"
```bash
# Make files executable
chmod +x /Users/andrewansley/Desktop/ta-content-quality-analysis/src/index.js
chmod +x /Users/andrewansley/Desktop/ta-content-quality-analysis/venv312/bin/python
```

---

## 🚀 Testing Your Setup

Once everything is configured, test in Claude Desktop:

1. **Look for 🔨 tools icon** in chat input
2. **Click it** - should show Content Quality Analysis tools
3. **Test command:** "List available analysis tools"
4. **Expected:** Help text with available analysis modes

### Test Analysis:
```
Create a test collection and run analysis:

analyze_content_quality(
  collection_name: "test",
  analysis_mode: "auto"
)
```

---

## 📞 Still Having Issues?

### Check These Patterns:
- **Working MCP servers use `venv312`** - not `venv` or other names
- **All paths must be absolute** - relative paths cause disconnection
- **Environment variables are key** - PYTHON_PATH points to venv
- **Restart Claude Desktop completely** after config changes

### Debug Information to Collect:
1. **Exact error message** from Claude Desktop
2. **Your complete claude_desktop_config.json**
3. **Output of:** `ls -la /path/to/your/ta-content-quality-analysis/`
4. **Output of:** `./venv312/bin/python --version`
5. **Output of:** `node src/index.js` (from project directory)

---

## 💡 Key Learnings

What we discovered works:
1. **Exact file paths** in args (not relative)
2. **Virtual environment** named exactly `venv312`
3. **PYTHON_PATH environment variable** pointing to venv python
4. **Minimal configuration** - don't overcomplicate with extra env vars
5. **Complete restart** of Claude Desktop after config changes

This pattern works because it matches successful MCP servers like `topicatlas-local` that use the same architecture.

---

**🎉 Following these exact patterns should get your MCP server connected and working perfectly!**