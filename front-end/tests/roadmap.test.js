import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import { login, logout } from '../src/api.js';
import { roadmapPath, validateRoadmap, loadRoadmap } from '../src/roadmap.js';
import { loginDestination } from '../src/navigation.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; logout(); });
const target = { kind: 'skill', slug: 'rest' };
const step = { order: 1, skill_id: 3, skill_slug: 'rest', skill_title: 'REST', competency_title: 'API',
  difficulty: 'beginner', estimated_minutes: 90, mastery: 0, prerequisites: [], is_target: true };
const roadmap = { target: { type: 'skill', slug: 'rest', title: 'REST' }, total_steps: 1, remaining_minutes: 90,
  remaining_hours: 1.5, already_satisfied: [], steps: [step] };
test('roadmap uses exactly one server-resolved slug and keeps safe return-to-login URL', () => {
  for (const kind of ['career_track', 'competency', 'skill']) assert.equal(roadmapPath({ kind, slug: 'api & rest' }), `roadmap?${kind}=api+%26+rest`);
  assert.throws(() => roadmapPath({ kind: 'unknown', slug: 'rest' }));
  assert.throws(() => roadmapPath({ kind: 'skill', slug: '' }));
  assert.equal(loginDestination('/roadmap?track=10&competency=20&skill=30&target=skill'), '/roadmap?track=10&competency=20&skill=30&target=skill');
  assert.equal(loginDestination('//evil.test/roadmap'), '/');
});
test('roadmap validates server totals, target, order and empty satisfied route without client grading', () => {
  assert.equal(validateRoadmap(roadmap, target), roadmap);
  const empty = { ...roadmap, total_steps: 0, remaining_minutes: 0, remaining_hours: 0, steps: [],
    already_satisfied: [{ skill_slug: 'rest', skill_title: 'REST', mastery: 70 }] };
  assert.equal(validateRoadmap(empty, target), empty);
  for (const invalid of [null, {}, { ...roadmap, total_steps: 2 }, { ...roadmap, remaining_minutes: 0 },
    { ...roadmap, remaining_hours: null }, { ...roadmap, steps: [{ ...step, mastery: null }] },
    { ...roadmap, steps: [{ ...step, order: 2 }] }, { ...roadmap, steps: [{ ...step, prerequisites: ['rest'] }] },
    { ...roadmap, target: { ...roadmap.target, slug: 'other' } }, { ...empty, already_satisfied: [empty.already_satisfied[0], empty.already_satisfied[0]] }]) {
    assert.throws(() => validateRoadmap(invalid, target));
  }
  const ordered = { ...roadmap, total_steps: 2, remaining_minutes: 180, remaining_hours: 3,
    steps: [{ ...step, skill_id: 2, skill_slug: 'foundation', is_target: false }, { ...step, order: 2, prerequisites: ['foundation'] }] };
  assert.equal(validateRoadmap(ordered, target), ordered);
  assert.throws(() => validateRoadmap({ ...ordered, steps: [{ ...ordered.steps[0], prerequisites: ['rest'] }, ordered.steps[1]] }, target));
});
test('roadmap requests are read-only, authenticated and preserve API failure/cancellation', async () => {
  let reads = 0;
  globalThis.fetch = async (url, options) => {
    if (url.endsWith('auth/login')) return new Response(JSON.stringify({ access: 'token', refresh: 'refresh' }));
    if (url.endsWith('auth/me')) return new Response(JSON.stringify({ username: 'student' }));
    assert.equal(url, '/api/v1/roadmap?skill=rest');
    assert.equal(options.method, 'GET'); assert.equal(options.headers.Authorization, 'Bearer token'); assert.equal(options.body, undefined);
    reads += 1; return new Response(JSON.stringify(roadmap));
  };
  await login({ username: 'student', password: 'test' });
  assert.deepEqual(await loadRoadmap(target), roadmap);
  assert.equal(reads, 1);
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: 'Target contains no skills.' }), { status: 400 });
  await assert.rejects(loadRoadmap(target), (e) => e.status === 400 && e.message === 'Target contains no skills.');
  const controller = new AbortController(); controller.abort();
  globalThis.fetch = async (url, options) => { options.signal.throwIfAborted(); };
  await assert.rejects(loadRoadmap(target, { signal: controller.signal }), (e) => e.name === 'AbortError');
});
