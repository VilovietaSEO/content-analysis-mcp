# Quick Setup Guide for Claude Desktop

## 🚀 Add to Claude Desktop

### Step 1: Copy Configuration
Add this to your Claude Desktop configuration file:

**Location of config file:**
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration to add:**
```json
{
  "mcpServers": {
    "ta-content-quality-analysis": {
      "command": "node", 
      "args": ["src/index.js"],
      "cwd": "/Users/andrewansley/Desktop/ta-content-quality-analysis",
      "env": {}
    }
  }
}
```

### Step 2: Restart Claude Desktop
Close and reopen Claude Desktop to load the new MCP server.

### Step 3: Verify Installation
In Claude Desktop, you should see the MCP server connected and these tools available:
- `analyze_content_quality`
- `list_chroma_collections` 
- `get_analysis_help`

## 🧪 Test Commands

### List Your Collections
```
Use the list_chroma_collections tool to see my available Chroma collections.
```

### Get Help
```
Use get_analysis_help with topic "examples" to show me usage examples.
```

### Analyze Content
```
Use analyze_content_quality to analyze the "dallasroofer_website" collection in auto mode.
```

### Save Results
```
Analyze the "dallasroofer_website" collection in website mode and save the results to a JSON file.
```

## 🔧 Troubleshooting

### MCP Not Connecting
1. Check the `cwd` path in your config matches the actual location
2. Ensure Node.js and Python are in your PATH
3. Check Claude Desktop logs for connection errors

### Python Script Errors  
1. Test the Python script directly:
   ```bash
   cd /Users/andrewansley/Desktop/ta-content-quality-analysis
   python3 tools/content-quality-analyzer.py --help
   ```
2. Ensure the chroma-test directory exists and has collections

### Missing Collections
1. Verify your Chroma database directory path
2. Check that collections actually contain documents
3. Use the correct chroma_directory parameter

## 📁 Custom Chroma Directory

If your Chroma database is elsewhere, specify the directory:
```
Use analyze_content_quality with collection_name="my_collection" and chroma_directory="/path/to/my/chroma/db"
```

## ⚡ Quick Start Workflow

1. **List collections** to see what's available
2. **Get help** to understand analysis modes  
3. **Run auto-analysis** to let the system choose the best mode
4. **Save results** for detailed JSON output
5. **Try different modes** (individual, website, competitive) for specific insights

## 🎯 Next Steps

Once working, explore advanced features:
- **Enhanced metadata structure** for better analysis
- **Competitive analysis** with multiple competitors in one collection  
- **Website strategy analysis** for content optimization
- **Custom output files** and verbose logging for debugging