# Simple Setup Guide - Content Analysis MCP

**🎯 Goal:** Get content analysis working in Claude Desktop in 5 minutes - no terminal expertise needed!

---

## 📋 What You'll Have When Done

- Claude Desktop with content analysis superpowers
- Ability to analyze competitor content quality with 1 click
- Professional 5-dimension scoring system
- Instant competitive intelligence

---

## 🚀 Step 1: Install Python (One-Time Setup)

### For Mac Users 🍎
1. **Go to** [python.org/downloads](https://www.python.org/downloads/)
2. **Click** the big "Download Python" button
3. **Run the installer** (click through all the defaults)
4. **Verify it worked:** Open Terminal and type `python3 --version`

### For Windows Users 🪟  
1. **Go to** [python.org/downloads](https://www.python.org/downloads/)
2. **Click** the big "Download Python" button  
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. **Verify it worked:** Open Command Prompt and type `python --version`

---

## 🖥️ Step 2: Setup Claude Desktop + Chroma

### Install Claude Desktop
1. **Download** from [claude.ai/desktop](https://claude.ai/desktop) 
2. **Install** and sign up for an account
3. **Open** Claude Desktop

### Add Chroma MCP to Claude
1. **In Claude Desktop:** Settings ⚙️ → Developer → Edit Config
2. **Replace everything** with this config:

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
        "/Users/yourname/Documents/chroma-data"
      ]
    }
  }
}
```

3. **Change the path:**
   - **Mac:** Use `/Users/YOURNAME/Documents/chroma-data`
   - **Windows:** Use `C:\\Users\\YOURNAME\\Documents\\chroma-data`

4. **Save** and close the config
5. **Restart** Claude Desktop completely

### Create Your Data Folder
- **Mac:** Create a folder at `/Users/yourname/Documents/chroma-data`
- **Windows:** Create a folder at `C:\Users\yourname\Documents\chroma-data`

### Verify It's Working
1. **Open a new chat** in Claude Desktop
2. **Look for** 🔨 hammer icon in the chat input
3. **Click it** - you should see Chroma tools listed!

---

## 📊 Step 3: Add the Content Analyzer

### Download the Analyzer Script
1. **Right-click this link:** [analyze_content_quality.py](https://github.com/VilovietaSEO/content-analysis-mcp/raw/main/analyze_content_quality.py)
2. **Choose "Save Link As"** or "Download Linked File"
3. **Save it** directly into your chroma-data folder:
   - **Mac:** `/Users/yourname/Documents/chroma-data/analyze_content_quality.py`
   - **Windows:** `C:\Users\yourname\Documents\chroma-data\analyze_content_quality.py`

### Install the Required Package
**Mac users:** Open Terminal and run:
```bash
pip3 install chromadb
```

**Windows users:** Open Command Prompt and run:
```cmd
pip install chromadb
```

---

## 🎉 Step 4: Test Everything Works

### Add Test Content in Claude Desktop

**Copy and paste this into Claude Desktop:**

```
Create a test collection and add some sample content:

chroma_create_collection(name: "test_analysis")

chroma_add_documents(
  collection_name: "test_analysis",
  documents: [
    "This comprehensive guide provides specific, actionable strategies for digital marketing success. We definitively outline proven methods that consistently deliver measurable results for businesses.",
    "Contact us today! We're really good! Call now for amazing stuff!"
  ],
  metadatas: [
    {"heading": "Digital Marketing Strategy Guide", "type": "guide"},
    {"heading": "Contact Us", "type": "cta"}
  ],
  ids: ["guide1", "cta1"]
)
```

### Run Your First Analysis

**Then type this in Claude Desktop:**

> Run the content quality analyzer on the test collection. Navigate to my chroma data folder and run: python analyze_content_quality.py test_analysis

You should see a beautiful quality report showing the difference between good and poor content!

---

## 💡 How to Use It Daily

### Typical Workflow in Claude Desktop:

1. **Collect competitor content:**
   > "Scrape this competitor URL and add it to a collection called 'competitors'"

2. **Analyze quality:**
   > "Run the quality analyzer on my competitors collection"

3. **Get insights:**
   > "What are the quality scores telling me? Where are the biggest opportunities?"

4. **Track improvements:**
   > "Add my new content to the collection and compare quality scores"

### You'll Chat Like This:
- **"Analyze the quality of content in my 'legal-competitors' collection"**
- **"Which competitor has the weakest content I can easily beat?"**
- **"Compare my content quality scores to the top 3 competitors"**
- **"What should I improve to get higher quality scores?"**

---

## 🆘 Something Not Working?

### Claude Desktop Shows No 🔨 Icon
- **Check:** Your config file syntax (use a JSON validator)
- **Try:** Restart Claude Desktop completely
- **Fix:** Make sure the data folder path exists

### "uvx command not found"
- **Mac:** Open Terminal, run: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Windows:** Open PowerShell as Admin, run: `irm https://astral.sh/uv/install.ps1 | iex`
- **Then:** Restart Claude Desktop

### Python/pip not found
- **Reinstall Python** from python.org
- **Mac users:** Use `python3` and `pip3` instead of `python` and `pip`
- **Windows users:** Make sure "Add to PATH" was checked during installation

### Script Won't Run
- **Check:** The script is in your chroma-data folder
- **Install:** `pip install chromadb` (or `pip3 install chromadb` on Mac)
- **Path:** Use the full path to your chroma folder

---

## 🎯 Pro Tips

### Organize Your Analysis
- **Create separate collections** for different competitor types
- **Use descriptive names** like "legal-competitors", "saas-competitors"
- **Add metadata** to track competitor names, URLs, dates

### Batch Analysis
- **Add multiple competitor pages** to one collection
- **Run analysis on entire collections** at once
- **Compare scores** across different content types

### Content Strategy
- **Focus on competitors** with scores below 0.6 (easy to beat)
- **Study top performers** with scores above 0.8 
- **Track your progress** by re-analyzing your content after improvements

---

**🎉 Ready to start dominating with data-driven content analysis?**

Your setup is complete! Start by analyzing some competitor content and watch your SEO strategy transform with professional-grade insights.