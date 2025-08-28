#!/usr/bin/env node
/**
 * Simple test script to verify MCP server is working
 */

import { spawn } from 'child_process';

console.log('🧪 Testing MCP Server Connection...');

const server = spawn('/Users/andrewansley/.nvm/versions/node/v20.18.0/bin/node', ['src/index.js'], {
  cwd: '/Users/andrewansley/Desktop/ta-content-quality-analysis',
  env: {
    ...process.env,
    PATH: '/Users/andrewansley/.nvm/versions/node/v20.18.0/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
    PYTHON_PATH: '/opt/homebrew/bin/python3'
  },
  stdio: ['pipe', 'pipe', 'pipe']
});

// Send tools list request
const toolsRequest = JSON.stringify({
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
});

server.stdin.write(toolsRequest + '\n');

let output = '';
server.stdout.on('data', (data) => {
  output += data.toString();
});

server.stderr.on('data', (data) => {
  console.log('Server started:', data.toString());
});

setTimeout(() => {
  try {
    const response = JSON.parse(output);
    if (response.result && response.result.tools) {
      console.log('✅ MCP Server is working!');
      console.log(`📋 Found ${response.result.tools.length} tools:`);
      response.result.tools.forEach(tool => {
        console.log(`   • ${tool.name}: ${tool.description}`);
      });
    } else {
      console.log('❌ Unexpected response:', output);
    }
  } catch (error) {
    console.log('❌ Failed to parse response:', error.message);
    console.log('Raw output:', output);
  }
  
  server.kill();
  process.exit(0);
}, 2000);

server.on('error', (error) => {
  console.log('❌ Server error:', error.message);
  process.exit(1);
});