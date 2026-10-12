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
