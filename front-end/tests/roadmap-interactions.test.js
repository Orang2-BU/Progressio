import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import React from 'react';
import { login, logout } from '../src/api.js';
import { foundationRenderer } from './support/render-foundation.js';
import { mountDom } from './support/mount-dom.js';

const Roadmap = foundationRenderer({ path: '/roadmap' }).load('Roadmap.jsx').default;
const originalFetch = Object.getOwnPropertyDescriptor(globalThis, 'fetch');
const pages = [];
afterEach(async () => {
  await logout();
  for (const page of pages.splice(0).reverse()) await page.close();
  if (originalFetch) Object.defineProperty(globalThis, 'fetch', originalFetch); else delete globalThis.fetch;
});
const response = (data, status = 200) => new Response(JSON.stringify(data), { status });
const skill = (id, order, slug, title, prerequisites = []) => ({ skill_id: id, skill_slug: slug, skill_title: title,
  mastery: 0, order, competency_title: 'API', difficulty: 'beginner', estimated_minutes: 30,
  is_target: order === 2, prerequisites });
const roadmap = { target: { type: 'career_track', slug: 'backend', title: 'Backend' }, total_steps: 2,
  remaining_minutes: 60, remaining_hours: 1, already_satisfied: [],
  steps: [skill(1, 1, 'http', 'HTTP'), skill(2, 2, 'rest', 'REST', ['http'])] };
async function mount({ data = roadmap, onRoadmap } = {}) {
  const fetcher = async (rawUrl) => {
    const path = new URL(rawUrl, 'http://localhost').pathname.replace(/^\/api\/v1\//, '').replace(/\/$/, '');
    if (path === 'auth/login') return response({ access: 'access', refresh: 'refresh' });
    if (path === 'auth/me') return response({ username: 'student' });
    if (path === 'auth/logout') return response({});
    if (path === 'career-tracks/10') return response({ id: 10, title: 'Backend', slug: 'backend', is_active: true });
    if (path === 'roadmap') return onRoadmap ? onRoadmap() : response(data);
    throw new Error(`Unexpected request ${path}`);
  };
  globalThis.fetch = fetcher;
  await login({ username: 'student', password: 'synthetic-password' });
  const page = mountDom(React.createElement(Roadmap), { path: '/roadmap', query: 'track=10', fetcher });
  pages.push(page);
  await page.render(); await page.flush();
  return page;
}

test('roadmap selects ordered steps accessibly and preserves target in study links', async () => {
  const page = await mount();
  assert.match(page.container.textContent, /LANGKAH 1 \/ 2/);
  await page.click('button', /Lihat detail langkah 2: REST/);
  assert.match(page.container.textContent, /LANGKAH 2 \/ 2/);
  assert.match(page.container.textContent, /Akan dipelajari di langkah 1/);
  assert.ok(page.container.querySelector('a[href="/study?track=10&learn=2"]'));
});

test('empty roadmap is not represented as credential eligibility', async () => {
  const empty = { ...roadmap, total_steps: 0, remaining_minutes: 0, remaining_hours: 0, steps: [],
    already_satisfied: [{ skill_slug: 'rest', skill_title: 'REST', mastery: 70 }] };
  const page = await mount({ data: empty });
  assert.match(page.container.textContent, /Tidak ada langkah tersisa menurut mastery server/);
  assert.match(page.container.textContent, /evidence assessment tetap diperlukan/);
});

test('roadmap exposes server errors and a retry action', async () => {
  let fail = true;
  const page = await mount({ onRoadmap: () => fail ? response({ detail: 'Service unavailable.' }, 503) : response(roadmap) });
  assert.match(page.container.textContent, /Service unavailable/);
  fail = false;
  await page.click('button', /^Coba lagi$/); await page.flush();
  assert.match(page.container.textContent, /REST/);
});
