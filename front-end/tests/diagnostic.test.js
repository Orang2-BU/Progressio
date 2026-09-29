import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import { validateQuestions, diagnosticPayload, validateAttempt } from '../src/diagnostic.js';
import { loadTarget } from '../src/catalog.js';
import { login, logout, request } from '../src/api.js';
import { loginDestination } from '../src/navigation.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; logout(); });
const questions = [{ id: 1, prompt: 'Question?', skill_title: 'API', options: [{ value: 'a', label: 'A' }] }];
const attempt = { id: 1, career_track: 10, overall_score: 0, completed_at: '2026-09-29T12:00:00Z',
  skill_scores: [{ skill_id: 3, skill_title: 'API', score: 0, correct_answers: 0, total_questions: 1 }], recommended_skill_ids: [3] };
test('questions, incomplete answers, explicit unknown and server result contracts', () => {
  assert.equal(validateQuestions(questions), questions);
  assert.deepEqual(validateQuestions([]), []);
  for (const invalid of [null, [{}], [...questions, ...questions], [{ ...questions[0], options: [] }]]) assert.throws(() => validateQuestions(invalid));
  assert.throws(() => diagnosticPayload(questions, {}), (error) => Boolean(error.fields[1]));
  assert.deepEqual(diagnosticPayload(questions, { 1: '', score: 100, 99: 'a' }), { answers: { 1: '' } });
  assert.throws(() => diagnosticPayload(questions, { 1: 'invalid' }));
  assert.equal(validateAttempt(attempt, 10), attempt);
  for (const bad of [{ ...attempt, career_track: 11 }, { ...attempt, overall_score: null }, { ...attempt, overall_score: 101 }, { ...attempt, recommended_skill_ids: [99] }]) assert.throws(() => validateAttempt(bad, 10));
  assert.equal(loginDestination('/diagnostic/result?track=10'), '/diagnostic/result?track=10');
  assert.equal(loginDestination('https://evil.test/diagnostic'), '/');
});
test('diagnostic target validates the selected parent chain using public endpoints', async () => {
  const records = { 'career-tracks/10': { id: 10, title: 'Backend', slug: 'backend', is_active: true },
    'competencies/20': { id: 20, title: 'API', slug: 'api', career_track: 10 }, 'skills/30': { id: 30, title: 'REST', slug: 'rest', competency: 20 } };
  globalThis.fetch = async (url, options) => {
    assert.equal(options.headers.Authorization, undefined);
    return new Response(JSON.stringify(records[url.replace('/api/v1/', '')]));
  };
  assert.equal((await loadTarget('track=10&competency=20&skill=30&target=skill')).track.id, 10);
  records['skills/30'].competency = 21;
  await assert.rejects(loadTarget('track=10&competency=20&skill=30&target=skill'), /bukan bagian/);
  await assert.rejects(loadTarget(''), /Pilih career track/);
});
test('lost diagnostic POST response is never automatically submitted again', async () => {
  let posts = 0;
  globalThis.fetch = async (url) => {
    if (url.endsWith('auth/login')) return new Response(JSON.stringify({ access: 'access', refresh: 'refresh' }));
    if (url.endsWith('auth/me')) return new Response(JSON.stringify({ username: 'student' }));
    posts += 1; throw new TypeError('connection lost');
  };
  await login({ username: 'student', password: 'test' });
  await assert.rejects(request('diagnostics/10/submit', { method: 'POST', body: { answers: { 1: '' } } }));
  assert.equal(posts, 1);
});
