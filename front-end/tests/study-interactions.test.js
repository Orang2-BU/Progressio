import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import React, { act, createElement, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { JSDOM } from 'jsdom';
import { foundationRenderer } from './support/render-foundation.js';

const { StudyInteractionBoundary } = foundationRenderer().load('StudyInteractions.jsx');

const receipt = (lessonId, newlyCompleted = true) => ({
  status: 'completed', lesson_id: lessonId, xp_earned: newlyCompleted ? 20 : 0,
  newly_completed: newlyCompleted, current_skill_mastery: 70, current_skill_xp: 50,
});

const lessons = [
  { id: 7, title: 'REST API Design' },
  { id: 8, title: 'Relational Data Modelling' },
];

const steps = [
  { id: 9, lesson: 7, prompt: 'Periksa endpoint REST.', estimated_minutes: 5, checkpoint_question: 'Apa status sukses create?' },
  { id: 10, lesson: 8, prompt: 'Periksa relasi data.', estimated_minutes: 7, checkpoint_question: 'Apa kunci baris?' },
];

const environments = [];
afterEach(async () => {
  for (const environment of environments.splice(0)) await environment.close();
});

function createPicker({ onComplete, onSubmitCheckpoint, completed = false, disabled = false, linkBroken = false }) {
  const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: 'http://localhost/' });
  const previous = new Map();
  for (const key of ['window', 'document', 'HTMLElement', 'HTMLInputElement', 'Event', 'MouseEvent', 'navigator']) {
    previous.set(key, Object.getOwnPropertyDescriptor(globalThis, key));
    Object.defineProperty(globalThis, key, { configurable: true, value: key === 'window' ? dom.window : key === 'document' ? dom.window.document : key === 'navigator' ? dom.window.navigator : dom.window[key] });
  }
  previous.set('IS_REACT_ACT_ENVIRONMENT', Object.getOwnPropertyDescriptor(globalThis, 'IS_REACT_ACT_ENVIRONMENT'));
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;

  const container = dom.window.document.getElementById('root');
  const root = createRoot(container);

  function Picker() {
    const [lessonId, setLessonId] = useState(7);
    const lesson = lessons.find((item) => item.id === lessonId);
    return createElement(React.Fragment, null,
      createElement('button', { type: 'button', onClick: () => setLessonId((current) => current === 7 ? 8 : 7) }, 'Ganti materi'),
      createElement(StudyInteractionBoundary, {
        key: lesson.id,
        lesson,
        steps: steps.filter((step) => step.lesson === lesson.id),
        completed,
        disabled,
        linkBroken,
        onComplete,
        onSubmitCheckpoint,
      }));
  }

  const environment = {
    container,
    root,
    async render() { await act(async () => { root.render(createElement(Picker)); }); },
    async click(name) {
      const button = [...container.querySelectorAll('button')].find((item) => item.textContent.trim() === name);
      assert.ok(button, `Expected visible button: ${name}`);
      await act(async () => { button.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true })); });
    },
    getByRole(role, name) {
      const selector = role === 'button' ? 'button' : `[role="${role}"]`;
      const matches = [...container.querySelectorAll(selector)];
      const match = matches.find((item) => name.test(item.textContent.trim()));
      assert.ok(match, `Expected ${role} named ${name}`);
      return match;
    },
    async changeInput(label, value) {
      const labelNode = [...container.querySelectorAll('label')].find((item) => item.textContent.trim() === label);
      assert.ok(labelNode, `Expected label: ${label}`);
      const input = container.querySelector(`#${labelNode.htmlFor}`);
      const setter = Object.getOwnPropertyDescriptor(dom.window.HTMLInputElement.prototype, 'value').set;
      await act(async () => {
        setter.call(input, value);
        input.dispatchEvent(new dom.window.Event('input', { bubbles: true }));
        input.dispatchEvent(new dom.window.Event('change', { bubbles: true }));
      });
      return input;
    },
    async submit(label) {
      const form = [...container.querySelectorAll('form')].find((item) => item.querySelector('h4')?.textContent === label);
      assert.ok(form, `Expected checkpoint form: ${label}`);
      await act(async () => { form.dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true })); });
    },
    text() { return container.textContent; },
    async close() {
      await act(async () => root.unmount());
      dom.window.close();
      for (const [key, descriptor] of previous) {
        if (descriptor) Object.defineProperty(globalThis, key, descriptor);
        else delete globalThis[key];
      }
    },
  };
  environments.push(environment);
  return environment;
}

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((done, fail) => { resolve = done; reject = fail; });
  return { promise, resolve, reject };
}

test('completion busy state and late receipt stay with the lesson that submitted them', async () => {
  const firstRequest = deferred();
  const onComplete = async (lessonId) => lessonId === 7 ? firstRequest.promise : receipt(lessonId, false);
  const view = createPicker({ onComplete, onSubmitCheckpoint: async () => ({ correct: true, feedback: 'Sesuai' }) });
  await view.render();

  await view.click('Tandai lesson selesai');
  assert.match(view.getByRole('button', /Mencatat di server/).textContent, /Mencatat di server/);
  assert.equal(view.getByRole('button', /Mencatat di server/).disabled, true);

  await view.click('Ganti materi');
  assert.match(view.container.textContent, /Apa kunci baris/);
  const lessonBButton = view.getByRole('button', /Tandai lesson selesai/);
  assert.equal(lessonBButton.disabled, false);
  assert.doesNotMatch(view.text(), /receipt|XP pada receipt|Mencatat di server/);

  await act(async () => { firstRequest.resolve(receipt(7)); await firstRequest.promise; });
  assert.doesNotMatch(view.text(), /Server mencatat aktivitas lesson/);

  await view.click('Tandai lesson selesai');
  assert.match(view.getByRole('status', /sudah pernah tercatat, tanpa reward baru/).textContent, /0 XP/);
});

test('checkpoint answer, pending state and feedback do not bleed across lesson changes', async () => {
  const firstRequest = deferred();
  const onSubmitCheckpoint = async (stepId) => stepId === 9 ? firstRequest.promise : ({ correct: false, feedback: 'Baris ini belum tepat.' });
  const view = createPicker({ onComplete: async (lessonId) => receipt(lessonId), onSubmitCheckpoint });
  await view.render();

  const answerA = await view.changeInput('Jawaban singkat', '201');
  assert.equal(answerA.disabled, false);
  await view.submit('Apa status sukses create?');
  assert.equal(view.container.querySelector('form').getAttribute('aria-busy'), 'true');

  await view.click('Ganti materi');
  const answerB = view.container.querySelector('input');
  assert.equal(answerB.value, '');
  assert.equal(view.container.querySelector('form').getAttribute('aria-busy'), 'false');
  await view.changeInput('Jawaban singkat', 'id');
  await view.submit('Apa kunci baris?');
  assert.match(view.getByRole('status', /Belum sesuai/).textContent, /Baris ini belum tepat/);

  await act(async () => { firstRequest.resolve({ correct: true, feedback: 'Status 201.' }); await firstRequest.promise; });
  assert.doesNotMatch(view.text(), /Status 201/);
  assert.match(view.text(), /Baris ini belum tepat/);
});

test('pending checkpoint prevents duplicate submissions and unknown completion stays disabled', async () => {
  const request = deferred();
  let submissions = 0;
  const view = createPicker({
    completed: null,
    disabled: true,
    onComplete: async () => { assert.fail('Unknown completion status must not submit'); },
    onSubmitCheckpoint: async () => { submissions += 1; return request.promise; },
  });
  await view.render();
  assert.equal(view.getByRole('button', /Tandai lesson selesai/).disabled, true);
  await view.changeInput('Jawaban singkat', '201');
  const form = view.container.querySelector('form');
  await act(async () => {
    form.dispatchEvent(new view.container.ownerDocument.defaultView.Event('submit', { bubbles: true, cancelable: true }));
    form.dispatchEvent(new view.container.ownerDocument.defaultView.Event('submit', { bubbles: true, cancelable: true }));
  });
  assert.equal(submissions, 1);
  request.resolve({ correct: true, feedback: 'Status 201.' });
  await act(async () => { await request.promise; });
});

test('completion errors are announced, cleared on lesson change, and duplicate clicks submit once', async () => {
  const request = deferred();
  let submissions = 0;
  const view = createPicker({
    onComplete: async (lessonId) => {
      submissions += 1;
      if (lessonId === 7) throw new Error('Completion A gagal.');
      return request.promise;
    },
    onSubmitCheckpoint: async () => ({ correct: true, feedback: 'Sesuai' }),
  });
  await view.render();

  await view.click('Tandai lesson selesai');
  assert.match(view.getByRole('alert', /Completion A gagal/).textContent, /Completion A gagal/);
  await view.click('Ganti materi');
  assert.doesNotMatch(view.text(), /Completion A gagal/);

  const button = view.getByRole('button', /Tandai lesson selesai/);
  await act(async () => {
    button.dispatchEvent(new view.container.ownerDocument.defaultView.MouseEvent('click', { bubbles: true }));
    button.dispatchEvent(new view.container.ownerDocument.defaultView.MouseEvent('click', { bubbles: true }));
  });
  assert.equal(submissions, 2);
  assert.equal(view.getByRole('button', /Mencatat di server/).disabled, true);
  request.resolve(receipt(8));
  await act(async () => { await request.promise; });
});

test('broken source links are not made actionable in the lesson panel', async () => {
  const view = createPicker({ onComplete: async (lessonId) => receipt(lessonId), onSubmitCheckpoint: async () => ({ correct: true, feedback: 'Sesuai' }), linkBroken: true });
  await view.render();
  assert.match(view.text(), /Tautan bagian materi tidak tersedia atau tercatat broken/);
  assert.equal([...view.container.querySelectorAll('a')].some((link) => link.textContent.includes('Buka bagian materi terkait')), false);
});

test('checkpoint validation errors stay local and can be retried for server feedback', async () => {
  let attempts = 0;
  const view = createPicker({
    onComplete: async (lessonId) => receipt(lessonId),
    onSubmitCheckpoint: async () => {
      attempts += 1;
      if (attempts === 1) throw Object.assign(new Error('Jawaban belum dapat diperiksa.'), { fields: { answer: 'Coba isi format jawaban yang diminta.' } });
      return { correct: false, feedback: 'Status sukses create adalah 201.' };
    },
  });
  await view.render();
  const input = await view.changeInput('Jawaban singkat', '200');
  await view.submit('Apa status sukses create?');
  assert.match(view.getByRole('alert', /Jawaban belum dapat diperiksa/).textContent, /Jawaban belum dapat diperiksa/);
  assert.equal(input.getAttribute('aria-invalid'), 'true');
  await view.changeInput('Jawaban singkat', '201');
  await view.submit('Apa status sukses create?');
  assert.match(view.getByRole('status', /Belum sesuai/).textContent, /Status sukses create adalah 201/);
  assert.equal(attempts, 2);
});
