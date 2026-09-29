import { ApiError, publicRequest } from './api.js';

export async function listPages(path, options) {
  const items = [];
  const seen = new Set();
  let current = path;
  // ponytail: load all pages of small catalog/study lists; use server search/paging for large collections.
  while (current) {
    if (seen.has(current)) throw new ApiError('Pagination katalog berulang. Coba muat ulang.');
    seen.add(current);
    const data = await publicRequest(current, options);
    if (!data || !Array.isArray(data.results) || !Number.isInteger(data.count) ||
        !data.results.every((item) => item && Number.isSafeInteger(item.id) && item.id > 0)) {
      throw new ApiError('Format katalog dari server tidak valid.');
    }
    items.push(...data.results);
    if (data.next === null) break;
    if (typeof data.next !== 'string') throw new ApiError('Pagination katalog tidak valid.');
    const page = new URL(data.next, 'https://catalog.local').searchParams.get('page');
    if (!/^[1-9]\d*$/.test(page || '')) throw new ApiError('Pagination katalog tidak valid.');
    // Reuse only the page number; never forward requests to a server-supplied origin.
    const url = new URL(path, 'https://catalog.local');
    url.searchParams.set('page', page);
    current = url.pathname.slice(1) + url.search;
  }
  return items;
}

export async function listCatalog(path, options) {
  const items = await listPages(path, options);
  if (!items.every((item) => typeof item.title === 'string' && typeof item.slug === 'string' &&
      ['description', 'difficulty'].every((key) => item[key] === undefined || typeof item[key] === 'string') &&
      ['career_track', 'competency', 'estimated_learning_minutes'].every((key) => item[key] === undefined || (Number.isSafeInteger(item[key]) && item[key] >= 0)))) {
    throw new ApiError('Format katalog dari server tidak valid.');
  }
  return items;
}

export function parseSelection(params) {
  const selection = { track: '', competency: '', skill: '', target: params.get('target') || 'career_track' };
  for (const key of Object.keys(selection)) {
    if (params.getAll(key).length > 1) throw new Error('Parameter target tidak boleh berulang.');
    if (key === 'target') continue;
    const value = params.get(key) || '';
    if (value && (!/^[1-9]\d*$/.test(value) || !Number.isSafeInteger(Number(value)))) throw new Error('ID target pada URL tidak valid.');
    selection[key] = value;
  }
  if (!['career_track', 'competency', 'skill'].includes(selection.target) ||
      (selection.competency && !selection.track) || (selection.skill && !selection.competency) ||
      (selection.target === 'competency' && !selection.competency) || (selection.target === 'skill' && !selection.skill)) {
    throw new Error('Pilihan target pada URL belum lengkap atau tidak valid.');
  }
  return selection;
}

export function selectionHref(selection) {
  const params = new URLSearchParams();
  for (const key of ['track', 'competency', 'skill']) if (selection[key]) params.set(key, selection[key]);
  if (selection.target !== 'career_track') params.set('target', selection.target);
  return '/catalog' + (params.size ? '?' + params.toString() : '');
}

export function resolveTarget(selection, tracks, competencies, skills) {
  const track = tracks.find((item) => String(item.id) === selection.track);
  const competency = competencies.find((item) => String(item.id) === selection.competency);
  const skill = skills.find((item) => String(item.id) === selection.skill);
  if (selection.track && (!track || track.is_active !== true)) throw new Error('Career track tidak tersedia atau tidak aktif.');
  if (selection.competency && (!competency || competency.career_track !== track?.id)) throw new Error('Competency bukan bagian dari career track ini.');
  if (selection.skill && (!skill || skill.competency !== competency?.id)) throw new Error('Skill bukan bagian dari competency ini.');
  const record = { career_track: track, competency, skill }[selection.target];
  return record ? { ...record, kind: selection.target, track, competency, skill } : null;
}

export async function loadTarget(query, options) {
  const selection = parseSelection(new URLSearchParams(query));
  if (!selection.track) throw new ApiError('Pilih career track terlebih dahulu.');
  const [track, competency, skill] = await Promise.all([
    publicRequest(`career-tracks/${selection.track}`, options),
    selection.competency ? publicRequest(`competencies/${selection.competency}`, options) : null,
    selection.skill ? publicRequest(`skills/${selection.skill}`, options) : null,
  ]);
  const target = resolveTarget(selection, [track], competency ? [competency] : [], skill ? [skill] : []);
  if (!target || typeof target.title !== 'string' || typeof target.slug !== 'string' || !target.slug) throw new ApiError('Target dari server tidak valid.');
  return target;
}
