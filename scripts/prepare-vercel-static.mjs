import { cpSync, existsSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const source = resolve(root, 'frontend', 'dist');
const target = resolve(root, 'public');

if (!existsSync(source)) {
  throw new Error(`Frontend build output not found: ${source}`);
}

rmSync(target, { recursive: true, force: true });
cpSync(source, target, { recursive: true });
