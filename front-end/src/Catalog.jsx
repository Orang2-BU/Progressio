'use client';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { WorkspaceLayout } from './App.jsx';
import { publicRequest } from './api.js';
import {
  listCatalog, parseSelection, selectionHref, resolveTarget,
  filterSkills, countByDifficulty, formatMinutes,
} from './catalog.js';
import { studyHref } from './study.js';
import { Icon, DifficultyTag, EmptyState, LoadingState } from './ui.jsx';

const empty = { track: '', competency: '', skill: '', target: 'career_track' };
const names = { career_track: 'Career track', competency: 'Competency', skill: 'Skill' };
const targetIcons = { career_track: 'route', competency: 'chart', skill: 'book' };
const difficultyTabs = [['all', 'Semua'], ['beginner', 'Pemula'], ['intermediate', 'Menengah'], ['advanced', 'Mahir']];

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
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState('all');
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
  useEffect(() => { setSearch(''); setDifficulty('all'); }, [competency?.id]);
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
  function retry() { setRevision(revision + 1); }
  function resetFilters() { setSearch(''); setDifficulty('all'); }

  const totalSkills = skills.data?.length || 0;
  const difficultyCounts = countByDifficulty(skills.data || []);
  const visibleSkills = filterSkills(skills.data || [], { search, difficulty });

  function errorBlock(message) {
    return <div className="error-summary" role="alert"><p>{message}</p><button className="button secondary" onClick={retry}>Coba lagi</button></div>;
  }

  return <WorkspaceLayout><section className="workspace-content catalog-content">
    <p className="eyebrow">01 / TENTUKAN ARAH</p><h1>Pilih target kompetensimu</h1>
    <p className="intro">Kurikulum adalah standar penilaian, bukan daftar materi yang wajib dibaca. Pilih career track, lalu persempit ke competency atau skill — kami ukur titik awalmu, lalu susun langkahnya.</p>
    {invalid && <div className="error-summary" role="alert"><p>{invalid}</p><Link href="/catalog">Reset pilihan</Link></div>}
    <div className="catalog-layout">
      <div className="catalog-steps">
        <section className="catalog-step" aria-labelledby="track-heading" aria-busy={tracks.loading}>
          <div className="catalog-step-head"><span className="step-badge">1</span><h2 id="track-heading">Career track</h2><span className="hint">Bidang besar yang ingin kamu tekuni</span></div>
          {tracks.loading && <LoadingState>Memuat career track…</LoadingState>}
          {!tracks.loading && tracks.error && errorBlock(tracks.error)}
          {!tracks.loading && !tracks.error && tracks.data?.length === 0 &&
            <EmptyState icon="target" title="Belum ada career track aktif">Administrator perlu mengimpor kurikulum sebelum target bisa dipilih.</EmptyState>}
          {!tracks.loading && !tracks.error && tracks.data?.length > 0 && <>
            <div className="catalog-track-grid" role="radiogroup" aria-labelledby="track-heading">
              {tracks.data.filter((item) => item.is_active).map((item) => <label className="catalog-track-card" key={item.id}>
                <input type="radio" name="track" checked={selection.track === String(item.id)} onChange={() => change('track', String(item.id))} />
                <span className="catalog-track-icon" aria-hidden="true"><Icon name="route" size={24} /></span>
                <span className="catalog-track-title">{item.title}</span>
                <span className="catalog-track-desc">{item.description || 'Belum ada deskripsi career track.'}</span>
              </label>)}
            </div>
            {track && <div className="catalog-description"><h3>{track.title}</h3><p>{track.description || 'Belum ada deskripsi career track.'}</p></div>}
          </>}
        </section>

        {track && <section className="catalog-step" aria-labelledby="competency-heading" aria-busy={competencies.loading}>
          <div className="catalog-step-head"><span className="step-badge">2</span><h2 id="competency-heading">Competency</h2><span className="hint">di <b>{track.title}</b> · opsional</span></div>
          {competencies.loading && <LoadingState>Memuat competency…</LoadingState>}
          {!competencies.loading && competencies.error && errorBlock(competencies.error)}
          {!competencies.loading && !competencies.error && <>
            <div className="catalog-competency-pills" role="radiogroup" aria-labelledby="competency-heading">
              <label className="catalog-competency-pill is-clear"><input type="radio" name="competency" checked={!selection.competency} onChange={() => change('competency', '')} />Seluruh career track</label>
              {competencies.data?.map((item) => <label className="catalog-competency-pill" key={item.id}>
                <input type="radio" name="competency" checked={selection.competency === String(item.id)} onChange={() => change('competency', String(item.id))} />{item.title}
              </label>)}
            </div>
            {competencies.data?.length === 0 &&
              <EmptyState icon="info" title="Belum ada competency">Career track ini belum memiliki competency. Target tetap bisa diarahkan ke seluruh career track.</EmptyState>}
            {competency && <div className="catalog-description"><h3>{competency.title}</h3><p>{competency.description || 'Belum ada deskripsi competency.'}</p></div>}
          </>}
        </section>}

        {competency && <section className="catalog-step" aria-labelledby="skill-heading" aria-busy={skills.loading}>
          <div className="catalog-step-head"><span className="step-badge">3</span><h2 id="skill-heading">Skill</h2><span className="hint">Satu skill = satu target yang diukur &amp; dibuktikan · opsional</span></div>
          {skills.loading && <LoadingState>Memuat skill…</LoadingState>}
          {!skills.loading && skills.error && errorBlock(skills.error)}
          {!skills.loading && !skills.error && totalSkills === 0 &&
            <EmptyState icon="info" title="Belum ada skill">Competency ini belum memiliki skill. Target tetap bisa diarahkan ke competency.</EmptyState>}
          {!skills.loading && !skills.error && totalSkills > 0 && <div className="catalog-skill-card">
            <div className="catalog-skill-toolbar">
              <label className="catalog-skill-search"><span className="sr-only">Cari skill</span>
                <input type="search" value={search} placeholder="Cari skill, misalnya caching" onChange={(event) => setSearch(event.target.value)} />
              </label>
            </div>
            <div className="catalog-skill-tabs" role="group" aria-label="Filter tingkat kesulitan">
              {difficultyTabs.map(([key, label]) => <button key={key} type="button" aria-pressed={difficulty === key}
                className={`catalog-skill-tab${difficulty === key ? ' is-active' : ''}`} onClick={() => setDifficulty(key)}>
                {label} <span className="catalog-skill-tab-count">{key === 'all' ? totalSkills : difficultyCounts[key]}</span>
              </button>)}
            </div>
            <div className="catalog-skill-rows" role="radiogroup" aria-label="Daftar skill">
              <div className="catalog-skill-head" aria-hidden="true"><span>Skill</span><span>Tingkat</span><span>Estimasi</span></div>
              <label className="catalog-skill-row is-clear"><input type="radio" name="skill" checked={!selection.skill} onChange={() => change('skill', '')} />
                <span className="catalog-skill-main"><span className="catalog-skill-title">Seluruh competency</span>
                  <span className="catalog-skill-desc">Ukur semua skill pada competency ini, tanpa target skill tunggal.</span></span>
              </label>
              {visibleSkills.length === 0 ? <div className="catalog-skill-empty">
                <p>Tidak ada skill yang cocok dengan filter ini.</p>
                <button type="button" className="button secondary" onClick={resetFilters}>Reset filter</button>
              </div> : visibleSkills.map((item) => <label className="catalog-skill-row" key={item.id}>
                <input type="radio" name="skill" checked={selection.skill === String(item.id)} onChange={() => change('skill', String(item.id))} />
                <span className="catalog-skill-main"><span className="catalog-skill-title">{item.title}</span>
                  {item.description && <span className="catalog-skill-desc">{item.description}</span>}</span>
                <DifficultyTag level={item.difficulty} />
                <span className="catalog-skill-estimate">{formatMinutes(item.estimated_learning_minutes)}</span>
              </label>)}
            </div>
            <p className="hint catalog-skill-summary">Menampilkan <b>{visibleSkills.length}</b> dari <b>{totalSkills}</b> skill.</p>
          </div>}
          {skill && detail.loading && <LoadingState>Memuat detail skill…</LoadingState>}
          {skill && !detail.loading && detail.error && <div className="catalog-description">{errorBlock(detail.error)}</div>}
          {skill && validDetail && <div className="catalog-description">
            <h3>{skill.title}</h3><p>{skill.description || 'Belum ada deskripsi skill.'}</p>
            <p className="hint"><DifficultyTag level={skill.difficulty} /> · Estimasi belajar {formatMinutes(skill.estimated_learning_minutes)} (bukan skor kemampuan).</p>
            <h4>Prasyarat skill</h4>
            {detail.data.prerequisites.length ? <ul>{detail.data.prerequisites.map((item) => <li key={item.id}>{item.required_skill_title}</li>)}</ul> : <p>Tidak ada prasyarat skill pada katalog.</p>}
            <p className="hint">{detail.data.lesson_count} materi tersedia. Materi bukan kriteria penerbitan credential.</p>
          </div>}
        </section>}
      </div>

      <aside className="catalog-detail profile-card target-summary" aria-labelledby="target-title">
        <p className="eyebrow">PILIHANMU</p><h2 id="target-title">Cakupan target</h2>
        <fieldset disabled={pending || Boolean(error || invalid) || !track}><legend>Yang ingin saya capai</legend>
          {['career_track', 'competency', 'skill'].map((kind) => <label className="target-option" key={kind}>
            <input type="radio" name="target" checked={selection.target === kind} disabled={kind === 'competency' ? !competency : kind === 'skill' ? !skill : !track} onChange={() => change('target', kind)} />{names[kind]}</label>)}
        </fieldset>
        <div className="target-result" role="status" aria-live="polite">
          {pending ? <LoadingState>Memuat pilihan…</LoadingState> : error || invalid ? <p>Target belum bisa digunakan. Perbaiki pilihan atau muat ulang katalog.</p> : target ? <>
            <span className="catalog-detail-icon" aria-hidden="true"><Icon name={targetIcons[target.kind]} size={28} /></span>
            <span className="eyebrow">{names[target.kind]}</span><h3>{target.title}</h3>
            {target.kind === 'skill' && <DifficultyTag level={target.difficulty} />}
            <p className="hint">Slug: {target.slug}</p><p>Career track: {target.track.title}</p>
          </> : <p>Pilih career track untuk menentukan target.</p>}
        </div>
        <button className="button primary full" disabled={!target || pending || Boolean(error || invalid)} onClick={copy}>Salin tautan target <Icon name="arrow" size={18} /></button>
        {copied?.href === href && <p className="hint" role="status">{copied.message}</p>}
        <p className="session-note">Pilihan tersimpan pada URL, bukan di profil server. Tautan dapat dibuka kembali; login tetap diperlukan.</p>
        {target && !pending && !error && !invalid && <Link className="button primary full" href={href.replace('/catalog', '/diagnostic')}>Ukur titik awal <Icon name="arrow" size={18} /></Link>}
        {target && !pending && !error && !invalid && <Link className="button secondary full" href={href.replace('/catalog', '/roadmap')}>Lihat roadmap target</Link>}
        {target && skill && !pending && !error && !invalid && <Link className="button secondary full" href={studyHref(href.split('?')[1] || '', skill.id)}>Buka materi skill pilihan</Link>}
        <p className="hint">Diagnostic mencakup seluruh career track. Roadmap mengikuti cakupan target dan mastery tersimpan; diagnostic belum wajib.</p>
      </aside>
    </div>
  </section></WorkspaceLayout>;
}
