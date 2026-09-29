import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import { login, logout } from '../src/api.js';
import { studyHref, sourceHref, validateProgress, loadStudy, loadProgress, submitCheckpoint, completeLesson } from '../src/study.js';
import { loginDestination } from '../src/navigation.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; logout(); });
const response = (body, status = 200) => new Response(JSON.stringify(body), { status });
const progress = { total_xp: 50, completed_lessons_count: 1, completed_lesson_ids: [7], skills: [{ skill: 3, mastery: 35, xp: 50 }] };
const lesson = { id: 7, skill: 3, title: 'HTTP', duration: 20, order: 1, content_url: 'https://example.com/http', content_type: 'reading',
  provider: 'Publisher', license: 'Declared', license_url: 'https://example.com/license', link_status: '', license_verified: false,
  attribution_required: true, redistributable: false, commercial_use_allowed: false };
const step = { id: 9, lesson: 7, order: 1, prompt: 'Read', checkpoint_question: 'Status?', estimated_minutes: 5, study_url: 'https://example.com/http#status' };

test('study URL preserves target; source links reject unsafe protocols and credentials', () => {
  assert.equal(studyHref('track=1&target=career_track&learn=2', 3), '/study?track=1&target=career_track&learn=3');
  assert.equal(loginDestination('/study?track=1&learn=3'), '/study?track=1&learn=3');
  assert.equal(sourceHref('https://example.com/a#b'), 'https://example.com/a#b');
  for (const unsafe of ['javascript:alert(1)', 'data:text/html,hello', '//evil.test', '/relative', 'https://user:secret@example.com', '']) assert.equal(sourceHref(unsafe), null);
  assert.throws(() => studyHref('', -1));
});
test('completion is derived from server lesson IDs, never from mastery or total count alone', () => {
  assert.equal(validateProgress(progress), progress);
  assert.equal(validateProgress({ ...progress, total_xp: 0, completed_lessons_count: 0, completed_lesson_ids: [], skills: [{ skill: 3, mastery: 100, xp: 0 }] }).completed_lesson_ids.length, 0);
  for (const invalid of [{ ...progress, completed_lesson_ids: undefined }, { ...progress, completed_lesson_ids: [7, 7], completed_lessons_count: 2 },
    { ...progress, completed_lessons_count: 2 }, { ...progress, total_xp: -1 }, { ...progress, skills: [{ skill: 3, mastery: null, xp: 0 }] }]) assert.throws(() => validateProgress(invalid));
});
test('study loads all public pages, verifies skill track and rejects unrelated lesson/step payloads', async () => {
  let pages = 0;
  let otherTrack = false;
  let invalidStep = false;
  let emptyLists = false;
  let unplanned = false;
  globalThis.fetch = async (url, options) => {
    assert.equal(options.headers.Authorization, undefined);
    if (url.endsWith('career-tracks/1')) return response({ id: 1, title: 'Backend', slug: 'backend', is_active: true });
    if (url.endsWith('skills/3')) return response({ id: 3, competency: 2, title: 'HTTP', slug: 'http' });
    if (url.endsWith('competencies/2')) return response({ id: 2, career_track: otherTrack ? 99 : 1 });
    if (url.includes('lessons?skill=3')) {
      pages += 1;
      if (emptyLists) return response({ count: 0, next: null, results: [] });
      return response({ count: 2, next: url.includes('page=2') ? null : 'https://untrusted.test/lessons?page=2', results: [{ ...lesson, id: url.includes('page=2') ? 8 : 7 }] });
    }
    if (url.endsWith('skills/http/study-plan')) return response({ count: emptyLists || unplanned ? 0 : 1, next: null, results: emptyLists || unplanned ? [] : [{ ...step, lesson: invalidStep ? 99 : 7 }] });
    assert.fail(`unexpected ${url}`);
  };
  assert.equal((await loadStudy('track=1&learn=3')).lessons.length, 2);
  assert.equal(pages, 2);
  otherTrack = true;
  await assert.rejects(loadStudy('track=1&learn=3'), /bukan bagian/);
  otherTrack = false; invalidStep = true;
  await assert.rejects(loadStudy('track=1&learn=3'), /Format materi/);
  invalidStep = false; unplanned = true;
  assert.equal((await loadStudy('track=1&learn=3')).steps.length, 0);
  emptyLists = true;
  assert.deepEqual((await loadStudy('track=1&learn=3')).lessons, []);
  for (const query of ['track=1', 'track=1&learn=-1', 'track=1&learn=3&learn=4']) await assert.rejects(loadStudy(query));
});
test('checkpoint sends only an answer; wrong feedback is not HTTP success-as-correct; completion has no body', async () => {
  const calls = [];
  globalThis.fetch = async (url, options) => {
    if (url.endsWith('auth/login')) return response({ access: 'token', refresh: 'refresh' });
    if (url.endsWith('auth/me')) return response({ username: 'student' });
    assert.equal(options.headers.Authorization, 'Bearer token'); calls.push(url);
    if (url.endsWith('checkpoint')) { assert.deepEqual(JSON.parse(options.body), { answer: '200' }); return response({ correct: false, feedback: 'Try again' }); }
    if (url.endsWith('complete')) { assert.equal(options.body, undefined); return response({ status: 'completed', lesson_id: 7, xp_earned: 0, newly_completed: false, current_skill_mastery: 70, current_skill_xp: 50 }); }
    return response(progress);
  };
  await login({ username: 'student', password: 'test' });
  await assert.rejects(submitCheckpoint(9, ' '), (e) => Boolean(e.fields.answer));
  assert.equal((await submitCheckpoint(9, ' 200 ')).correct, false);
  assert.equal((await completeLesson(7)).xp_earned, 0);
  assert.deepEqual(await loadProgress(), progress);
  assert.equal(calls.length, 3);
});
test('lost completion response is not automatically replayed and malformed results cannot grant a badge', async () => {
  let posts = 0;
  globalThis.fetch = async (url) => {
    if (url.endsWith('auth/login')) return response({ access: 'token', refresh: 'refresh' });
    if (url.endsWith('auth/me')) return response({ username: 'student' });
    posts += 1; throw new TypeError('lost response');
  };
  await login({ username: 'student', password: 'test' });
  await assert.rejects(completeLesson(7)); assert.equal(posts, 1);
  globalThis.fetch = async () => response({ correct: 'true', feedback: 'Invalid' });
  await assert.rejects(submitCheckpoint(9, '200'), /Format feedback/);
  globalThis.fetch = async () => response({ status: 'completed', lesson_id: 99 });
  await assert.rejects(completeLesson(7), /tidak dapat dipastikan/);
});
