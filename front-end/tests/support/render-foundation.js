import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { compileFunction } from 'node:vm';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import * as api from '../../src/api.js';

const require = createRequire(import.meta.url);
const { transformSync } = require('next/dist/compiled/babel/core');
const { AppRouterContext } = require('next/dist/shared/lib/app-router-context.shared-runtime');
const { PathnameContext, SearchParamsContext } = require('next/dist/shared/lib/hooks-client-context.shared-runtime');
const sourceDirectory = fileURLToPath(new URL('../../src/', import.meta.url));

// Render real components with real Next providers. Only the session data boundary
// is supplied for each scenario; effects, CSS, events and hydration are not run.
export function foundationRenderer({ path = '/login', query = '', session = { user: null, reason: '' } } = {}) {
  const modules = new Map();
  function load(filePath) {
    if (modules.has(filePath)) return modules.get(filePath).exports;
    const module = { exports: {} };
    modules.set(filePath, module);
    const source = readFileSync(filePath, 'utf8');
    const { code } = transformSync(source, {
      filename: filePath, babelrc: false, configFile: false,
      presets: [['next/babel', { 'preset-env': { modules: 'commonjs', targets: { node: 'current' } }, 'preset-react': { runtime: 'automatic' }, 'transform-runtime': { helpers: false } }]],
    });
    function dependency(name) {
      if (name === './api.js') return { ...api, getServerSession: () => session };
      return name.startsWith('.') ? load(resolve(dirname(filePath), name)) : require(name);
    }
    compileFunction(code, ['require', 'module', 'exports'], { filename: filePath })(dependency, module, module.exports);
    return module.exports;
  }
  const app = load(resolve(sourceDirectory, 'App.jsx'));
  const ui = load(resolve(sourceDirectory, 'ui.jsx'));
  const router = { replace() { throw new Error('SSR must not navigate'); }, push() { throw new Error('SSR must not navigate'); }, prefetch() {} };
  function render(component, props = {}) {
    return renderToStaticMarkup(React.createElement(AppRouterContext.Provider, { value: router },
      React.createElement(PathnameContext.Provider, { value: path },
        React.createElement(SearchParamsContext.Provider, { value: new URLSearchParams(query) },
          React.createElement(component, props)))));
  }
  return { app, ui, render, load: (name) => load(resolve(sourceDirectory, name)) };
}
