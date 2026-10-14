import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import { listCatalog, parseSelection, selectionHref, resolveTarget, filterSkills, countByDifficulty, formatMinutes } from '../src/catalog.js';
import { clearLocalSession, login } from '../src/api.js';
import { loginDestination } from '../src/navigation.js';

const originalFetch = globalThis.fetch;
const response = (body) => new Response(JSON.stringify(body));
const tracks = [{ id: 10, title: 'Backend', slug: 'backend', is_active: true }];
const competencies = [{ id: 20, title: 'API', slug: 'api', career_track: 10 }];
const skills = [{ id: 30, title: 'JWT', slug: 'jwt', competency: 20 }];
afterEach(() => { globalThis.fetch = originalFetch; clearLocalSession(); });

test('catalog pagination preserves parent filters and never attaches a token or follows an external URL', async () => {
  let pages = 0;
  globalThis.fetch = async (url, options) => {
    if (url.endsWith('auth/login')) return response({ access: 'secret-access', refresh: 'secret-refresh' });
    if (url.endsWith('auth/me')) return response({ id: 1, username: 'student' });
    assert.equal(options.headers.Authorization, undefined);
    pages += 1;
    assert.equal(url, pages === 1 ? '/api/v1/skills/?competency=20' : '/api/v1/skills/?competency=20&page=2');
    return response({ count: 2, next: pages === 1 ? 'https://other-origin.test/api/v1/skills/?competency=99&page=2' : null,
      results: [{ ...skills[0], id: pages === 1 ? 30 : 31 }] });
  };
  await login({ username: 'student', password: 'test' });
  assert.equal((await listCatalog('skills/?competency=20')).length, 2);
  assert.equal(pages, 2);
});

test('empty catalog, malformed payload and repeated pagination are handled', async () => {
  globalThis.fetch = async () => response({ count: 0, next: null, results: [] });
  assert.deepEqual(await listCatalog('career-tracks/'), []);
  globalThis.fetch = async () => response({ results: [{}], next: null });
  await assert.rejects(listCatalog('career-tracks/'), /Format katalog/);
  globalThis.fetch = async () => response({ count: 1, results: [null], next: null });
  await assert.rejects(listCatalog('career-tracks/'), /Format katalog/);
  globalThis.fetch = async () => response({ count: 1, results: tracks, next: '?page=1' });
  await assert.rejects(listCatalog('career-tracks/'), /berulang/);
  globalThis.fetch = async () => response({ count: 1, results: tracks, next: '?page=NaN' });
  await assert.rejects(listCatalog('career-tracks/'), /Pagination katalog tidak valid/);
});

test('cancelled catalog requests cannot proceed to a new page', async () => {
  const controller = new AbortController();
  let calls = 0;
  globalThis.fetch = async (url, options) => {
    calls += 1;
    assert.ok(options.signal);
    controller.abort();
    throw controller.signal.reason;
  };
  await assert.rejects(listCatalog('career-tracks/', { signal: controller.signal }), { name: 'AbortError' });
  assert.equal(calls, 1);
});

test('selection URLs round-trip all target kinds without trusting client-supplied slugs', () => {
  for (const target of ['career_track', 'competency', 'skill']) {
    const selection = { track: '10', competency: '20', skill: '30', target };
    const parsed = parseSelection(new URL(selectionHref(selection), 'https://local.test').searchParams);
    assert.deepEqual(parsed, selection);
    const resolved = resolveTarget(parsed, tracks, competencies, skills);
    assert.equal(resolved.slug, { career_track: 'backend', competency: 'api', skill: 'jwt' }[target]);
    assert.equal(resolved.track.id, 10);
  }
});

test('invalid IDs, duplicate parameters, missing parents, wrong ancestry and inactive tracks are rejected', () => {
  for (const query of ['track=-1', 'track=1.2', 'track=1&track=2', 'skill=30', 'target=unknown', 'track=10&target=skill', 'track=9007199254740993']) {
    assert.throws(() => parseSelection(new URLSearchParams(query)));
  }
  const selected = parseSelection(new URLSearchParams('track=10&competency=20&skill=30&target=skill'));
  assert.throws(() => resolveTarget(selected, tracks, [{ ...competencies[0], career_track: 99 }], skills), /Competency/);
  assert.throws(() => resolveTarget(selected, tracks, competencies, [{ ...skills[0], competency: 99 }]), /Skill/);
  assert.throws(() => resolveTarget(selected, [{ ...tracks[0], is_active: false }], competencies, skills), /aktif/);
  assert.throws(() => resolveTarget(selected, [], [], []), /tersedia/);
});

test('skill difficulty filter and search narrow only the loaded list, and an unmatched filter yields an empty result', () => {
  const list = [
    { id: 1, title: 'REST API Design', difficulty: 'intermediate' },
    { id: 2, title: 'Caching Basics', difficulty: 'beginner' },
    { id: 3, title: 'Observability', difficulty: 'advanced' },
  ];
  assert.deepEqual(countByDifficulty(list), { beginner: 1, intermediate: 1, advanced: 1 });
  assert.deepEqual(countByDifficulty([]), { beginner: 0, intermediate: 0, advanced: 0 });
  assert.equal(filterSkills(list, { search: '', difficulty: 'all' }).length, 3);
  assert.deepEqual(filterSkills(list, { search: '', difficulty: 'beginner' }).map((item) => item.id), [2]);
  assert.deepEqual(filterSkills(list, { search: 'api', difficulty: 'all' }).map((item) => item.id), [1]);
  assert.equal(filterSkills(list, { search: 'caching', difficulty: 'advanced' }).length, 0);
  assert.equal(filterSkills(list, {}).length, 3);
});

test('estimated minutes are formatted as hours/minutes and missing estimates are labelled, never shown as 0', () => {
  assert.equal(formatMinutes(45), '45 menit');
  assert.equal(formatMinutes(90), '1 jam 30 menit');
  assert.equal(formatMinutes(120), '2 jam');
  assert.equal(formatMinutes(0), 'Estimasi belum tersedia');
  assert.equal(formatMinutes(undefined), 'Estimasi belum tersedia');
  assert.equal(formatMinutes(-5), 'Estimasi belum tersedia');
});

test('login returns to the target URL and rejects external or unknown destinations', () => {
  assert.equal(loginDestination('/catalog?track=10&competency=20&skill=30&target=skill'), '/catalog?track=10&competency=20&skill=30&target=skill');
  assert.equal(loginDestination('/catalog/?track=10'), '/catalog?track=10');
  for (const next of ['https://evil.test', '//evil.test', '/\\evil.test', '/register', '/api/v1/auth/me', null]) assert.equal(loginDestination(next), '/');
});
