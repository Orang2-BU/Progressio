import test from 'node:test';
import assert from 'node:assert/strict';
import { assessmentPayload, validateAssessment, validateSubmission, submitAssessment, recoverSubmission, proofHref, loadVerification } from '../src/proof.js';
import { login, logout } from '../src/api.js';

const key = 'f1cf4884-8f43-4cb9-ae87-b4d7049874ec';
const a = { id: 4, skill: 2, title: 'Quiz', instructions: '', objective: '', mastery_criteria: '', review_status: 'draft', evaluation_mode: 'rules', max_score: 100, passing_score: 70,
  expected_evidence: [], questions: [{ id: 'q1', prompt: 'Question', options: [{ value: 'A', label: 'First' }, { value: 'B', label: 'Second' }] }] };
const submission = { id: 7, assessment: 4, request_id: key, status: 'completed', score: 0, is_passed: false, feedback: 'Try again', evaluation: { provider: 'rules', max_score: 100 } };

test('assessment payload has only answers/evidence and stable request ID, validates missing and unsafe inputs', () => {
  assert.equal(validateAssessment(a, 4, 2), a);
  assert.throws(() => assessmentPayload(a, {}, {}, key), (e) => e.fields.q1 === 'Pilih satu jawaban.');
  assert.deepEqual(assessmentPayload(a, { q1: 'B' }, {}, key), { request_id: key, content: { answers: { q1: 'B' } } });
  assert.throws(() => assessmentPayload({ ...a, evaluation_mode: 'ai' }, {}, { text: '', github_url: 'https://example.org' }, key));
  assert.throws(() => assessmentPayload({ ...a, evaluation_mode: 'ai' }, {}, { text: 'code', github_url: 'https://user:password@example.org' }, key));
  assert.throws(() => validateAssessment({ ...a, questions: [a.questions[0], a.questions[0]] }, 4, 2));
  assert.equal(proofHref('track=1&learn=8&exam=3&submission=9', 2), '/assessment?track=1&learn=2');
});

test('server results are validated, not inferred; legacy provenance never fabricated', () => {
  assert.equal(validateSubmission(submission, 4).is_passed, false);
  assert.equal(validateSubmission({ ...submission, evaluation: {} }, 4).evaluation.provider, undefined);
  assert.throws(() => validateSubmission({ ...submission, score: 101 }, 4));
  assert.throws(() => validateSubmission(submission, 8));
});

test('lost POST is not automatically replayed and request-specific GET recovers without sending evidence again', async () => {
  const original = global.fetch; let posts = 0;
  global.fetch = async (url, options) => {
    const path = String(url);
    if (path.endsWith('auth/login')) return Response.json({ access: 'token', refresh: 'refresh' });
    if (path.endsWith('auth/me')) return Response.json({ id: 1, username: 'student' });
    assert.equal(options.headers.Authorization, 'Bearer token');
    if (path.endsWith('/submit')) { posts++; assert.equal(JSON.parse(options.body).request_id, key); throw new TypeError('lost'); }
    assert.ok(path.includes(`request_id=${key}`));
    return Response.json({ count: 1, results: [submission], next: null });
  };
  try {
    await login({ username: 'student', password: 'test' });
    await assert.rejects(submitAssessment(a, assessmentPayload(a, { q1: 'A' }, {}, key)));
    assert.equal(posts, 1); assert.equal((await recoverSubmission(a, key)).id, 7); assert.equal(posts, 1);
  } finally { global.fetch = original; logout(); }
});

test('public verification needs no token; invalid UUID rejected before network', async () => {
  const original = global.fetch;
  global.fetch = async (_url, options) => {
    assert.equal(options.headers.Authorization, undefined);
    return Response.json({ credential_id: key, status: 'draft', is_valid: false, integrity_verified: false, evidences: [], standard: { mode: 'demo' } });
  };
  try { await assert.rejects(loadVerification('invalid')); assert.equal((await loadVerification(key)).is_valid, false); }
  finally { global.fetch = original; }
});
