const $ = (id) => document.getElementById(id);
const percent = (value, digits = 1) => `${(value * 100).toFixed(digits)}%`;
const signed = (value) => `${value > 0 ? '+' : '-'}${Math.abs(value).toFixed(2)}`;
const METER_LIMIT = 3; // margin scores beyond this fill the meter

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function showError(id, message) {
  $(id).textContent = message;
  $(id).hidden = !message;
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      headers: { 'Content-Type': 'application/json' }, ...options,
    });
  } catch {
    setStatus(false);
    throw new Error('The server is not responding. Check that the app is still running, then try again.');
  }
  if (!response.ok) {
    if (response.status === 422) throw new Error('Check your input: each headline must be 1 to 2,000 characters.');
    throw new Error(`The server could not complete this request (error ${response.status}).`);
  }
  return response.json();
}

function setStatus(ok) {
  $('status').className = `status ${ok ? 'ok' : 'down'}`;
  $('status').querySelector('span').textContent = ok ? 'Model ready' : 'Server offline';
}

function tag(label) {
  if (!label) return el('span', 'tag', 'No result');
  return el('span', `tag ${label}`, label === 'fake' ? 'Likely fake' : 'Likely real');
}

function row(cells) {
  const tr = el('tr');
  cells.forEach((cell) => tr.append(cell));
  return tr;
}

function td(content, className) {
  const cell = el('td', className);
  cell.append(content);
  return cell;
}

/* Tabs */
const TABS = ['check', 'batch', 'history', 'model'];
function openTab(name) {
  TABS.forEach((tab) => {
    $(`tab-${tab}`).setAttribute('aria-selected', String(tab === name));
    $(`view-${tab}`).hidden = tab !== name;
  });
  if (name === 'history') loadHistory();
  if (name === 'model') loadModel();
}
TABS.forEach((tab) => $(`tab-${tab}`).addEventListener('click', () => openTab(tab)));

/* Single check */
let currentSample = null;

function renderResult(result) {
  $('result-empty').hidden = true;
  $('result-body').hidden = false;
  const known = Boolean(result.label);
  $('meter-block').hidden = !known;
  $('terms-block').hidden = !known;
  $('giveaway').hidden = !(known && result.has_giveaway_words);

  if (!known) {
    $('verdict').className = 'verdict';
    $('verdict').textContent = 'NO RESULT';
    $('prob-text').className = 'prob-text plain';
    $('prob-text').textContent = 'The model knows none of these words. Try an English headline with more detail.';
    $('truth').hidden = true;
    return;
  }

  $('verdict').className = `verdict ${result.label}`;
  $('verdict').textContent = result.label === 'fake' ? 'LIKELY FAKE' : 'LIKELY REAL';
  $('prob-text').className = 'prob-text';
  $('prob-text').textContent = signed(result.margin);
  $('prob-text').append(el('small', '', 'margin score: distance from the decision boundary, not a probability'));
  $('meter').className = `meter ${result.label}`;
  const reach = (Math.min(Math.abs(result.margin), METER_LIMIT) / METER_LIMIT) * 50;
  $('meter-fill').style.width = `${reach}%`;
  $('meter-fill').style.left = result.margin > 0 ? '50%' : `${50 - reach}%`;

  const largest = Math.max(...result.terms.map((t) => Math.abs(t.effect)), 0.001);
  $('terms').replaceChildren(...result.terms.map((t) => {
    const direction = t.effect > 0 ? 'fake' : 'real';
    const li = el('li');
    const bar = el('div', 'bar');
    const fill = el('i', direction);
    fill.style.width = `${(Math.abs(t.effect) / largest) * 50}%`;
    bar.append(fill, el('b'));
    li.append(el('span', '', t.term), bar,
      el('div', 'effect', signed(t.effect)));
    return li;
  }));

  const isSample = currentSample && currentSample.headline === result.headline;
  $('truth').hidden = !isSample;
  if (isSample) {
    const right = currentSample.label === result.label;
    $('truth').textContent = `Dataset label: ${currentSample.label === 'fake' ? 'Fake' : 'Real'}. The model got this one ${right ? 'right' : 'wrong'}.`;
  }
}

async function checkHeadline() {
  const headline = $('headline').value.trim();
  showError('check-error', '');
  if (!headline) {
    showError('check-error', 'Enter a headline to check.');
    $('headline').focus();
    return;
  }
  $('check-btn').disabled = true;
  try {
    renderResult(await api('/api/predict', { method: 'POST', body: JSON.stringify({ headline }) }));
  } catch (error) {
    showError('check-error', error.message);
  } finally {
    $('check-btn').disabled = false;
  }
}

$('check-form').addEventListener('submit', (event) => {
  event.preventDefault();
  checkHeadline();
});
$('headline').addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    checkHeadline();
  }
});
$('sample-btn').addEventListener('click', async () => {
  showError('check-error', '');
  try {
    currentSample = await api('/api/samples/random');
    $('headline').value = currentSample.headline;
    await checkHeadline();
  } catch (error) {
    showError('check-error', error.message);
  }
});
$('clear-btn').addEventListener('click', () => {
  currentSample = null;
  $('headline').value = '';
  showError('check-error', '');
  $('result-empty').hidden = false;
  $('result-body').hidden = true;
  $('headline').focus();
});

/* Batch */
let batchResults = [];

$('batch-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  showError('batch-error', '');
  const headlines = $('batch-input').value.split('\n').map((line) => line.trim()).filter(Boolean);
  if (!headlines.length) return showError('batch-error', 'Enter at least one headline.');
  if (headlines.length > 200) return showError('batch-error', `You entered ${headlines.length} headlines. The limit is 200.`);
  $('batch-btn').disabled = true;
  try {
    const data = await api('/api/predict/batch', { method: 'POST', body: JSON.stringify({ headlines }) });
    batchResults = data.results;
    const { total, fake, real, no_result: none } = data.summary;
    $('batch-summary').replaceChildren(...[[total, 'checked'], [fake, 'likely fake'], [real, 'likely real'], [none, 'no result']]
      .map(([count, label]) => {
        const item = el('span');
        item.append(el('strong', '', String(count)), label);
        return item;
      }));
    $('batch-rows').replaceChildren(...batchResults.map((r) => row([
      td(r.headline, 'headline-cell'), td(tag(r.label)),
      td(r.margin === null ? '-' : signed(r.margin), 'num'),
    ])));
    $('batch-results').hidden = false;
    $('batch-download').disabled = false;
  } catch (error) {
    showError('batch-error', error.message);
  } finally {
    $('batch-btn').disabled = false;
  }
});

function csvCell(value) {
  let text = String(value ?? '');
  if (/^[=+\-@]/.test(text)) text = `'${text}`; // stops spreadsheets running it as a formula
  return `"${text.replace(/"/g, '""')}"`;
}

$('batch-download').addEventListener('click', () => {
  const lines = [['headline', 'result', 'margin_score'],
    ...batchResults.map((r) => [r.headline, r.label ?? 'no result', r.margin ?? ''])];
  const blob = new Blob([`﻿${lines.map((line) => line.map(csvCell).join(',')).join('\r\n')}`], { type: 'text/csv' });
  const link = el('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'headline_results.csv';
  link.click();
  URL.revokeObjectURL(link.href);
});

/* History */
async function loadHistory() {
  showError('history-error', '');
  try {
    const { checks } = await api('/api/history?limit=200');
    $('history-empty').hidden = checks.length > 0;
    $('history-table').hidden = checks.length === 0;
    $('history-clear').disabled = checks.length === 0;
    $('history-rows').replaceChildren(...checks.map((c) => row([
      td(new Date(c.created_at).toLocaleString(), 'time'), td(c.headline, 'headline-cell'),
      td(tag(c.label)), td(signed(c.margin), 'num'),
    ])));
  } catch (error) {
    showError('history-error', error.message);
  }
}

$('history-clear').addEventListener('click', () => { $('history-confirm').hidden = false; });
$('history-confirm-no').addEventListener('click', () => { $('history-confirm').hidden = true; });
$('history-confirm-yes').addEventListener('click', async () => {
  $('history-confirm').hidden = true;
  try {
    await api('/api/history', { method: 'DELETE' });
    await loadHistory();
  } catch (error) {
    showError('history-error', error.message);
  }
});

/* Model report */
let modelLoaded = false;

async function loadModel() {
  if (modelLoaded) return;
  showError('model-error', '');
  try {
    const report = await api('/api/model');
    const m = report.test_metrics;
    $('metric-tiles').replaceChildren(...[['Accuracy', m.accuracy], ['Precision', m.precision], ['Recall', m.recall], ['F1-score', m.f1]]
      .map(([name, value]) => {
        const tile = el('div', 'tile');
        tile.append(el('span', '', name), el('strong', '', percent(value)));
        return tile;
      }));
    const cm = report.confusion_matrix;
    const count = (n) => n.toLocaleString();
    $('matrix-rows').replaceChildren(
      row([td('Real'), td(count(cm.real_as_real), 'num'), td(count(cm.real_as_fake), 'num')]),
      row([td('Fake'), td(count(cm.fake_as_real), 'num'), td(count(cm.fake_as_fake), 'num')]),
    );
    const p = report.best_params;
    const details = [
      ['Algorithm', report.algorithm],
      ['Word features', 'Single words and word pairs'],
      ['Vocabulary', `${count(report.vocabulary_size)} terms`],
      ['Regularization (C)', String(p.clf__C)],
      ['Minimum word count', String(p.tfidf__min_df)],
      ['Sublinear TF', p.tfidf__sublinear_tf ? 'Yes' : 'No'],
      ['Class weight', p.clf__class_weight ?? 'None'],
      ['Cross-validation F1', percent(report.cv_f1)],
    ];
    $('details').replaceChildren(...details.flatMap(([name, value]) => [el('dt', '', name), el('dd', '', value)]));
    $('robust-rows').replaceChildren(...report.robustness.map((r) => row([
      td(r.subset), td(count(r.rows), 'num'), td(percent(r.accuracy), 'num'),
      td(percent(r.precision), 'num'), td(percent(r.recall), 'num'), td(percent(r.f1), 'num'),
    ])));
    $('top-fake').replaceChildren(...report.top_fake_terms.map((t) => el('span', '', t)));
    $('top-real').replaceChildren(...report.top_real_terms.map((t) => el('span', '', t)));
    modelLoaded = true;
  } catch (error) {
    showError('model-error', error.message);
  }
}

api('/api/health').then(() => setStatus(true)).catch(() => setStatus(false));
