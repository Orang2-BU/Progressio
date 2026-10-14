import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import { createRequire } from 'node:module';
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { JSDOM } from 'jsdom';
import { login, logout } from '../src/api.js';
import { foundationRenderer } from './support/render-foundation.js';

const require = createRequire(import.meta.url);
const { AppRouterContext } = require('next/dist/shared/lib/app-router-context.shared-runtime');
const { PathnameContext, SearchParamsContext } = require('next/dist/shared/lib/hooks-client-context.shared-runtime');
const { StudyFlow } = foundationRenderer({ path: '/study' }).load('Study.jsx');
const profile = { id: 1, username: 'student', email: 'student@example.test', role: 'student' };
const lessons = [
  { id: 7, skill: 3, title: 'REST API Design', duration: 20, order: 1, content_url: 'https://example.com/rest', content_type: 'reading', provider: 'Publisher', license: 'CC BY', license_url: 'https://example.com/license', link_status: '', license_verified: true, attribution_required: true, redistributable: false, commercial_use_allowed: false },
  { id: 8, skill: 3, title: 'Relational Data Modelling', duration: 30, order: 2, content_url: 'https://example.com/data', content_type: 'reading', provider: 'Publisher', license: 'CC BY', license_url: 'https://example.com/license', link_status: '', license_verified: true, attribution_required: true, redistributable: false, commercial_use_allowed: false },
];
const progress = { total_xp: 40, completed_lessons_count: 0, completed_lesson_ids: [], skills: [{ skill: 3, mastery: 0, xp: 0 }] };

function response(data, status = 200) { return new Response(JSON.stringify(data), { status }); }
function deferred() {
  let resolve;
  const promise = new Promise((done) => { resolve = done; });
  return { promise, resolve };
}

const environments = [];
afterEach(async () => {
  logout();
  for (const environment of environments.splice(0)) await environment.close();
});

function createStudyPage(query, fetcher) {
  const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: `http://localhost/study?${query}` });
  const previous = new Map();
  for (const key of ['window', 'self', 'document', 'HTMLElement', 'HTMLInputElement', 'Event', 'MouseEvent', 'navigator']) {
    previous.set(key, Object.getOwnPropertyDescriptor(globalThis, key));
    Object.defineProperty(globalThis, key, { configurable: true, value: key === 'window' || key === 'self' ? dom.window : key === 'document' ? dom.window.document : key === 'navigator' ? dom.window.navigator : dom.window[key] });
  }
  previous.set('IS_REACT_ACT_ENVIRONMENT', Object.getOwnPropertyDescriptor(globalThis, 'IS_REACT_ACT_ENVIRONMENT'));
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  globalThis.fetch = fetcher;

  const container = dom.window.document.getElementById('root');
  const root = createRoot(container);
  const router = { back() {}, forward() {}, push() {}, replace() {}, refresh() {}, prefetch() {} };
  const tree = React.createElement(AppRouterContext.Provider, { value: router },
    React.createElement(PathnameContext.Provider, { value: '/study' },
      React.createElement(SearchParamsContext.Provider, { value: new URLSearchParams(query) },
        React.createElement(StudyFlow, { query }))));
  const environment = {
    container,
    async render() { await act(async () => { root.render(tree); }); },
    findButton(name) {
      const button = [...container.querySelectorAll('button')].find((item) => name.test(item.textContent.trim()));
      assert.ok(button, `Expected button matching ${name}; rendered: ${container.textContent}`);
      return button;
    },
    async clickButton(name) {
      const button = this.findButton(name);
      await act(async () => { button.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true })); });
    },
    async close() {
      await act(async () => root.unmount());
      dom.window.close();
      for (const [key, descriptor] of previous) {
        if (descriptor) Object.defineProperty(globalThis, key, descriptor);
        else delete globalThis[key];
      }
    },
  };
  environments.push(environment);
  return environment;
}

function demoApi({ onComplete, onCheckpoint, failFirstProgress = false }) {
  let progressCalls = 0;
  const calls = [];
  const fetcher = async (rawUrl, options = {}) => {
    const requestUrl = new URL(rawUrl, 'http://localhost');
    const path = requestUrl.pathname;
    const route = `${path}${requestUrl.search}`;
    calls.push(route);
    if (path.endsWith('/auth/login')) return response({ access: 'access-token', refresh: 'refresh-token' });
    if (path.endsWith('/auth/me')) return response(profile);
    if (path.endsWith('/career-tracks/1')) return response({ id: 1, title: 'Backend Engineering', slug: 'backend', is_active: true });
    if (path.endsWith('/skills/3')) return response({ id: 3, competency: 2, title: 'REST API Design', slug: 'rest-api-design' });
    if (path.endsWith('/competencies/2')) return response({ id: 2, career_track: 1 });
    if (route.includes('/lessons?skill=3')) return response({ count: lessons.length, next: null, results: lessons });
    if (path.endsWith('/skills/rest-api-design/study-plan')) return response({ count: 2, next: null, results: [
      { id: 9, lesson: 7, order: 1, prompt: 'Design a resource.', checkpoint_question: 'What status creates a resource?', estimated_minutes: 5, study_url: 'https://example.com/rest#status' },
      { id: 10, lesson: 8, order: 1, prompt: 'Model related data.', checkpoint_question: 'What identifies a row?', estimated_minutes: 7, study_url: 'https://example.com/data#keys' },
    ] });
    if (path.endsWith('/progress')) {
      progressCalls += 1;
      if (failFirstProgress && progressCalls === 1) return response({ detail: 'Progress sementara tidak tersedia.' }, 503);
      return response(progress);
    }
    if (/\/lesson\/\d+\/complete$/.test(path)) return onComplete ? onComplete(Number(path.match(/lesson\/(\d+)\/complete$/)[1]), options) : response({ status: 'completed', lesson_id: 7, xp_earned: 0, newly_completed: false, current_skill_mastery: 70, current_skill_xp: 0 });
    if (/\/study-steps\/\d+\/checkpoint$/.test(path)) return onCheckpoint ? onCheckpoint(Number(path.match(/study-steps\/(\d+)\/checkpoint$/)[1]), options) : response({ correct: false, feedback: 'Coba lagi.' });
    throw new Error(`Unexpected test request: ${path}`);
  };
  fetcher.calls = calls;
  return fetcher;
}

test('the real Study selector remounts lesson activity and ignores late completion receipts', async () => {
  const completion = deferred();
  const fetcher = demoApi({ onComplete: (lessonId) => lessonId === 7 ? completion.promise : response({ status: 'completed', lesson_id: lessonId, xp_earned: 0, newly_completed: false, current_skill_mastery: 70, current_skill_xp: 0 }) });
  const page = createStudyPage('track=1&learn=3', fetcher);
  await login({ username: 'student', password: 'test' });
  await page.render();

  assert.match(page.container.textContent, /REST API Design/, JSON.stringify(fetcher.calls));
  await page.clickButton(/Tandai lesson selesai/);
  assert.equal(page.findButton(/Mencatat di server/).disabled, true);
  await page.clickButton(/Relational Data Modelling/);
  assert.match(page.container.textContent, /What identifies a row/);
  assert.equal(page.findButton(/Tandai lesson selesai/).disabled, true, 'the global completion lock prevents concurrent mutations');
  assert.doesNotMatch(page.container.textContent, /Mencatat di server/);
  assert.doesNotMatch(page.container.textContent, /XP pada receipt/);

  completion.resolve(response({ status: 'completed', lesson_id: 7, xp_earned: 20, newly_completed: true, current_skill_mastery: 70, current_skill_xp: 20 }));
  await act(async () => { await completion.promise; });
  assert.doesNotMatch(page.container.textContent, /20 XP pada receipt/);
  assert.match(page.container.textContent, /Relational Data Modelling/);
  assert.equal(page.findButton(/Tandai lesson selesai/).disabled, false);
});

test('Study presents failed progress as unknown and lets the learner retry successfully', async () => {
  const page = createStudyPage('track=1&learn=3', demoApi({ failFirstProgress: true }));
  await login({ username: 'student', password: 'test' });
  await page.render();

  assert.match(page.container.textContent, /Status completion belum dapat dipastikan/);
  assert.equal(page.findButton(/Coba perbarui progress/).disabled, false);
  await page.clickButton(/Coba perbarui progress/);
  assert.doesNotMatch(page.container.textContent, /Status completion belum dapat dipastikan/);
  assert.match(page.container.textContent, /40 XP total dari server/);
});
