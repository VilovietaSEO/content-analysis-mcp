# Complete Setup Guide - Content Analysis MCP

This guide will walk you through setting up the Content Analysis MCP from scratch, including all prerequisites.

## 📋 What You'll Need

- A computer (Mac or Windows)
- Internet connection
- 15 minutes for complete setup

---

## 🖥️ Step 1: Install Python

### For Mac Users

#### Option A: Using Homebrew (Recommended)
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Verify installation
python3 --version
```

#### Option B: Direct Download
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. Verify: `python3 --version`

### For Windows Users

1. **Download Python** from [python.org](https://www.python.org/downloads/)
2. **Run the installer** 
3. **⚠️ IMPORTANT**: Check "Add Python to PATH" during installation
4. **Open Command Prompt** (Win + R, type "cmd", press Enter)
5. **Verify installation:**
   ```cmd
   python --version
   ```

---

## 🛠️ Step 2: Install UV Package Manager

### For Mac Users
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart Terminal or reload shell
source ~/.zshrc

# Verify installation
uvx --version
```

### For Windows Users
```cmd
# Install uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Restart Command Prompt

# Verify installation
uvx --version
```

---

## 🎨 Step 3: Setup Claude Desktop

### Install Claude Desktop
1. Download from [claude.ai/desktop](https://claude.ai/desktop)
2. Install and create an account
3. Open Claude Desktop

### Configure Chroma MCP

1. **Open Claude Desktop Settings:**
   - Click **Claude menu** → **Settings**
   - Click **Developer** in sidebar
   - Click **Edit Config**

2. **Add Chroma MCP configuration:**
   ```json
   {
     "mcpServers": {
       "chroma": {
         "command": "uvx",
         "args": [
           "chroma-mcp",
           "--client-type",
           "persistent",
           "--data-dir",
           "/path/to/your/chroma-folder"
         ]
       }
     }
   }
   ```

3. **Set your data directory path:**
   - **Mac Example**: `/Users/yourname/Documents/chroma-data`
   - **Windows Example**: `C:\\Users\\yourname\\Documents\\chroma-data`

4. **Create the data directory:**
   ```bash
   # Mac
   mkdir -p /Users/yourname/Documents/chroma-data
   
   # Windows
   mkdir C:\Users\yourname\Documents\chroma-data
   ```

5. **Restart Claude Desktop completely**

6. **Verify setup:**
   - Look for 🔨 hammer icon in chat input
   - Click it to see Chroma tools available

---

## 📊 Step 4: Install Content Quality Analyzer

### Download the Script

#### Option A: Direct Download
```bash
# Navigate to your chroma data folder
cd /Users/yourname/Documents/chroma-data  # Mac
cd C:\Users\yourname\Documents\chroma-data  # Windows

# Download the analyzer
curl -O https://raw.githubusercontent.com/yourusername/content-analysis-mcp/main/analyze_content_quality.py

# Make executable (Mac/Linux only)
chmod +x analyze_content_quality.py
```

#### Option B: Clone Repository
```bash
# Clone the entire repository
git clone https://github.com/yourusername/content-analysis-mcp.git

# Copy the script to your chroma folder
cp content-analysis-mcp/analyze_content_quality.py /path/to/your/chroma-data/
```

### Install Python Dependencies

```bash
# Install required packages
pip install chromadb

# Verify installation
python -c "import chromadb; print('ChromaDB installed successfully!')"
```

---

## 🚀 Step 5: Test Your Setup

### Add Test Content in Claude Desktop

```javascript
// Create a test collection
chroma_create_collection(name: "test_analysis")

// Add sample content
chroma_add_documents(
  collection_name: "test_analysis",
  documents: [
    "This is a well-structured article about digital marketing. It provides specific, actionable insights for businesses looking to improve their online presence. The content flows logically from introduction to conclusion, maintaining consistent focus throughout.",
    "Contact us today! We're the best! Really amazing stuff here. Call now!!!"
  ],
  metadatas: [
    {"heading": "Digital Marketing Guide", "type": "article"},
    {"heading": "Contact Page", "type": "cta"}
  ],
  ids: ["doc1", "doc2"]
)
```

### Run the Analyzer

```bash
# Navigate to your chroma folder
cd /Users/yourname/Documents/chroma-data

# Run the analyzer
python analyze_content_quality.py test_analysis
```

### Expected Output

You should see something like:
```
🎯 CONTENT QUALITY ANALYSIS REPORT
Collection: test_analysis
Documents: 2

📈 COLLECTION AVERAGES:
  Overall Quality:        0.642 (Range: 0.234 - 0.851)
  Word Precision:         0.578 (Range: 0.123 - 0.834)
  ...

🏆 BEST DOCUMENT (Score: 0.851):
  Heading: Digital Marketing Guide

⚠️  NEEDS IMPROVEMENT (Score: 0.234):
  Heading: Contact Page
```

---

## 🆘 Troubleshooting

### `uvx: command not found`

**Mac:**
```bash
# Reload shell configuration
source ~/.zshrc
# or
source ~/.bash_profile

# If still not working, try full path
which uvx
# Use the full path in your Claude config
```

**Windows:**
```cmd
# Restart Command Prompt completely
# If still not working, find uvx location:
where uvx
# Use the full path in your Claude config
```

### `python: command not found`

**Mac:**
```bash
# Try python3 instead
python3 --version

# If that works, create an alias
echo "alias python=python3" >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
- Reinstall Python and ensure "Add Python to PATH" is checked
- Restart Command Prompt after reinstall

### Claude Desktop Can't Connect to Chroma

1. **Check your config file syntax** (valid JSON)
2. **Ensure data directory exists** and path is correct
3. **Use forward slashes** `/` in paths (even on Windows)
4. **Restart Claude Desktop** after config changes
5. **Check Claude logs** for specific errors:
   - **Mac**: `~/Library/Logs/Claude/mcp*.log`
   - **Windows**: `%APPDATA%\Claude\logs\mcp*.log`

### ChromaDB Import Error

```bash
# Ensure you're using the right pip
pip --version

# If multiple Python versions, be specific
pip3 install chromadb

# Or use uv for cleaner dependency management
uvx pip install chromadb
```

### Permission Errors (Mac/Linux)

```bash
# Make script executable
chmod +x analyze_content_quality.py

# If still issues, run with python explicitly
python analyze_content_quality.py
```

---

## 💡 Pro Tips

### Workflow Optimization

1. **Batch Content Addition:**
   ```javascript
   // Add multiple competitor pages at once
   chroma_add_documents(
     collection_name: "competitors",
     documents: [content1, content2, content3],
     metadatas: [meta1, meta2, meta3],
     ids: ["comp1", "comp2", "comp3"]
   )
   ```

2. **Regular Analysis:**
   ```bash
   # Set up a simple script for regular analysis
   #!/bin/bash
   cd /path/to/chroma-data
   python analyze_content_quality.py all_competitors --save-json "results_$(date +%Y%m%d).json"
   ```

3. **Competitive Intelligence:**
   ```bash
   # Compare before and after content updates
   python analyze_content_quality.py before_update --save-json before.json
   python analyze_content_quality.py after_update --save-json after.json
   ```

### Advanced Usage

```bash
# Custom data directory
python analyze_content_quality.py --data-dir /custom/path collection_name

# Help and options
python analyze_content_quality.py --help

# Analyze all collections and save results
python analyze_content_quality.py --save-json full_analysis.json
```

---

## 📞 Getting Help

If you're still stuck:

1. **Check the troubleshooting section above**
2. **Create an issue** on GitHub with:
   - Your operating system and version
   - Python version (`python --version`)
   - Complete error messages (copy/paste)
   - What step you're stuck on
3. **Include relevant log files** if available

---

**🎉 Congratulations!** You're now ready to analyze content like a pro. Start by adding some competitor content to Chroma and running your first analysis!