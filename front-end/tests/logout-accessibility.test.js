import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const appPath = new URL('../src/App.jsx', import.meta.url);
const foundationPath = new URL('../src/foundation.css', import.meta.url);

test('logout keeps an accessible name when its visible text is hidden on mobile', async () => {
  const [app, foundation] = await Promise.all([
    readFile(appPath, 'utf8'),
    readFile(foundationPath, 'utf8'),
  ]);

  assert.match(app, /<Button[^>]*className="compact"[^>]*aria-label="Keluar"[^>]*>[\s\S]*?<span>Keluar<\/span><\/Button>/);
  assert.match(foundation, /@media \(max-width: 650px\)[\s\S]*?\.header-right \.button span \{ display: none; \}/);
});
