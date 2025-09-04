#!/usr/bin/env node
import path from 'path';
import { loadAllConfig } from './configLoader.js';
import { PromptGenerator } from './generator.js';
import fs from 'fs';

interface CLIArgs {
  count: number;
  json: boolean;
  root: string;
  out?: string;
}

function parseArgs(): CLIArgs {
  const args = process.argv.slice(2);
  const parsed: CLIArgs = {
    count: 1,
    json: false,
    root: process.cwd()
  };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--count' && args[i + 1]) parsed.count = parseInt(args[++i], 10);
    else if (a === '--json') parsed.json = true;
    else if (a === '--root' && args[i + 1]) parsed.root = path.resolve(args[++i]);
    else if (a === '--out' && args[i + 1]) parsed.out = args[++i];
  }
  return parsed;
}

async function main() {
  const cli = parseArgs();
  const config = loadAllConfig(cli.root);
  const gen = new PromptGenerator(config);
  const results = gen.generate(cli.count);

  if (cli.json) {
    const payload = results.map(r => ({
      prompt: r.prompt,
      metadata: r.metadata
    }));
    const text = JSON.stringify(payload, null, 2);
    if (cli.out) {
      fs.writeFileSync(cli.out, text, 'utf-8');
      console.log(`Written JSON to ${cli.out}`);
    } else {
      console.log(text);
    }
  } else {
    for (const r of results) {
      console.log('---');
      console.log(r.prompt);
      if (r.metadata.warnings.length) {
        console.warn('Warnings:', r.metadata.warnings.join('; '));
      }
    }
  }
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});