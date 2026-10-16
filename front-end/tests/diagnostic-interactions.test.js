import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import React from 'react';
import { act } from 'react';
import { login, logout } from '../src/api.js';
import { foundationRenderer } from './support/render-foundation.js';
import { mountDom } from './support/mount-dom.js';

const diagnostic = foundationRenderer({ path: '/diagnostic' }).load('Diagnostic.jsx').default;
const pages = [];
const originalFetch = Object.getOwnPropertyDescriptor(globalThis, 'fetch');
afterEach(async () => {
  await logout();
  for (const page of pages.splice(0).reverse()) await page.close();
  if (originalFetch) Object.defineProperty(globalThis, 'fetch', originalFetch); else delete globalThis.fetch;
});
function response(data, status = 200) { return new Response(JSON.stringify(data), { status }); }
async function choose(page, selector) { await act(async () => page.container.querySelector(selector).click()); }
function fixture({ onSubmit = () => response({ id: 5, career_track: 10, overall_score: 50, completed_at: '2026-10-01T00:00:00Z',
  skill_scores: [{ skill_id: 3, skill_title: 'REST API', score: 50, total_questions: 2, correct_answers: 1 }], recommended_skill_ids: [3] }), onQuestions } = {}) {
  const fixtureOptions = { onQuestions };
  const questions = [1, 2].map((id) => ({ id, prompt: `Pertanyaan ${id}?`, skill_title: 'REST API', options: [{ value: 'yes', label: 'Ya' }, { value: 'no', label: 'Tidak' }] }));
  const calls = [];
  const fetcher = async (rawUrl, options = {}) => {
    const url = new URL(rawUrl, 'http://localhost');
    const route = `${url.pathname.replace(/^\/api\/v1\//, '').replace(/\/$/, '')}${url.search}`;
    calls.push({ route, options });
    if (route === 'auth/login') return response({ access: 'synthetic-access', refresh: 'synthetic-refresh' });
    if (route === 'auth/me') return response({ username: 'student' });
    if (route === 'auth/logout') return response({});
    const trackMatch = route.match(/^career-tracks\/(\d+)$/);
    if (trackMatch) return response({ id: Number(trackMatch[1]), title: Number(trackMatch[1]) === 10 ? 'Backend' : 'Data', slug: Number(trackMatch[1]) === 10 ? 'backend' : 'data', is_active: true, career_track: Number(trackMatch[1]) });
    const questionMatch = route.match(/^diagnostics\/(\d+)$/);
    if (questionMatch) return fixtureOptions.onQuestions ? fixtureOptions.onQuestions(Number(questionMatch[1]), options) : response(questions);
    if (route === 'diagnostics/10/submit') return onSubmit(options);
    if (route === 'diagnostics/latest?career_track=10') return response({ id: 5, career_track: 10, overall_score: 50, completed_at: '2026-10-14T00:00:00Z',
      skill_scores: [{ skill_id: 3, skill_title: 'REST API', score: 50, total_questions: 2, correct_answers: 1 }], recommended_skill_ids: [3] });
    throw new Error(`Unexpected request ${route}`);
  };
  return { fetcher, calls };
}
async function mount({ onSubmit, onQuestions, query = 'track=10', result = false } = {}) {
  const { fetcher, calls } = fixture({ onSubmit, onQuestions });
  globalThis.fetch = fetcher;
  await login({ username: 'student', password: 'synthetic-password' });
  const pushed = [];
  const page = mountDom(React.createElement(diagnostic, { result }), { path: result ? '/diagnostic/result' : '/diagnostic', query, fetcher, router: { push: (path) => pushed.push(path) } });
  pages.push(page);
  await page.render();
  await page.flush();
  return { page, calls, pushed };
}

test('diagnostic locks submission while the server is grading, preventing duplicate POST', async () => {
  let resolve; let posts = 0;
  const pending = new Promise((done) => { resolve = done; });
  const { page, calls } = await mount({ onSubmit: () => { posts += 1; return pending; } });
  await choose(page, 'input[name="question-1"][value="yes"]');
  await page.click('button', /^Lanjut$/);
  await choose(page, 'input[name="question-2"][value="no"]');
  await page.click('button', /^Kirim jawaban$/);
  assert.equal(page.container.querySelector('button[type="submit"]').disabled, true);
  await act(async () => page.container.querySelector('button[type="submit"]').click());
  assert.equal(posts, 1);
  resolve(response({ id: 5, career_track: 10, overall_score: 50, completed_at: '2026-10-01T00:00:00Z',
    skill_scores: [{ skill_id: 3, skill_title: 'REST API', score: 50, total_questions: 2, correct_answers: 1 }], recommended_skill_ids: [3] }));
  await pending; await page.flush();
  assert.equal(calls.filter(({ route }) => route.endsWith('/submit')).length, 1);
});

test('diagnostic aborts an old track request when the target query changes', async () => {
  let resolveOld; let oldSignal;
  const oldResponse = new Promise((done) => { resolveOld = done; });
  const { page } = await mount({ onQuestions: (trackId, options) => {
    if (trackId === 10) { oldSignal = options.signal; return oldResponse; }
    return response([{ id: 21, prompt: 'Data question?', skill_title: 'Data', options: [{ value: 'yes', label: 'Ya' }] }]);
  } });
  assert.equal(page.container.querySelector('[role="status"]')?.textContent.includes('Memuat'), true);
  await page.render(undefined, 'track=11'); await page.flush();
  assert.equal(oldSignal.aborted, true);
  assert.match(page.container.textContent, /Data question/);
  resolveOld(response([{ id: 10, prompt: 'Backend question?', skill_title: 'API', options: [{ value: 'yes', label: 'Ya' }] }]));
  await oldResponse; await page.flush();
  assert.match(page.container.textContent, /Data question/);
  assert.doesNotMatch(page.container.textContent, /Backend question/);
});

test('diagnostic result renders a server attempt without treating it as a question list', async () => {
  const { page, calls } = await mount({ result: true });
  assert.match(page.container.textContent, /Titik awalmu sudah tercatat/);
  assert.match(page.container.textContent, /50/);
  assert.equal(calls.some(({ route }) => route === 'diagnostics/latest?career_track=10'), true);
});

test('diagnostic navigates without losing answers and sends explicit unknown for every question', async () => {
  const { page, calls, pushed } = await mount();
  assert.match(page.container.textContent, /Pertanyaan 1/);
  const first = page.container.querySelector('input[name="question-1"][value="yes"]');
  await choose(page, 'input[name="question-1"][value="yes"]');
  await page.flush();
  await page.click('button', /^Lanjut$/);
  assert.match(page.container.textContent, /Pertanyaan 2/);
  await page.click('button', /^Tandai belum tahu$/);
  assert.equal(page.container.querySelector('input[name="question-2"][value=""]')?.checked, true);
  assert.equal(calls.some(({ route }) => route.endsWith('/submit')), false);
  await page.click('button', /^Kirim jawaban$/);
  await page.flush();
  const submission = calls.find(({ route }) => route.endsWith('/submit'));
  assert.deepEqual(JSON.parse(submission.options.body), { answers: { 1: 'yes', 2: '' } });
  assert.deepEqual(pushed, ['/diagnostic/result?track=10']);
});

test('diagnostic does not resubmit uncertain server outcomes automatically', async () => {
  let posts = 0;
  const { page, calls } = await mount({ onSubmit: () => { posts += 1; throw new TypeError('connection lost'); } });
  await choose(page, 'input[name="question-1"][value="yes"]');
  await page.click('button', /^Lanjut$/);
  await choose(page, 'input[name="question-2"][value="no"]');
  await page.click('button', /^Kirim jawaban$/);
  await page.flush();
  assert.match(page.container.textContent, /Pengiriman mungkin sudah tersimpan/);
  assert.equal(posts, 1);
  assert.equal(calls.filter(({ route }) => route.endsWith('/submit')).length, 1);
  assert.equal(page.container.querySelector('button[type="submit"]').disabled, true);
});
