import assert from 'node:assert/strict';
import { afterEach, beforeEach, test } from 'node:test';
import nextConfig from '../next.config.mjs';
import { ApiError, getSession, getServerSession, login, logout, register, request } from '../src/api.js';

const originalFetch = globalThis.fetch;
const profile = { id: 1, username: 'student', email: 'student@example.test', role: 'student', date_joined: '2026-09-29T00:00:00Z' };
const response = (data, status = 200) => new Response(JSON.stringify(data), { status });
const deferred = () => { let resolve; const promise = new Promise((done) => { resolve = done; }); return { promise, resolve }; };
beforeEach(() => logout());
afterEach(() => { logout(); globalThis.fetch = originalFetch; });

function authenticatedFetch(handler) {
  globalThis.fetch = async (url, options) => {
    if (url.endsWith('auth/login')) return response({ access: 'initial', refresh: 'refresh-token' });
    if (url.endsWith('auth/me')) return response(profile);
    return handler(url, options);
  };
}

test('register sends exact payload without authorization; login loads real profile', async () => {
  const body = { username: 'student', email: 'student@example.test', password: 'abc', password_confirm: 'abc', role: 'student' };
  authenticatedFetch((url, options) => {
    assert.equal(url, '/api/v1/auth/register');
    assert.equal(options.headers.Authorization, undefined);
    assert.deepEqual(JSON.parse(options.body), body);
    return response(profile, 201);
  });
  assert.deepEqual(await register(body), profile);
  assert.equal(getSession().user, null);
  await login({ username: 'student', password: 'abc' });
  assert.deepEqual(getSession().user, profile);
});

test('Next proxy preserves Django endpoints with and without a trailing slash', async () => {
  assert.equal(nextConfig.skipTrailingSlashRedirect, true);
  const rules = await nextConfig.rewrites();
  assert.equal(rules[0].source, '/api/:path*/');
  assert.ok(rules[0].destination.endsWith('/api/:path*/'));
  assert.equal(rules[1].source, '/api/:path*');
  assert.ok(rules[1].destination.endsWith('/api/:path*'));
});

test('SSR snapshot stays anonymous even when the client is authenticated', async () => {
  const initial = getServerSession();
  authenticatedFetch(() => response({}));
  await login({ username: 'student', password: 'abc' });
  assert.equal(getSession().user.username, 'student');
  assert.equal(getServerSession(), initial);
  assert.deepEqual(initial, { user: null, reason: '' });
});

test('wrong credentials preserve error and never refresh', async () => {
  let calls = 0;
  globalThis.fetch = async (url) => {
    calls += 1;
    assert.ok(url.endsWith('auth/login'));
    return response({ detail: 'No active account found' }, 401);
  };
  await assert.rejects(login({ username: 'student', password: 'wrong' }), /No active account/);
  assert.equal(calls, 1);
  assert.equal(getSession().user, null);
});

test('concurrent 401 requests share one refresh and retry once', async () => {
  let refreshCalls = 0;
  authenticatedFetch((url, options) => {
    if (url.endsWith('auth/refresh')) {
      refreshCalls += 1;
      assert.equal(options.headers.Authorization, undefined);
      return response({ access: 'new-token' });
    }
    return options.headers.Authorization === 'Bearer initial'
      ? response({ detail: 'expired' }, 401) : response({ ok: true });
  });
  await login({ username: 'student', password: 'abc' });
  assert.deepEqual(await Promise.all([request('progress'), request('credentials/')]), [{ ok: true }, { ok: true }]);
  assert.equal(refreshCalls, 1);
});

test('invalid refresh ends session without an infinite retry', async () => {
  let refreshCalls = 0;
  authenticatedFetch((url) => {
    if (url.endsWith('auth/refresh')) refreshCalls += 1;
    return response({ detail: 'expired' }, 401);
  });
  await login({ username: 'student', password: 'abc' });
  await assert.rejects(request('progress'), ApiError);
  assert.equal(refreshCalls, 1);
  assert.equal(getSession().user, null);
  assert.match(getSession().reason, /Sesi berakhir/);
});

test('logout during refresh cannot restore the old session', async () => {
  const gate = deferred();
  const started = deferred();
  authenticatedFetch((url) => {
    if (url.endsWith('auth/refresh')) { started.resolve(); return gate.promise; }
    return response({ detail: 'expired' }, 401);
  });
  await login({ username: 'student', password: 'abc' });
  const pending = request('progress');
  const rejected = assert.rejects(pending, ApiError);
  await started.promise;
  logout();
  gate.resolve(response({ access: 'late-token' }));
  await rejected;
  assert.equal(getSession().user, null);
});

test('field validation, non-JSON errors, and network errors remain readable', async () => {
  globalThis.fetch = async () => response({ username: ['Already exists.'] }, 400);
  await assert.rejects(register({}), (error) => error.fields.username === 'Already exists.');
  globalThis.fetch = async () => new Response('<html>Unavailable</html>', { status: 502 });
  await assert.rejects(register({}), (error) => error.status === 502 && /tidak dapat dibaca/.test(error.message));
  globalThis.fetch = async () => { throw new TypeError('offline'); };
  await assert.rejects(register({}), /Tidak dapat terhubung/);
});
