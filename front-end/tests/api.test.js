import assert from 'node:assert/strict';
import { afterEach, beforeEach, describe, test } from 'node:test';
import React from 'react';
import nextConfig from '../next.config.mjs';
import { ApiError, getSession, getServerSession, login, logout, register, reloadProfile, request } from '../src/api.js';
import { loadProgress } from '../src/study.js';
import { foundationRenderer } from './support/render-foundation.js';

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

test('non-object JSON error bodies fall back to a readable API error', async () => {
  globalThis.fetch = async () => new Response(JSON.stringify('unavailable'), { status: 503 });
  await assert.rejects(register({}), (error) => error.status === 503 && /Permintaan belum berhasil/.test(error.message));
});

test('failed profile reload reports the error without clearing the authenticated identity', async () => {
  let profileCalls = 0;
  globalThis.fetch = async (url) => {
    if (url.endsWith('auth/login')) return response({ access: 'initial', refresh: 'refresh-token' });
    if (url.endsWith('auth/me')) {
      profileCalls += 1;
      return profileCalls === 1 ? response(profile) : response({ detail: 'Service unavailable' }, 503);
    }
    throw new Error(`Unexpected request: ${url}`);
  };
  await login({ username: 'student', password: 'secret' });
  const originalUser = getSession().user;
  await assert.rejects(reloadProfile(), /Service unavailable/);
  assert.equal(getSession().user, originalUser);
});

test('progress API failure can be retried without clearing the authenticated identity', async () => {
  globalThis.fetch = async (url) => {
    if (url.endsWith('auth/login')) return response({ access: 'initial', refresh: 'refresh-token' });
    if (url.endsWith('auth/me')) return response(profile);
    if (url.endsWith('progress')) return response({ detail: 'Service unavailable' }, 503);
    throw new Error(`Unexpected request: ${url}`);
  };
  await login({ username: 'student', password: 'secret' });
  const originalUser = getSession().user;
  await assert.rejects(loadProgress(), /Service unavailable/);
  assert.equal(getSession().user, originalUser);
});

// Keep foundation regression coverage in the frontend-only default test entrypoint.
describe('frontend foundation rendering', () => {
  const originalFoundationFetch = globalThis.fetch;
  beforeEach(() => { globalThis.fetch = () => { throw new Error('Foundation rendering must not contact any API'); }; });
  afterEach(() => { globalThis.fetch = originalFoundationFetch; });

  test('expired session and registration reasons render their notices', () => {
    for (const reason of ['Sesi berakhir. Masuk kembali untuk melanjutkan.', 'Akun pelajar-qa berhasil dibuat. Masuk dengan username dan kata sandimu.']) {
      const { app, render } = foundationRenderer({ session: { user: null, reason } });
      const markup = render(app.AuthPage, { mode: 'login' });
      assert.match(markup, /role="status"/);
      if (reason.startsWith('Sesi berakhir')) {
        assert.match(markup, /ui-notice-warning/);
        assert.match(markup, /<strong>Sesi berakhir<\/strong>/);
        assert.doesNotMatch(markup, /<strong>Berhasil<\/strong>/);
      } else {
        assert.match(markup, /ui-notice-success/);
        assert.match(markup, /<strong>Berhasil<\/strong>/);
      }
      assert.ok(markup.includes(reason));
      assert.match(markup, /Sesi hanya tersimpan selama halaman ini terbuka/);
    }
  });

  test('SSR stays deterministic and the client logout query resolves its success notice', () => {
    const originalWindow = globalThis.window;
    globalThis.window = { location: { search: '?logged_out=1' } };
    try {
      const { app, render } = foundationRenderer({ session: { user: null, reason: '' } });
      const markup = render(app.AuthPage, { mode: 'login' });
      assert.doesNotMatch(markup, /Kamu sudah keluar dari akun\./);
      assert.equal(app.logoutNoticeFromSearch(new URLSearchParams(window.location.search)), 'Kamu sudah keluar dari akun.');
      assert.equal(app.logoutNoticeFromSearch(new URLSearchParams('')), '');
    } finally {
      if (originalWindow === undefined) delete globalThis.window;
      else globalThis.window = originalWindow;
    }
  });

  test('workspace marks exactly one of four destination links, and no flow link', () => {
    for (const path of ['/', '/catalog', '/credentials', '/profile', '/catalog/', '/diagnostic', '/diagnostic/result', '/roadmap', '/study', '/assessment', '/catalog/detail']) {
      const { app, render } = foundationRenderer({ path });
      const markup = render(app.WorkspaceLayout, { children: 'Konten QA' });
      const navigation = markup.match(/<nav aria-label="Navigasi workspace">([\s\S]*?)<\/nav>/)[1];
      assert.equal((navigation.match(/<a /g) || []).length, 4);
      const normalized = path.replace(/\/$/, '') || '/';
      const expected = ['/', '/catalog', '/credentials', '/profile'].includes(normalized);
      const active = [...navigation.matchAll(/<a\b[^>]*aria-current="page"[^>]*>/g)];
      assert.equal(active.length, expected ? 1 : 0, path);
      if (expected) assert.ok(active[0][0].includes(`href="${normalized}"`), path);
    }
  });

  test('diagnostic focus shell omits workspace chrome and announces actual progress', () => {
    const { app, render } = foundationRenderer({ path: '/diagnostic', session: { user: { username: 'pelajar-qa', role: 'student' }, reason: '' } });
    const markup = render(app.default, { children: React.createElement(app.FocusLayout, { exitHref: '/catalog?track=10', completed: 2, total: 5 }, 'Soal QA') });
    assert.doesNotMatch(markup, /class="topbar"|<footer|Navigasi workspace/);
    assert.match(markup, /Soal QA/);
    assert.doesNotMatch(markup, /Mengalihkan halaman/);
    assert.match(markup, /href="#main"/);
    const focus = render(app.FocusLayout, { exitHref: '/catalog?track=10', completed: 2, total: 5, children: 'Soal QA' });
    assert.match(focus, /aria-label="Tutup diagnostic dan kembali ke target"/);
    assert.match(focus, /href="\/catalog\?track=10"/);
    assert.match(focus, /aria-valuenow="2"/);
    assert.match(focus, /aria-valuemax="5"/);
    assert.match(focus, /2 \/ 5 dijawab/);
  });

  test('public verification loading SSR markup omits sidebar and redirect placeholder', () => {
    const { app, render, load } = foundationRenderer({ path: '/verify/11111111-1111-4111-8111-111111111111' });
    const proof = load('Proof.jsx').default;
    const markup = render(app.default, { children: React.createElement(proof, { mode: 'verify', credentialId: '11111111-1111-4111-8111-111111111111' }) });
    assert.match(markup, /Verifikasi credential/);
    assert.match(markup, /role="status">Memuat data server/);
    assert.match(markup, /mock dan standar draft bukan bukti final/);
    assert.doesNotMatch(markup, /Navigasi workspace|Mengalihkan halaman/);
  });

  test('shared loading, empty and error states expose visible text and semantic roles', () => {
    const { ui, render } = foundationRenderer();
    assert.match(render(ui.LoadingState, { children: 'Memuat target…' }), /role="status"[\s\S]*Memuat target/);
    const empty = render(ui.EmptyState, { title: 'Belum ada target', children: 'Pilih target untuk mulai.', action: React.createElement(ui.Button, { href: '/catalog' }, 'Pilih target') });
    assert.match(empty, /role="status"/);
    assert.match(empty, /Belum ada target/);
    assert.match(empty, /href="\/catalog"/);
    assert.match(render(ui.Notice, { tone: 'error', children: 'Tidak dapat memuat target.' }), /role="alert"[\s\S]*Kesalahan[\s\S]*Tidak dapat memuat target/);
    const unknown = render(ui.ProgressBar, { value: 4, max: 0, label: 'Soal dijawab' });
    assert.match(unknown, /aria-valuetext="Total belum tersedia"/);
    assert.doesNotMatch(unknown, /aria-valuenow=/);
  });

  test('auth forms retain input labels, password toggle and supported registration roles', () => {
    const { app, render } = foundationRenderer();
    for (const mode of ['login', 'register']) {
      const markup = render(app.AuthPage, { mode });
      assert.match(markup, /<label for="username">Username<\/label>/);
      assert.match(markup, /<input[^>]*id="username"[^>]*name="username"/);
      assert.match(markup, /<label for="password">Kata sandi<\/label>/);
      assert.match(markup, /<input[^>]*type="password"/);
      assert.match(markup, /<button[^>]*type="button"[^>]*aria-pressed="false">Lihat/);
      if (mode === 'register') {
        assert.match(markup, /<label for="role">Saya bergabung sebagai/);
        assert.match(markup, /value="student"/);
        assert.match(markup, /value="recruiter"/);
        assert.match(markup, /Konfirmasi kata sandi/);
      }
    }
  });

  test('dashboard and profile render honest server-backed loading and unsupported states', () => {
    const user = { username: 'pelajar-qa', email: 'pelajar@example.test', role: 'student', date_joined: '2026-09-29T00:00:00Z' };
    const { load, render } = foundationRenderer({ path: '/', session: { user, reason: '' } });
    const dashboard = render(load('Dashboard.jsx').default, { user });
    assert.match(dashboard, /Halo, pelajar-qa/);
    assert.match(dashboard, /Pilih target belajar pertamamu/);
    assert.match(dashboard, /Memuat ringkasan akun dan progres belajar/);
    assert.doesNotMatch(dashboard, /Total XP[\s\S]*?<strong>\d/);

    const profile = render(load('Profile.jsx').default);
    assert.match(profile, />pelajar-qa</);
    assert.match(profile, /pelajar@example\.test/);
    assert.match(profile, /Memuat kemajuan akun/);
    assert.match(profile, /Streak, level, lencana, dan peta aktivitas belum tersedia dari server/);
    assert.match(profile, /Edit profil, segera/);
    assert.match(profile, /Ganti kata sandi, segera/);
    assert.match(profile, /Pengingat belajar, segera/);
    assert.match(profile, /Privasi profil, segera/);
  });
});
