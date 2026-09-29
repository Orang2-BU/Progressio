import { ApiError, publicRequest, request } from './api.js';
import { loadTarget, listPages } from './catalog.js';

const id = (n) => Number.isSafeInteger(n) && n > 0;
const count = (n) => Number.isSafeInteger(n) && n >= 0;
const score = (n) => typeof n === 'number' && Number.isFinite(n) && n >= 0 && n <= 100;
export function studyHref(query, skillId) {
  if (!id(skillId)) throw new ApiError('Skill materi tidak valid.');
  const params = new URLSearchParams(query); params.set('learn', skillId);
  return `/study?${params}`;
}
export function sourceHref(value) {
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password ? url.href : null;
  } catch { return null; }
}
export function validateProgress(data) {
  if (!data || !count(data.total_xp) || !count(data.completed_lessons_count) ||
      !Array.isArray(data.completed_lesson_ids) || !data.completed_lesson_ids.every(id) ||
      new Set(data.completed_lesson_ids).size !== data.completed_lessons_count || data.completed_lesson_ids.length !== data.completed_lessons_count ||
      !Array.isArray(data.skills) || !data.skills.every((s) => s && id(s.skill) && score(s.mastery) && count(s.xp))) {
    throw new ApiError('Format progress dari server tidak valid.');
  }
  return data;
}
export const loadProgress = async (options) => validateProgress(await request('progress', options));

export async function loadStudy(query, options) {
  const params = new URLSearchParams(query);
  const value = params.get('learn');
  if (params.getAll('learn').length !== 1 || !/^[1-9]\d*$/.test(value || '') || !id(Number(value))) throw new ApiError('Pilih skill materi dari roadmap atau katalog.');
  const target = await loadTarget(query, options);
  const skill = await publicRequest(`skills/${value}`, options);
  if (!skill || skill.id !== Number(value) || !id(skill.competency) || typeof skill.title !== 'string' || typeof skill.slug !== 'string' || !skill.slug) throw new ApiError('Skill materi dari server tidak valid.');
  const competency = await publicRequest(`competencies/${skill.competency}`, options);
  if (competency?.career_track !== target.track.id) throw new ApiError('Skill materi bukan bagian dari career track target.');
  const [lessons, steps] = await Promise.all([listPages(`lessons?skill=${skill.id}`, options), listPages(`skills/${encodeURIComponent(skill.slug)}/study-plan`, options)]);
  if (!lessons.every((l) => l.skill === skill.id && typeof l.title === 'string' && count(l.duration) && count(l.order) &&
      ['content_url', 'content_type', 'provider', 'license', 'license_url', 'link_status'].every((key) => typeof l[key] === 'string') &&
      ['license_verified', 'attribution_required', 'redistributable', 'commercial_use_allowed'].every((key) => typeof l[key] === 'boolean')) ||
      new Set(lessons.map((l) => l.id)).size !== lessons.length ||
      !steps.every((s) => lessons.some((l) => l.id === s.lesson) && count(s.order) && count(s.estimated_minutes) &&
        ['prompt', 'checkpoint_question', 'study_url'].every((key) => typeof s[key] === 'string')) || new Set(steps.map((s) => s.id)).size !== steps.length) {
    throw new ApiError('Format materi/study plan dari server tidak valid.');
  }
  const rank = new Map();
  for (const step of steps) if (!rank.has(step.lesson)) rank.set(step.lesson, rank.size);
  lessons.sort((a, b) => a.order - b.order || (rank.get(a.id) ?? steps.length) - (rank.get(b.id) ?? steps.length) || a.id - b.id);
  return { target, skill, lessons, steps };
}

export async function submitCheckpoint(stepId, answer) {
  if (!id(stepId) || typeof answer !== 'string' || !answer.trim() || answer.trim().length > 255) throw new ApiError('Isi jawaban checkpoint, maksimal 255 karakter.', 400, { answer: 'Jawaban wajib diisi, maksimal 255 karakter.' });
  const data = await request(`study-steps/${stepId}/checkpoint`, { method: 'POST', body: { answer: answer.trim() } });
  if (typeof data?.correct !== 'boolean' || typeof data.feedback !== 'string') throw new ApiError('Format feedback checkpoint tidak valid.');
  return data;
}

export async function completeLesson(lessonId) {
  if (!id(lessonId)) throw new ApiError('ID materi tidak valid.');
  const data = await request(`lesson/${lessonId}/complete`, { method: 'POST' });
  if (!data || data.lesson_id !== lessonId || data.status !== 'completed' || !count(data.xp_earned) || typeof data.newly_completed !== 'boolean' ||
      !score(data.current_skill_mastery) || !count(data.current_skill_xp)) throw new ApiError('Respons completion tidak dapat dipastikan. Perbarui progress sebelum mencoba lagi.');
  return data;
}
