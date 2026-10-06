import { ApiError, publicRequest, request } from './api.js';
import { listPages, loadTarget } from './catalog.js';
import { sourceHref } from './study.js';

const id = (n) => Number.isSafeInteger(n) && n > 0;
export const uuid = (s) => typeof s === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(s);
export function proofHref(query, skill) {
  const p = new URLSearchParams(query); p.delete('learn'); p.delete('exam'); p.delete('submission');
  if (skill) p.set('learn', skill);
  return `/assessment?${p}`;
}
export async function loadAssessments(query, options) {
  const p = new URLSearchParams(query);
  const target = await loadTarget(query, options);
  const skillId = p.get('learn') || (target.kind === 'skill' ? target.id : null);
  if (p.getAll('learn').length > 1 || !id(Number(skillId))) throw new ApiError('Buka assessment dari skill di roadmap atau materi.');
  const skill = await publicRequest(`skills/${skillId}`, options);
  const competency = await publicRequest(`competencies/${skill.competency}`, options);
  if (skill.id !== Number(skillId) || competency.career_track !== target.track.id) throw new ApiError('Skill assessment bukan bagian target ini.');
  const assessments = await listPages(`assessments/?skill=${skill.id}`, options);
  if (assessments.some((a) => a.skill !== skill.id || typeof a.title !== 'string')) throw new ApiError('Daftar assessment tidak valid.');
  const exam = p.get('exam');
  if (p.getAll('exam').length > 1 || (exam && (!id(Number(exam)) || !assessments.some((a) => a.id === Number(exam))))) throw new ApiError('Assessment pada URL tidak sesuai skill.');
  const assessment = exam ? validateAssessment(await publicRequest(`assessments/${exam}`, options), Number(exam), skill.id) : null;
  const submissions = assessment ? await listPages(`assessments/submissions/?assessment=${exam}`, options, request) : [];
  submissions.forEach((s) => validateSubmission(s, assessment.id));
  const resultId = p.get('submission');
  if (p.getAll('submission').length > 1 || (resultId && (!id(Number(resultId)) || !submissions.some((s) => s.id === Number(resultId))))) throw new ApiError('Hasil tidak ditemukan untuk assessment dan akun ini.');
  return { target, skill, competency, assessments, assessment, submissions, result: submissions.find((s) => s.id === Number(resultId)) };
}
export function validateAssessment(a, exam, skill) {
  if (!a || a.id !== exam || a.skill !== skill || !['rules', 'ai'].includes(a.evaluation_mode) ||
      !Number.isFinite(a.max_score) || a.max_score <= 0 || !Number.isFinite(a.passing_score) || a.passing_score < 0 || a.passing_score > a.max_score ||
      !['title', 'instructions', 'objective', 'mastery_criteria', 'review_status'].every((k) => typeof a[k] === 'string') || !Array.isArray(a.expected_evidence) || !a.expected_evidence.every((s) => typeof s === 'string') ||
      !Array.isArray(a.questions) || !a.questions.every((q) => typeof q.id === 'string' && q.id && typeof q.prompt === 'string' &&
        Array.isArray(q.options) && q.options.length && q.options.every((o) => typeof o.value === 'string' && typeof o.label === 'string') && new Set(q.options.map((o) => o.value)).size === q.options.length) ||
      new Set(a.questions.map((q) => q.id)).size !== a.questions.length) throw new ApiError('Detail assessment tidak valid.');
  if (a.rubric !== undefined && (!Array.isArray(a.rubric) || !a.rubric.every((r) => r && typeof r.criterion === 'string' && Number.isFinite(r.weight)))) throw new ApiError('Rubrik assessment tidak valid.');
  return a;
}
export function assessmentPayload(a, answers, evidence, requestId) {
  if (!uuid(requestId)) throw new ApiError('Request ID tidak valid.');
  if (a.evaluation_mode === 'rules') {
    if (!a.questions.length) throw new ApiError('Assessment belum memiliki soal publik.');
    const missing = a.questions.filter((q) => !q.options.some((o) => o.value === answers[q.id]));
    if (missing.length) throw new ApiError('Jawab semua soal.', 400, Object.fromEntries(missing.map((q) => [q.id, 'Pilih satu jawaban.'])));
    return { request_id: requestId, content: { answers: Object.fromEntries(a.questions.map((q) => [q.id, answers[q.id]])) } };
  }
  if (!evidence.text?.trim()) throw new ApiError('Sertakan isi evidence atau kode; URL saja tidak dinilai.', 400, { text: 'Isi evidence wajib.' });
  for (const key of ['github_url', 'demo_url']) if (evidence[key] && !sourceHref(evidence[key])) throw new ApiError('URL harus HTTP(S) tanpa credentials.', 400, { [key]: 'URL tidak aman.' });
  if (new TextEncoder().encode(JSON.stringify(evidence)).length > 200000) throw new ApiError('Evidence maksimal 200 KB.', 400, { text: 'Evidence terlalu panjang.' });
  return { request_id: requestId, content: evidence };
}
export function validateSubmission(s, exam) {
  if (!s || !id(s.id) || s.assessment !== exam || !['draft', 'submitted', 'evaluating', 'completed'].includes(s.status) ||
      typeof s.is_passed !== 'boolean' || typeof s.feedback !== 'string' || !s.evaluation ||
      (s.status === 'completed' && (!Number.isFinite(s.score) || s.score < 0 || (s.evaluation.max_score !== undefined && (!Number.isFinite(s.evaluation.max_score) || s.score > s.evaluation.max_score))))) throw new ApiError('Hasil server belum dapat dipastikan. Muat ulang riwayat; jangan membuat attempt baru.');
  return s;
}
export function resultLabel(s) {
  const { provider, review_status: review } = s.evaluation || {};
  const simulated = ['mock', 'mock-fallback'].includes(provider);
  const draft = review === 'draft' || review === 'unreviewed';
  const reviewLabel = review === 'draft' ? 'standar draft' : 'standar belum direview';
  const qualifier = simulated ? 'simulasi' : draft ? reviewLabel : review !== 'reviewed' || !['rules', 'openai'].includes(provider) ? 'provenance belum lengkap' : '';
  const heading = s.status !== 'completed' ? 'Belum selesai dinilai' : s.is_passed
    ? qualifier === 'simulasi' ? 'Lulus simulasi assessment' : qualifier ? `Lulus assessment (${qualifier})` : 'Lulus assessment'
    : qualifier === 'simulasi' ? 'Belum lulus simulasi' : qualifier ? `Belum lulus (${qualifier})` : 'Belum lulus';
  const label = simulated ? `Simulasi ${provider}${draft ? ` · ${reviewLabel}` : ''} — bukan bukti kompetensi final.`
    : draft ? `${reviewLabel === 'standar draft' ? 'Standar draft' : 'Standar belum direview'} — bukan bukti kompetensi final.`
    : qualifier ? 'Provenance penilai/review belum lengkap — status evidence final belum dapat dipastikan.' : '';
  return { heading, label };
}
export async function submitAssessment(a, body) {
  const result = validateSubmission(await request(`assessments/${a.id}/submit`, { method: 'POST', body }), a.id);
  if (result.request_id !== body.request_id) throw new ApiError('Request hasil tidak cocok. Periksa riwayat sebelum mencoba lagi.');
  return result;
}
export async function recoverSubmission(a, requestId) {
  const items = await listPages(`assessments/submissions/?assessment=${a.id}&request_id=${requestId}`, undefined, request);
  if (items.some((s) => s.request_id !== requestId)) throw new ApiError('Request hasil recovery tidak cocok.');
  return items.length ? validateSubmission(items[0], a.id) : null;
}
export async function loadCredentials(query, options) {
  const p = new URLSearchParams(query);
  const page = p.get('page') || '1';
  if (!/^[1-9]\d*$/.test(page) || p.getAll('page').length > 1) throw new ApiError('Halaman credential tidak valid.');
  const list = await request(`credentials/?page=${page}`, options);
  if (!list || !Array.isArray(list.results) || !list.results.every((c) => uuid(c.id) && typeof c.competency_title === 'string' && ['draft', 'issued', 'revoked'].includes(c.status))) throw new ApiError('Daftar credential tidak valid.');
  const comp = p.get('claim');
  if (p.getAll('claim').length > 1 || (comp && !id(Number(comp)))) throw new ApiError('Competency credential tidak valid.');
  const eligibility = comp ? await request(`credentials/eligibility/${comp}`, options) : null;
  if (eligibility && (eligibility.competency !== Number(comp) || typeof eligibility.eligible !== 'boolean' || typeof eligibility.demo_ready !== 'boolean' || typeof eligibility.reason !== 'string' || !Array.isArray(eligibility.missing_skills))) throw new ApiError('Kelayakan dari server tidak valid.');
  const credentialId = p.get('id');
  if (p.getAll('id').length > 1 || (credentialId && !uuid(credentialId))) throw new ApiError('ID credential tidak valid.');
  const detail = credentialId ? await request(`credentials/${credentialId}`, options) : null;
  if (detail && (!uuid(detail.id) || detail.id !== credentialId || !Array.isArray(detail.evidences) || !detail.metadata || typeof detail.is_valid !== 'boolean')) throw new ApiError('Detail credential tidak valid.');
  return { list, eligibility, detail, page: Number(page) };
}
export async function loadVerification(credentialId, options) {
  if (!uuid(credentialId)) throw new ApiError('ID verifikasi harus UUID.');
  const data = await publicRequest(`verify/${credentialId}`, options);
  if (!data || data.credential_id !== credentialId || typeof data.is_valid !== 'boolean' || typeof data.integrity_verified !== 'boolean' || !Array.isArray(data.evidences) || !data.standard) throw new ApiError('Respons verifikasi tidak valid.');
  return data;
}
