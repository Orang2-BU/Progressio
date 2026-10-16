import { ApiError } from './api.js';

export function isQuestionAnswered(answers, questionId) {
  return Object.hasOwn(answers, questionId);
}

export function updateQuestionAnswer(answers, questionId, value) {
  return { ...answers, [questionId]: value };
}

export function getAnsweredQuestionCount(questions, answers) {
  return questions.filter((question) => isQuestionAnswered(answers, question.id)).length;
}

export function findFirstUnansweredQuestion(questions, answers) {
  return questions.findIndex((question) => !isQuestionAnswered(answers, question.id));
}

export function isUncertainDiagnosticSubmission(error) {
  return !error.status || error.status >= 500 || (error.status >= 200 && error.status < 300);
}

export function getDiagnosticFocusTarget({ promptFocusRequested, issue }) {
  if (promptFocusRequested) return 'prompt';
  if (issue) return 'summary';
  return null;
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
  const missing = questions.filter((q) => !isQuestionAnswered(answers, q.id));
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

export function diagnosticRadarGeometry(skillScores) {
  if (!Array.isArray(skillScores) || skillScores.length < 3 || skillScores.length > 8 ||
      !skillScores.every((skill) => typeof skill?.score === 'number' && Number.isFinite(skill.score) && skill.score >= 0 && skill.score <= 100)) return null;
  const center = 100;
  const radius = 66;
  const point = (index, scale) => {
    const angle = -Math.PI / 2 + (index * Math.PI * 2) / skillScores.length;
    return { x: Number((center + Math.cos(angle) * radius * scale).toFixed(2)), y: Number((center + Math.sin(angle) * radius * scale).toFixed(2)) };
  };
  return {
    rings: [0.25, 0.5, 0.75, 1].map((scale) => skillScores.map((_, index) => point(index, scale))),
    axes: skillScores.map((_, index) => point(index, 1)),
    values: skillScores.map((skill, index) => point(index, skill.score / 100)),
    labels: skillScores.map((_, index) => point(index, 1.22)),
  };
}
