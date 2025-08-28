#!/usr/bin/env node
/**
 * TopicAtlas Content Quality Analysis MCP Server
 * 
 * Provides content quality analysis tools for Chroma vector databases
 * including individual quality scoring, website strategy analysis, and
 * competitive landscape analysis.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class ContentQualityMCP {
  constructor() {
    this.server = new Server(
      {
        name: 'ta-content-quality-analysis',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'analyze_content_quality',
            description: 'Analyze content quality in Chroma collections with multiple analysis modes',
            inputSchema: {
              type: 'object',
              properties: {
                chroma_directory: {
                  type: 'string',
                  description: 'Path to the Chroma database directory',
                  default: '/Users/andrewansley/Desktop/chroma-test'
                },
                collection_name: {
                  type: 'string',
                  description: 'Name of the Chroma collection to analyze'
                },
                analysis_mode: {
                  type: 'string',
                  enum: ['auto', 'individual', 'website', 'competitive'],
                  description: 'Analysis mode: auto (detect best mode), individual (5-dimension scoring), website (strategy analysis), competitive (multi-competitor)',
                  default: 'auto'
                },
                verbose: {
                  type: 'boolean',
                  description: 'Enable verbose output for debugging',
                  default: false
                }
              },
              required: ['collection_name']
            }
          },
          {
            name: 'analyze_text_direct',
            description: 'Analyze text content directly without using Chroma database',
            inputSchema: {
              type: 'object',
              properties: {
                text: {
                  type: 'string',
                  description: 'The text content to analyze'
                },
                metadata: {
                  type: 'object',
                  description: 'Optional metadata about the content (e.g., source, url, content_type)',
                  properties: {
                    source: { type: 'string' },
                    url: { type: 'string' },
                    content_type: { type: 'string' },
                    site_domain: { type: 'string' }
                  }
                },
                analysis_mode: {
                  type: 'string',
                  enum: ['individual'],
                  description: 'Analysis mode (only individual mode supported for direct text)',
                  default: 'individual'
                }
              },
              required: ['text']
            }
          },
          {
            name: 'list_chroma_collections',
            description: 'List all available Chroma collections with document counts',
            inputSchema: {
              type: 'object',
              properties: {
                chroma_directory: {
                  type: 'string',
                  description: 'Path to the Chroma database directory',
                  default: '/Users/andrewansley/Desktop/chroma-test'
                }
              }
            }
          },
          {
            name: 'get_analysis_help',
            description: 'Get help information about analysis modes and usage',
            inputSchema: {
              type: 'object',
              properties: {
                topic: {
                  type: 'string',
                  enum: ['modes', 'setup', 'metadata', 'examples'],
                  description: 'Help topic: modes (analysis modes), setup (getting started), metadata (enhanced structure), examples (usage examples)',
                  default: 'modes'
                }
              }
            }
          }
        ],
      };
    });

    // Handle tool execution
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'analyze_content_quality':
            return await this.analyzeContentQuality(args);
          case 'analyze_text_direct':
            return await this.analyzeTextDirect(args);
          case 'list_chroma_collections':
            return await this.listChromaCollections(args);
          case 'get_analysis_help':
            return await this.getAnalysisHelp(args);
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  /**
   * Analyze text directly without Chroma
   */
  async analyzeTextDirect(args) {
    const { text, metadata = {}, analysis_mode = 'individual' } = args;

    if (!text) {
      throw new Error('text is required');
    }

    // Create a temporary file with the text content
    const fs = await import('fs/promises');
    const os = await import('os');
    const path = await import('path');
    
    const tempDir = os.tmpdir();
    const tempFile = path.join(tempDir, `ta_analysis_${Date.now()}.txt`);
    
    try {
      // Write text to temp file
      await fs.writeFile(tempFile, text, 'utf8');
      
      // Build command arguments for direct analysis
      const pythonArgs = [
        join(__dirname, '..', 'tools', 'content-quality-analyzer-direct.py'),
        tempFile,
        '--mode', analysis_mode
      ];
      
      // Add metadata as JSON if provided
      if (metadata && Object.keys(metadata).length > 0) {
        pythonArgs.push('--metadata', JSON.stringify(metadata));
      }

      const result = await this.runPythonScript(pythonArgs);
      
      // Clean up temp file
      try {
        await fs.unlink(tempFile);
      } catch (e) {
        // Ignore cleanup errors
      }
      
      return {
        content: [
          {
            type: 'text',
            text: `# Direct Text Quality Analysis\n\n${result.stdout}`
          }
        ]
      };

    } catch (error) {
      // Clean up temp file on error
      try {
        await fs.unlink(tempFile);
      } catch (e) {
        // Ignore cleanup errors
      }
      throw new Error(`Direct analysis failed: ${error.message}\n\nStderr: ${error.stderr || 'None'}`);
    }
  }

  /**
   * Execute the Python content quality analyzer
   */
  async analyzeContentQuality(args) {
    const {
      chroma_directory = '/Users/andrewansley/Desktop/chroma-test',
      collection_name,
      analysis_mode = 'auto',
      verbose = false
    } = args;

    if (!collection_name) {
      throw new Error('collection_name is required');
    }

    // Build command arguments
    const pythonArgs = [
      join(__dirname, '..', 'tools', 'content-quality-analyzer.py'),
      collection_name,
      '--chroma-dir', chroma_directory,
      '--mode', analysis_mode
    ];

    if (verbose) {
      pythonArgs.push('--verbose');
    }

    try {
      const result = await this.runPythonScript(pythonArgs);
      
      return {
        content: [
          {
            type: 'text',
            text: `# Content Quality Analysis Results\n\n## Collection: ${collection_name}\n## Mode: ${analysis_mode}\n\n${result.stdout}`
          }
        ]
      };

    } catch (error) {
      throw new Error(`Analysis failed: ${error.message}\n\nStderr: ${error.stderr || 'None'}`);
    }
  }

  /**
   * List available Chroma collections
   */
  async listChromaCollections(args) {
    const { chroma_directory = '/Users/andrewansley/Desktop/chroma-test' } = args;

    const pythonArgs = [
      join(__dirname, '..', 'tools', 'content-quality-analyzer.py'),
      '--chroma-dir', chroma_directory
    ];

    try {
      const result = await this.runPythonScript(pythonArgs);
      
      return {
        content: [
          {
            type: 'text',
            text: `# Available Chroma Collections\n\n${result.stdout}`
          }
        ]
      };

    } catch (error) {
      throw new Error(`Failed to list collections: ${error.message}\n\nStderr: ${error.stderr || 'None'}`);
    }
  }

  /**
   * Get help information
   */
  async getAnalysisHelp(args) {
    const { topic = 'modes' } = args;

    const helpContent = {
      modes: `# Analysis Modes

## Available Analysis Modes

### 🤖 Auto Mode (Recommended)
- **Usage**: \`--mode auto\`
- **Description**: Automatically detects the best analysis mode based on your collection structure
- **Detection Logic**:
  - Multiple domains → Competitive analysis
  - Enhanced metadata → Website analysis
  - Basic collections → Individual analysis

### 📊 Individual Mode
- **Usage**: \`--mode individual\`
- **Description**: Analyzes individual content pieces across 5 quality dimensions
- **Metrics**:
  - Word Precision Score (0-1): Vocabulary specificity
  - Modal Certainty Score (0-1): Confidence in statements
  - Structure Efficiency Score (0-1): Content organization
  - Punctuation Impact Score (0-1): Punctuation effectiveness
  - Semantic Consistency Score (0-1): Topic coherence
- **Best For**: Content audits, quality benchmarking, writer feedback

### 🏢 Website Mode
- **Usage**: \`--mode website\`
- **Description**: Analyzes content as a cohesive website strategy
- **Metrics**:
  - Content Coherence: How sections work together
  - CTA Effectiveness: Call-to-action distribution
  - Trust Building: Credibility indicators
  - Content Structure: Organization variety
- **Best For**: Website optimization, content strategy planning

### 🏆 Competitive Mode
- **Usage**: \`--mode competitive\`
- **Description**: Compares multiple competitors in one collection
- **Metrics**:
  - Market quality averages
  - Competitor rankings
  - Content gap analysis
  - Strategy recommendations
- **Best For**: Competitive intelligence, market research`,

      setup: `# Setup Guide

## Prerequisites
- Python 3.8+
- Chroma vector database with content collections
- Node.js 18+ for MCP server

## Installation
1. Install MCP server dependencies:
   \`\`\`bash
   npm install
   \`\`\`

2. Ensure Python analyzer is available:
   \`\`\`bash
   python tools/content-quality-analyzer.py --help
   \`\`\`

## Quick Start
1. List your collections:
   \`\`\`
   list_chroma_collections(chroma_directory="/path/to/chroma")
   \`\`\`

2. Run auto-analysis:
   \`\`\`
   analyze_content_quality(collection_name="my_collection")
   \`\`\`

3. Save results:
   \`\`\`
   analyze_content_quality(
     collection_name="my_collection",
     save_results=true,
     analysis_mode="website"
   )
   \`\`\``,

      metadata: `# Enhanced Metadata Structure

## For Better Analysis Results

### Hierarchical Metadata
When creating collections, use this metadata structure:
\`\`\`json
{
  "site_domain": "example.com",
  "page_type": "homepage",
  "hierarchy": "1.0",
  "section_name": "hero_section",
  "content_type": "hero|value_proposition|service_info|trust_building",
  "page_flow_stage": "entry_point|value_props|trust_building|conversion",
  "importance_weight": 100,
  "section_order": 1,
  "contains_cta": true,
  "trust_signals_count": 2,
  "semantic_tags": ["legal", "cta", "problem_identification"],
  "word_count": 45,
  "business_category": "legal|roofing|healthcare|business"
}
\`\`\`

### Hierarchy System
- # headings → "1.0", "2.0", "3.0"
- ## headings → "1.1", "1.2", "2.1", "2.2"  
- ### headings → "1.1.1", "1.2.1", "2.1.1"
- #### headings → "1.1.1.1", "1.2.1.1"

### Collection Naming
- **Competitive Analysis**: \`keyword_analysis\` (all competitors)
- **Individual Sites**: \`brandname_pagetype\`
- **Market Research**: \`industry_location_competitive\``,

      examples: `# Usage Examples

## Basic Analysis
\`\`\`javascript
// List collections
list_chroma_collections()

// Auto-detect best analysis mode
analyze_content_quality({
  collection_name: "roofing_dallas_competitive"
})
\`\`\`

## Website Strategy Analysis
\`\`\`javascript
analyze_content_quality({
  collection_name: "acme_roofing_homepage",
  analysis_mode: "website",
  save_results: true
})
\`\`\`

## Competitive Intelligence
\`\`\`javascript
analyze_content_quality({
  collection_name: "legal_phoenix_market",
  analysis_mode: "competitive",
  verbose: true,
  output_file: "competitive_report.json"
})
\`\`\`

## Quality Audit
\`\`\`javascript
analyze_content_quality({
  collection_name: "blog_content_audit",
  analysis_mode: "individual",
  save_results: true
})
\`\`\`

## Custom Directory
\`\`\`javascript
analyze_content_quality({
  chroma_directory: "/path/to/my/chroma/db",
  collection_name: "my_collection",
  analysis_mode: "auto"
})
\`\`\``
    };

    return {
      content: [
        {
          type: 'text',
          text: helpContent[topic] || helpContent.modes
        }
      ]
    };
  }

  /**
   * Execute Python script and return results
   */
  async runPythonScript(args) {
    return new Promise((resolve, reject) => {
      const pythonPath = process.env.PYTHON_PATH || 'python3';
      const python = spawn(pythonPath, args, {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      python.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject({ 
            message: `Python script exited with code ${code}`, 
            stdout, 
            stderr 
          });
        }
      });

      python.on('error', (error) => {
        reject({ 
          message: `Failed to start Python script: ${error.message}`,
          stdout,
          stderr 
        });
      });
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Content Quality Analysis MCP server running on stdio');
  }
}

const server = new ContentQualityMCP();
server.run().catch(console.error);