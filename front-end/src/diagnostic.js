import { ApiError, publicRequest } from './api.js';
import { parseSelection, resolveTarget } from './catalog.js';

export async function diagnosticTarget(query, options) {
  const selection = parseSelection(new URLSearchParams(query));
  if (!selection.track) throw new ApiError('Pilih career track terlebih dahulu.');
  const [track, competency, skill] = await Promise.all([
    publicRequest(`career-tracks/${selection.track}`, options),
    selection.competency ? publicRequest(`competencies/${selection.competency}`, options) : null,
    selection.skill ? publicRequest(`skills/${selection.skill}`, options) : null,
  ]);
  const target = resolveTarget(selection, [track], competency ? [competency] : [], skill ? [skill] : []);
  if (!target || typeof target.title !== 'string') throw new ApiError('Target dari server tidak valid.');
  return target;
}

export function validateQuestions(data) {
  const ids = new Set();
  if (!Array.isArray(data) || !data.every((q) => {
    if (!q || !Number.isSafeInteger(q.id) || q.id < 1 || ids.has(q.id) ||
        typeof q.prompt !== 'string' || !q.prompt.trim() || typeof q.skill_title !== 'string' ||
        !Array.isArray(q.options) || !q.options.length) return false;
    ids.add(q.id);
    const values = new Set();
    return q.options.every((o) => {
      if (!o || typeof o.value !== 'string' || !o.value.trim() || typeof o.label !== 'string' || !o.label.trim() || values.has(o.value)) return false;
      values.add(o.value); return true;
    });
  })) throw new ApiError('Format soal dari server tidak valid.');
  return data;
}

export function diagnosticPayload(questions, answers) {
  const missing = questions.filter((q) => !Object.hasOwn(answers, q.id));
  if (missing.length) throw new ApiError('Jawab semua soal, atau pilih Belum tahu.', 400,
    Object.fromEntries(missing.map((q) => [q.id, 'Pilih satu jawaban.'])));
  if (!questions.length || questions.some((q) => answers[q.id] !== '' && !q.options.some((o) => o.value === answers[q.id]))) {
    throw new ApiError('Jawaban tidak sesuai pilihan soal.');
  }
  return { answers: Object.fromEntries(questions.map((q) => [q.id, answers[q.id]])) };
}

export function validateAttempt(data, trackId) {
  const score = (n) => typeof n === 'number' && Number.isFinite(n) && n >= 0 && n <= 100;
  if (!data || !Number.isSafeInteger(data.id) || data.id < 1 || data.career_track !== trackId ||
      !score(data.overall_score) || !data.completed_at || !Number.isFinite(Date.parse(data.completed_at)) ||
      !Array.isArray(data.skill_scores) || !data.skill_scores.length ||
      !data.skill_scores.every((s) => s && Number.isSafeInteger(s.skill_id) && s.skill_id > 0 && typeof s.skill_title === 'string' && score(s.score) &&
        Number.isInteger(s.total_questions) && s.total_questions > 0 && Number.isInteger(s.correct_answers) && s.correct_answers >= 0 && s.correct_answers <= s.total_questions) ||
      new Set(data.skill_scores.map((s) => s.skill_id)).size !== data.skill_scores.length ||
      !Array.isArray(data.recommended_skill_ids) || !data.recommended_skill_ids.every((id) => data.skill_scores.some((s) => s.skill_id === id))) {
    throw new ApiError('Format hasil diagnostic dari server tidak valid.');
  }
  return data;
}
