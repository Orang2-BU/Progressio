export function progressSummary(progress) {
  return {
    totalXp: progress.total_xp,
    completedLessons: progress.completed_lessons_count,
    skillsWithMastery: progress.skills.filter((skill) => skill.mastery > 0).length,
  };
}

export function nextStudyStep(roadmap) {
  return roadmap?.steps?.[0] || null;
}

export async function loadDashboardTarget(query, options, loadTarget, loadRoadmap) {
  const hasTargetContext = ['track', 'competency', 'skill', 'target'].some((key) => new URLSearchParams(query).has(key));
  if (!hasTargetContext) return {};
  let target;
  try { target = await loadTarget(query, options); }
  catch (error) { return { targetError: error.message }; }
  try { return { target, roadmap: await loadRoadmap(target, options) }; }
  catch (error) { return { target, roadmapError: error.message }; }
}

export async function loadDashboardData(query, options, loadProgress, loadTarget, loadRoadmap) {
  const progressRequest = Promise.resolve()
    .then(() => loadProgress(options))
    .then((progress) => ({ progress }), (error) => ({ progressError: error.message }));
  const targetRequest = loadDashboardTarget(query, options, loadTarget, loadRoadmap);
  const [progressResult, targetResult] = await Promise.all([progressRequest, targetRequest]);
  return options?.signal?.aborted ? null : { ...progressResult, ...targetResult };
}

export function journeyStatuses(target, roadmap) {
  return [
    target ? 'complete' : 'upcoming',
    'upcoming',
    roadmap ? (roadmap.steps.length ? 'current' : 'complete') : 'upcoming',
    'upcoming',
    'upcoming',
  ];
}

export function profileEmail(email) {
  return typeof email === 'string' && email.trim() ? email : 'Belum diisi';
}
export function displayUsername(user, fallback = 'Pengguna') {
  return typeof user?.username === 'string' && user.username.trim() ? user.username.trim() : fallback;
}
