import { ApiError, request } from './api.js';

export function roadmapPath(target) {
  if (!['career_track', 'competency', 'skill'].includes(target?.kind) || typeof target.slug !== 'string' || !target.slug) {
    throw new ApiError('Target roadmap tidak valid.');
  }
  return `roadmap?${new URLSearchParams({ [target.kind]: target.slug })}`;
}

export function validateRoadmap(data, target) {
  const text = (s) => typeof s === 'string' && s.trim().length > 0;
  const score = (n) => typeof n === 'number' && Number.isFinite(n) && n >= 0 && n <= 100;
  const minutes = (n) => Number.isSafeInteger(n) && n >= 0;
  const record = (s) => s && text(s.skill_slug) && text(s.skill_title) && score(s.mastery);
  if (!data || data.target?.type !== target.kind || data.target?.slug !== target.slug || !text(data.target?.title) ||
      !Array.isArray(data.steps) || !Array.isArray(data.already_satisfied) || data.total_steps !== data.steps.length ||
      !minutes(data.remaining_minutes) || typeof data.remaining_hours !== 'number' || !Number.isFinite(data.remaining_hours) || data.remaining_hours < 0 ||
      !data.already_satisfied.every(record) ||
      !data.steps.every((s, i) => record(s) && Number.isSafeInteger(s.skill_id) && s.skill_id > 0 && s.order === i + 1 &&
        text(s.competency_title) && text(s.difficulty) && minutes(s.estimated_minutes) && typeof s.is_target === 'boolean' &&
        Array.isArray(s.prerequisites) && s.prerequisites.every(text))) {
    throw new ApiError('Format roadmap dari server tidak valid.');
  }
  const all = [...data.steps, ...data.already_satisfied];
  if (new Set(all.map((s) => s.skill_slug)).size !== all.length ||
      new Set(data.steps.map((s) => s.skill_id)).size !== data.steps.length ||
      data.remaining_minutes !== data.steps.reduce((sum, s) => sum + s.estimated_minutes, 0) ||
      Math.abs(data.remaining_hours - data.remaining_minutes / 60) > 0.051 ||
      data.steps.some((s, i) => s.prerequisites.some((slug) => data.steps.findIndex((p) => p.skill_slug === slug) >= i))) {
    throw new ApiError('Urutan atau ringkasan roadmap dari server tidak valid.');
  }
  return data;
}

export async function loadRoadmap(target, options) {
  return validateRoadmap(await request(roadmapPath(target), options), target);
}
