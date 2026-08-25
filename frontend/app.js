import { chartMarkup, escapeHtml, resultTableMarkup, statusLabel, tableMarkup } from './render.js';
import { addMessage, createChatState, replaceMessage, resetChat } from './chat-state.js';

const form = document.querySelector('#analysis-form');
const question = document.querySelector('#question');
const button = document.querySelector('#submit');
const messages = document.querySelector('#messages');
const count = document.querySelector('#question-count');
const sessionLabel = document.querySelector('#session-label');
let chat = createChatState();
let requestInFlight = false;

function listMarkup(items, empty = 'Sin información adicional.') {
  return items?.length ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : `<p class="muted">${empty}</p>`;
}

function provenanceMarkup(evidence = []) {
  if (!evidence.length) return '<p class="muted">No se generó evidencia para esta solicitud.</p>';
  return `<div class="provenance">${evidence.map((item) => `<article class="provenance-card"><strong>${escapeHtml(item.tool_name || 'herramienta')}</strong><span>${escapeHtml(item.metric || 'resultado')} · ${escapeHtml(item.period_start || '')} → ${escapeHtml(item.period_end || '')}</span><br><span>Query: ${escapeHtml(item.query_id || 'no disponible')}</span></article>`).join('')}</div>`;
}

function dynamicTraceMarkup(data) {
  const query = data.query;
  const validation = data.validation;
  const result = data.result;
  if (!query && !validation && !result) return '';
  const sql = validation?.normalized_sql || query?.sql;
  const validationReasons = validation?.reasons?.join(' · ') || 'Guardrails aplicados';
  const validationApproved = validation?.status === 'approved';
  const validationLabel = validationApproved ? 'Aprobada' : 'Rechazada o requiere revisión';
  const validationClass = validationApproved ? 'status-badge' : 'status-badge error';
  return `<div class="assistant-section"><h3>Trazabilidad de la consulta dinámica</h3>${sql ? `<details><summary>SQL generado y validado</summary><pre class="sql-preview">${escapeHtml(sql)}</pre></details>` : ''}${validation ? `<p><span class="${validationClass}">${validationLabel}</span> · ${escapeHtml(validationReasons)}</p>` : ''}${result ? `<p class="muted">Filas devueltas: ${escapeHtml(String(result.row_count ?? 0))} · Hash SQL: ${escapeHtml(result.sql_hash || 'no disponible')}</p>` : ''}</div>`;
}

function technicalDetailsMarkup(data, performed, evidence, findings, structuredData) {
  const trace = dynamicTraceMarkup(data);
  if (!performed.length && !evidence.length && !trace && !findings.length && !structuredData.length) return '';
  const findingsMarkup = findings.length ? `<div class="assistant-section"><h3>Hallazgos clave</h3><ul class="findings">${findings.map((item) => `<li class="finding">${escapeHtml(item)}</li>`).join('')}</ul></div>` : '';
  const performedMarkup = performed.length ? `<div class="assistant-section"><h3>Análisis ejecutado</h3><div class="analysis-flow">${performed.map((tool, index) => `${index ? '<span class="flow-arrow">→</span>' : ''}<span class="tool-pill">${escapeHtml(tool)}</span>`).join('')}</div></div>` : '';
  const evidenceMarkup = evidence.length ? `<div class="assistant-section"><h3>Evidencia y procedencia</h3>${provenanceMarkup(evidence)}</div>` : '';
  const structuredMarkup = structuredData.length ? `<div class="assistant-section"><h3>Datos estructurados</h3>${chartMarkup(structuredData)}${tableMarkup(structuredData)}</div>` : '';
  return `<details class="technical-details"><summary>Ver trazabilidad y evidencia técnica</summary>${findingsMarkup}${performedMarkup}${evidenceMarkup}${structuredMarkup}${trace}</details>`;
}

function assistantMarkup(data) {
  const statusClass = data.status === 'completed' ? '' : data.status === 'failed' ? 'error' : 'warning';
  const findings = data.key_findings || [];
  const performed = data.analysis_performed || [];
  const structuredData = data.structured_data || [];
  const limitation = data.status !== 'completed' ? `<div class="assistant-section warning-box"><h3>Limitación</h3>${listMarkup(data.warnings, 'La solicitud no produjo evidencia suficiente.')}</div>` : '';
  const warnings = data.status === 'completed' && data.warnings?.length ? `<div class="assistant-section warning-box"><h3>Advertencias y límites</h3>${listMarkup(data.warnings)}</div>` : '';
  const technicalDetails = technicalDetailsMarkup(data, performed, data.evidence || [], findings, structuredData);
  const resultSet = data.result?.rows?.length ? `<div class="assistant-section"><h3>Resultado de la consulta</h3>${resultTableMarkup(data.result)}</div>` : '';
  return `<div class="message-label">Analista ERP · <span class="status-badge ${statusClass}">${escapeHtml(statusLabel(data.status))}</span></div><div class="assistant-answer">${escapeHtml(data.answer || 'No hay respuesta disponible.')}</div><div class="assistant-sections">${limitation}${resultSet}${technicalDetails}${warnings}</div>`;
}

function messageMarkup(message) {
  if (message.role === 'user') return `<article class="message user" data-message-id="${escapeHtml(message.id)}"><div class="message-bubble"><span class="message-label">Tú</span><div class="message-question">${escapeHtml(message.question)}</div></div></article>`;
  if (message.pending) return `<article class="message assistant" data-message-id="${escapeHtml(message.id)}"><div class="message-bubble pending-bubble"><span class="message-label">Analista ERP</span>Analizando<span class="pending-dots"><i></i><i></i><i></i></span></div></article>`;
  const retry = message.retryQuestion ? `<button class="retry-button" type="button" data-retry-question="${escapeHtml(message.retryQuestion)}">Reintentar</button>` : '';
  return `<article class="message assistant" data-message-id="${escapeHtml(message.id)}"><div class="message-bubble">${assistantMarkup(message.data)}${retry}</div></article>`;
}

function renderTranscript() {
  sessionLabel.textContent = `Sesión ${chat.conversationId.slice(0, 8)}`;
  messages.innerHTML = chat.messages.length ? chat.messages.map(messageMarkup).join('') : '<div class="empty-state"><span class="empty-icon">✦</span><h2>¿Qué quieres investigar?</h2><p>Haz una pregunta y recibirás una respuesta con evidencia del ERP sintético.</p></div>';
  messages.scrollTop = messages.scrollHeight;
}

function renderError(message) {
  return { answer: message, key_findings: [], evidence: [], analysis_performed: [], structured_data: [], warnings: ['Revisa que la API esté disponible e inténtalo de nuevo.'], status: 'failed' };
}

async function sendQuestion(rawQuestion, retryMessageId = null) {
  const value = rawQuestion.trim();
  if (!value || requestInFlight) { if (!value) question.focus(); return; }
  requestInFlight = true; button.disabled = true;
  if (retryMessageId) replaceMessage(chat, retryMessageId, { role: 'assistant', pending: true });
  else { addMessage(chat, { role: 'user', question: value }); addMessage(chat, { role: 'assistant', pending: true }); }
  const pendingId = retryMessageId || chat.messages[chat.messages.length - 1].id;
  renderTranscript();
  try {
    const response = await fetch('/api/v1/dynamic-analysis', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: value, conversation_id: chat.conversationId }) });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) { const detail = Array.isArray(payload.detail) ? payload.detail.map((item) => item.msg).join(', ') : payload.detail; throw new Error(detail || 'El servicio de análisis no está disponible.'); }
    replaceMessage(chat, pendingId, { role: 'assistant', data: payload });
  } catch (error) { replaceMessage(chat, pendingId, { role: 'assistant', data: renderError(error instanceof Error ? error.message : 'Error desconocido.'), retryQuestion: value }); }
  finally { requestInFlight = false; button.disabled = false; question.value = ''; question.dispatchEvent(new Event('input')); renderTranscript(); question.focus(); }
}

function resetConversation() { chat = resetChat(); question.value = ''; question.dispatchEvent(new Event('input')); renderTranscript(); question.focus(); }

question.addEventListener('input', () => { count.textContent = `${question.value.length} / 2000`; question.style.height = 'auto'; question.style.height = `${Math.min(question.scrollHeight, 150)}px`; });
question.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); } });
form.addEventListener('submit', (event) => { event.preventDefault(); sendQuestion(question.value); });
document.querySelector('#new-conversation').addEventListener('click', resetConversation);
document.querySelectorAll('[data-question]').forEach((chip) => chip.addEventListener('click', () => { question.value = chip.dataset.question; question.dispatchEvent(new Event('input')); sendQuestion(question.value); }));
messages.addEventListener('click', (event) => { const retry = event.target.closest('[data-retry-question]'); if (retry) sendQuestion(retry.dataset.retryQuestion, retry.closest('[data-message-id]').dataset.messageId); });
renderTranscript();
