import assert from 'node:assert/strict';
import test from 'node:test';
import { progressSummary, nextStudyStep, profileEmail, loadDashboardTarget, loadDashboardData, journeyStatuses, displayUsername } from '../src/dashboard.js';

test('dashboard summaries use only validated server progress and report empty accounts clearly', () => {
  assert.deepEqual(progressSummary({ total_xp: 0, completed_lessons_count: 0, completed_lesson_ids: [], skills: [] }),
    { totalXp: 0, completedLessons: 0, skillsWithMastery: 0 });
  assert.deepEqual(progressSummary({ total_xp: 120, completed_lessons_count: 2, completed_lesson_ids: [4, 5], skills: [{ mastery: 0 }, { mastery: 35 }] }),
    { totalXp: 120, completedLessons: 2, skillsWithMastery: 1 });
  assert.equal(profileEmail(''), 'Belum diisi');
  assert.equal(profileEmail('rama@example.test'), 'rama@example.test');
});

test('dashboard username is trimmed and falls back for missing or invalid values', () => {
  assert.equal(displayUsername({ username: '  Raka  ' }, 'teman'), 'Raka');
  assert.equal(displayUsername({ username: '   ' }, 'teman'), 'teman');
  assert.equal(displayUsername({ username: 42 }), 'Pengguna');
});

test('next study step comes from the server roadmap and never invents a checkpoint', () => {
  const roadmap = { steps: [{ skill_id: 42, skill_title: 'HTTP', order: 1 }, { skill_id: 43, skill_title: 'REST', order: 2 }] };
  assert.equal(nextStudyStep(roadmap), roadmap.steps[0]);
  assert.equal(nextStudyStep({ steps: [] }), null);
  assert.equal(nextStudyStep(null), null);
});

test('dashboard keeps validated target when roadmap fails and only marks supported journey stages', async () => {
  const target = { title: 'API Design' };
  const result = await loadDashboardTarget('track=1', undefined,
    async () => target,
    async () => { throw new Error('Roadmap belum tersedia.'); });
  assert.deepEqual(result, { target, roadmapError: 'Roadmap belum tersedia.' });
  assert.deepEqual(journeyStatuses(target, null), ['complete', 'upcoming', 'upcoming', 'upcoming', 'upcoming']);
  assert.deepEqual(journeyStatuses(target, { steps: [{ skill_id: 1 }] }), ['complete', 'upcoming', 'current', 'upcoming', 'upcoming']);
  assert.deepEqual(journeyStatuses(target, { steps: [] }), ['complete', 'upcoming', 'complete', 'upcoming', 'upcoming']);
});

test('dashboard data keeps independent failures and ignores results after cancellation', async () => {
  const data = await loadDashboardData('track=1', undefined,
    async () => { throw new Error('Progress offline'); },
    async () => ({ title: 'Backend' }),
    async () => ({ steps: [] }));
  assert.deepEqual(data, { progressError: 'Progress offline', target: { title: 'Backend' }, roadmap: { steps: [] } });

  const controller = new AbortController();
  let resolveProgress;
  const pending = loadDashboardData('', { signal: controller.signal },
    () => new Promise((resolve) => { resolveProgress = resolve; }),
    async () => assert.fail('No target should load without URL context'),
    async () => assert.fail('No roadmap should load without URL context'));
  await Promise.resolve();
  controller.abort();
  resolveProgress({ total_xp: 5, completed_lessons_count: 0, skills: [] });
  assert.equal(await pending, null);
});
