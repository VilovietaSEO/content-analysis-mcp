# Content Quality Analysis MCP for Claude Desktop

A simple MCP server that analyzes text content quality using 5 scientific dimensions. Works with Chroma databases or direct text input.

## 🚀 Quick Start (5 minutes)

### 1. Install Prerequisites
```bash
# Check if you have Node.js (need v18+)
node --version

# Check if you have Python (need 3.8+) 
python3 --version
```

### 2. Download & Setup
```bash
# Clone or download this repository
cd ta-content-quality-analysis

# Install Node dependencies
npm install

# Create Python environment & install dependencies
python3 -m venv venv312
source venv312/bin/activate  # On Windows: venv312\Scripts\activate
pip install chromadb
```

### 3. Add to Claude Desktop

Find your Claude config file:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration (replace YOUR_USERNAME with your actual username):

```json
{
  "mcpServers": {
    "content-quality": {
      "command": "node",
      "args": ["/Users/YOUR_USERNAME/Desktop/ta-content-quality-analysis/src/index.js"],
      "env": {
        "PYTHON_PATH": "/Users/YOUR_USERNAME/Desktop/ta-content-quality-analysis/venv312/bin/python"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Completely quit and restart Claude Desktop. You should see the 🔨 tools icon in the chat input.

## 📊 What It Does

Analyzes content quality across 5 dimensions:

- **Word Precision** - Vocabulary specificity vs vagueness
- **Modal Certainty** - Confidence and authority in statements  
- **Structure Efficiency** - Content organization and flow
- **Punctuation Impact** - Effective punctuation usage
- **Semantic Consistency** - Topic focus and coherence

Each dimension scores 0-1, with an overall quality score.

## 💬 How to Use in Claude

### Direct Text Analysis (NEW!)
Just paste your content and ask Claude to analyze it:
```
"Analyze the quality of this article: [paste your text]"
```

### Chroma Database Analysis
If you have content in a Chroma database:
```
"List my Chroma collections"
"Analyze the content in my_collection" 
```

### Get Help
```
"Show me content analysis help"
```

## 🔧 Troubleshooting

### "Server is disconnected" Error

1. **Check paths are absolute** (start with `/` on Mac/Linux or `C:\` on Windows)
2. **Verify Python environment**:
   ```bash
   cd ta-content-quality-analysis
   ./venv312/bin/python -c "import chromadb; print('OK')"
   ```
3. **Test the server directly**:
   ```bash
   node src/index.js
   # Should output: "Content Quality Analysis MCP server running on stdio"
   ```

### Common Fixes

| Problem | Solution |
|---------|----------|
| Python not found | Make sure path to `venv312/bin/python` is correct |
| Module not found | Run `pip install chromadb` in venv312 |
| JSON syntax error | Check for trailing commas or missing quotes |
| Tools don't appear | Restart Claude Desktop completely |

### Still Having Issues?

1. Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for detailed solutions
2. Make sure all paths in config are absolute paths
3. The virtual environment MUST be named `venv312`
4. Restart Claude Desktop after any config changes

## 📁 Files Structure

```
ta-content-quality-analysis/
├── src/
│   └── index.js                     # MCP server
├── tools/
│   ├── content-quality-analyzer.py  # Chroma analyzer
│   └── content-quality-analyzer-direct.py  # Direct text analyzer  
├── venv312/                         # Python environment (create this)
├── package.json                     # Node config
├── README.md                        # This file
└── TROUBLESHOOTING.md              # Detailed help
```

## 🎯 Analysis Modes

- **Individual** - Analyze single documents for quality scoring
- **Website** - Analyze website content strategy and coherence
- **Competitive** - Compare multiple competitors in one collection
- **Auto** - Automatically detects the best mode

## 📝 What Makes Good Content?

The analyzer looks for:
- Clear, specific vocabulary (not vague terms)
- Confident statements (appropriate to content type)
- Good structure with transitions
- Varied punctuation for readability
- Consistent topic focus

Scores above 0.7 indicate high quality content.

## 🆘 Need Help?

- The tool is simple by design - minimal dependencies
- Everything runs locally on your machine
- No API keys or external services required
- Works with any Chroma database or direct text

## 📄 License

MIT License - Use freely!