'use client';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { publicRequest } from './api.js';
import { listCatalog, parseSelection, selectionHref, resolveTarget } from './catalog.js';
import { studyHref } from './study.js';

const empty = { track: '', competency: '', skill: '', target: 'career_track' };
const names = { career_track: 'Career track', competency: 'Competency', skill: 'Skill' };
const difficulties = { beginner: 'Pemula', intermediate: 'Menengah', advanced: 'Lanjutan' };

function useLoad(path, revision, loader = listCatalog) {
  const [state, setState] = useState({ path: null, loading: false, data: null, error: '' });
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    setState({ path, loading: true, data: null, error: '' });
    loader(path, { signal: controller.signal }).then((data) => {
      if (!controller.signal.aborted) setState({ path, loading: false, data, error: '' });
    }).catch((error) => {
      if (!controller.signal.aborted) setState({ path, loading: false, data: null, error: error.message });
    });
    return () => controller.abort();
  }, [path, revision, loader]);
  return path && state.path === path ? state : { loading: Boolean(path), data: null, error: '' };
}

export default function Catalog() {
  const params = useSearchParams();
  const router = useRouter();
  const [revision, setRevision] = useState(0);
  const [copied, setCopied] = useState(null);
  let selection = empty;
  let invalid = '';
  try { selection = parseSelection(params); } catch (error) { invalid = error.message; }
  const tracks = useLoad('career-tracks/', revision);
  const track = tracks.data?.find((item) => String(item.id) === selection.track && item.is_active);
  const competencies = useLoad(track ? `competencies/?career_track=${track.id}` : null, revision);
  const competency = competencies.data?.find((item) => String(item.id) === selection.competency && item.career_track === track?.id);
  const skills = useLoad(competency ? `skills/?competency=${competency.id}` : null, revision);
  const skill = skills.data?.find((item) => String(item.id) === selection.skill && item.competency === competency?.id);
  const detail = useLoad(skill ? `skills/${skill.id}` : null, revision, publicRequest);
  const validDetail = detail.data?.id === skill?.id && detail.data?.competency === competency?.id &&
    Number.isInteger(detail.data?.lesson_count) && Array.isArray(detail.data?.prerequisites) &&
    detail.data.prerequisites.every((item) => Number.isInteger(item.id) && typeof item.required_skill_title === 'string');
  const pending = [tracks, competencies, skills, detail].some((state) => state.loading);
  const error = [tracks, competencies, skills, detail].find((state) => state.error)?.error;
  let target = null;
  if (!pending && !error && !invalid) {
    try { target = resolveTarget(selection, tracks.data || [], competencies.data || [], skills.data || []); }
    catch (issue) { invalid = issue.message; }
    if (skill && !validDetail) {
      invalid = 'Detail skill dari server tidak sesuai pilihan.'; target = null;
    }
  }
  const href = selectionHref(selection);
  function change(key, value) {
    const next = { ...selection, [key]: value };
    if (key === 'track') { next.competency = ''; next.skill = ''; next.target = 'career_track'; }
    if (key === 'competency') { next.skill = ''; if (next.target === 'skill' || !value) next.target = 'career_track'; }
    if (key === 'skill' && !value && next.target === 'skill') next.target = 'career_track';
    setCopied(null); router.push(selectionHref(next), { scroll: false });
  }
  async function copy() {
    try { await navigator.clipboard.writeText(new URL(href, window.location.origin).href); setCopied({ href, message: 'Tautan target disalin.' }); }
    catch { setCopied({ href, message: 'Tidak dapat menyalin. Salin URL dari bilah alamat browser.' }); }
  }
  function selector(key, label, state, enabled, placeholder) {
    return <div className="field"><label htmlFor={key}>{label}</label>
      <select id={key} value={selection[key]} disabled={!enabled || state.loading || Boolean(state.error)} aria-describedby={`${key}-status`} onChange={(event) => change(key, event.target.value)}>
        <option value="">{placeholder}</option>{(state.data || []).map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
      </select><p id={`${key}-status`} className="hint">{state.loading ? 'Memuat katalog…' : !enabled ? 'Pilih parent terlebih dahulu.' : state.error ? 'Katalog gagal dimuat.' : state.data?.length === 0 ? 'Belum ada pilihan pada katalog ini.' : `${state.data?.length || 0} pilihan tersedia.`}</p>
    </div>;
  }
  return <WorkspaceLayout><section className="workspace-content catalog-content">
    <p className="eyebrow">01 / TENTUKAN ARAH</p><h1>Targetmu, titik awalmu.</h1>
    <p className="intro">Pilih jalur karier, lalu persempit ke competency atau skill. Pilihan ini menentukan kemampuan yang nantinya diukur, bukan bukti bahwa kamu sudah menguasainya.</p>
    <div className="catalog-grid"><section className="profile-card" aria-labelledby="catalog-title" aria-busy={pending}>
      <div className="section-heading"><h2 id="catalog-title">Jelajahi katalog</h2><span className="status">Data server</span></div>
      <div className="catalog-fields">
        {selector('track', '1. Career track', tracks, true, 'Pilih career track')}
        {selector('competency', '2. Competency (opsional)', competencies, Boolean(track), 'Seluruh career track')}
        {selector('skill', '3. Skill (opsional)', skills, Boolean(competency), 'Seluruh competency')}
      </div>
      {error && <div className="error-summary" role="alert"><p>{error}</p><button className="button secondary" onClick={() => setRevision(revision + 1)}>Coba lagi</button></div>}
      {invalid && <div className="error-summary" role="alert"><p>{invalid}</p><Link href="/catalog">Reset pilihan</Link></div>}
      {!tracks.loading && !tracks.error && tracks.data?.length === 0 && <p className="notice">Belum ada career track aktif. Administrator perlu mengimpor kurikulum sebelum target bisa dipilih.</p>}
      {track && <div className="catalog-description"><h3>{track.title}</h3><p>{track.description || 'Belum ada deskripsi career track.'}</p></div>}
      {competency && <div className="catalog-description"><h3>{competency.title}</h3><p>{competency.description || 'Belum ada deskripsi competency.'}</p></div>}
      {skill && <div className="catalog-description"><h3>{skill.title}</h3><p>{skill.description || 'Belum ada deskripsi skill.'}</p>
        <p className="hint">{difficulties[skill.difficulty] || skill.difficulty} · Estimasi belajar {skill.estimated_learning_minutes} menit (bukan skor kemampuan).</p>
        {validDetail && !invalid && <><h4>Prasyarat skill</h4>{detail.data.prerequisites.length ? <ul>{detail.data.prerequisites.map((item) => <li key={item.id}>{item.required_skill_title}</li>)}</ul> : <p>Tidak ada prasyarat skill pada katalog.</p>}
          <p className="hint">{detail.data.lesson_count} materi tersedia. Materi bukan kriteria penerbitan credential.</p></>}
      </div>}
    </section>
    <aside className="profile-card target-summary" aria-labelledby="target-title">
      <p className="eyebrow">PILIHANMU</p><h2 id="target-title">Cakupan target</h2>
      <fieldset disabled={pending || Boolean(error || invalid) || !track}><legend>Yang ingin saya capai</legend>
        {['career_track', 'competency', 'skill'].map((kind) => <label className="target-option" key={kind}>
          <input type="radio" name="target" value={kind} checked={selection.target === kind} disabled={kind === 'competency' ? !competency : kind === 'skill' ? !skill : !track} onChange={() => change('target', kind)} />{names[kind]}</label>)}
      </fieldset>
      <div className="target-result" role="status" aria-live="polite">
        {pending ? <p>Memuat pilihan…</p> : error || invalid ? <p>Target belum bisa digunakan. Perbaiki pilihan atau muat ulang katalog.</p> : target ? <><span className="eyebrow">{names[target.kind]}</span><h3>{target.title}</h3><p className="hint">Slug: {target.slug}</p><p>Career track: {target.track.title}</p></> : <p>Pilih career track untuk menentukan target.</p>}
      </div>
      <button className="button primary full" disabled={!target || pending || Boolean(error || invalid)} onClick={copy}>Salin tautan target <span aria-hidden="true">↗</span></button>
      {copied?.href === href && <p className="hint" role="status">{copied.message}</p>}
      <p className="session-note">Pilihan tersimpan pada URL, bukan di profil server. Tautan dapat dibuka kembali; login tetap diperlukan.</p>
      {target && !pending && !error && !invalid && <Link className="button primary full" href={href.replace('/catalog', '/diagnostic')}>Ukur titik awal</Link>}
      {target && !pending && !error && !invalid && <Link className="button secondary full" href={href.replace('/catalog', '/roadmap')}>Lihat roadmap target</Link>}
      {target && skill && !pending && !error && !invalid && <Link className="button secondary full" href={studyHref(href.split('?')[1] || '', skill.id)}>Buka materi skill pilihan</Link>}
      <p className="hint">Diagnostic mencakup seluruh career track. Roadmap mengikuti cakupan target dan mastery tersimpan; diagnostic belum wajib.</p>
    </aside></div>
  </section></WorkspaceLayout>;
}
