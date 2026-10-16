import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { JSDOM } from 'jsdom';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { AppRouterContext } = require('next/dist/shared/lib/app-router-context.shared-runtime');
const { PathnameContext, SearchParamsContext } = require('next/dist/shared/lib/hooks-client-context.shared-runtime');

export function mountDom(element, { path = '/', query = '', fetcher, router = {} } = {}) {
  const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: `http://localhost${path}${query ? `?${query}` : ''}` });
  const previous = new Map();
  for (const key of ['window', 'self', 'document', 'HTMLElement', 'HTMLInputElement', 'Event', 'MouseEvent', 'navigator', 'fetch']) {
    previous.set(key, Object.getOwnPropertyDescriptor(globalThis, key));
    const value = key === 'window' || key === 'self' ? dom.window : key === 'document' ? dom.window.document
      : key === 'navigator' ? dom.window.navigator : key === 'fetch' ? fetcher : dom.window[key];
    Object.defineProperty(globalThis, key, { configurable: true, value });
  }
  previous.set('IS_REACT_ACT_ENVIRONMENT', Object.getOwnPropertyDescriptor(globalThis, 'IS_REACT_ACT_ENVIRONMENT'));
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  const container = dom.window.document.getElementById('root');
  const root = createRoot(container);
  const appRouter = { back() {}, forward() {}, push() {}, replace() {}, refresh() {}, prefetch() {}, ...router };
  let closed = false;
  function tree(nextElement, nextQuery) {
    return React.createElement(AppRouterContext.Provider, { value: appRouter },
      React.createElement(PathnameContext.Provider, { value: path },
        React.createElement(SearchParamsContext.Provider, { value: new URLSearchParams(nextQuery) }, nextElement)));
  }
  return {
    container,
    async render(nextElement = element, nextQuery = query) { await act(async () => root.render(tree(nextElement, nextQuery))); },
    async click(selector, name) {
      const node = [...container.querySelectorAll(selector)].find((item) => (item.getAttribute('aria-label') || item.textContent.trim()).match(name));
      if (!node) throw new Error(`Missing ${selector} ${name}: ${container.textContent}`);
      await act(async () => node.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true })));
    },
    async flush() { await act(async () => new Promise((resolve) => setImmediate(resolve))); },
    async close() {
      if (closed) return;
      closed = true;
      await act(async () => root.unmount());
      dom.window.close();
      for (const [key, descriptor] of previous) descriptor ? Object.defineProperty(globalThis, key, descriptor) : delete globalThis[key];
    },
  };
}
