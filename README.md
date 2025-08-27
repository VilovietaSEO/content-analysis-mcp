# Content Analysis MCP

A powerful standalone content quality analyzer that works with Claude Desktop and Chroma MCP to provide professional-grade SEO content analysis.

## 🚀 What This Does

Analyzes any text content across **5 critical quality dimensions** used by top SEO agencies:

1. **Word Precision Score** (0-1) - How specific vs vague your vocabulary is
2. **Modal Certainty Score** (0-1) - Confidence level in your statements  
3. **Structure Efficiency Score** (0-1) - How well-organized your content flows
4. **Punctuation Impact Score** (0-1) - Effectiveness of punctuation usage
5. **Semantic Consistency Score** (0-1) - Topic coherence throughout the text

## 📊 Perfect For

- **SEO Professionals** analyzing competitor content
- **Content Creators** wanting to improve quality scores
- **Digital Agencies** auditing client content
- **Anyone** using Claude Desktop with Chroma MCP for content analysis

## 🎯 Sample Output

```
🎯 CONTENT QUALITY ANALYSIS REPORT
Collection: competitor_analysis
Documents: 15

📈 COLLECTION AVERAGES:
  Overall Quality:        0.742 (Range: 0.234 - 0.891)
  Word Precision:         0.678 (Measures vocabulary specificity)
  Modal Certainty:        0.823 (Measures confidence in statements)
  Structure Efficiency:   0.567 (Measures content organization)
  Punctuation Impact:     0.734 (Measures punctuation effectiveness)
  Semantic Consistency:   0.689 (Measures topic coherence)

🏆 BEST DOCUMENT (Score: 0.891):
  Heading: "How to File Personal Injury Claims"
  
⚠️ NEEDS IMPROVEMENT (Score: 0.234):
  Heading: "Contact Us Today"
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.10+
- Claude Desktop
- Chroma MCP configured

### Installation

1. **Download the analyzer:**
   ```bash
   wget https://raw.githubusercontent.com/yourusername/content-analysis-mcp/main/analyze_content_quality.py
   ```

2. **Install dependencies:**
   ```bash
   pip install chromadb
   ```

3. **Place in your Chroma data folder and run:**
   ```bash
   python analyze_content_quality.py
   ```

## 📚 Full Setup Guide

For complete installation instructions including Python, UV, and Claude Desktop setup, see:

**👉 [COMPLETE SETUP GUIDE](SETUP.md)**

## 💡 Usage Examples

```bash
# Analyze all collections
python analyze_content_quality.py

# Analyze specific collection
python analyze_content_quality.py competitor_content

# Save detailed JSON results
python analyze_content_quality.py competitor_content --save-json results.json

# Use custom Chroma directory
python analyze_content_quality.py --data-dir /path/to/chroma competitor_content
```

## 🧠 How It Works

The analyzer uses advanced NLP techniques to evaluate content quality:

- **Lexical Analysis** - Identifies vague vs precise vocabulary
- **Modal Analysis** - Measures certainty and confidence markers
- **Structural Analysis** - Evaluates organization and flow
- **Punctuation Analysis** - Assesses punctuation effectiveness
- **Semantic Analysis** - Measures topic consistency and coherence

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

Having issues? Please create an issue with:
- Your operating system
- Python version (`python --version`)
- Error messages (copy/paste exactly)
- What step you're stuck on

---

**Ready to analyze content like a pro?** ⭐ Star this repo if you find it useful!