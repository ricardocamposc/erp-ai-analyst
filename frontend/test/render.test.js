import assert from 'node:assert/strict';
import test from 'node:test';
import { chartMarkup, escapeHtml, statusLabel, tableMarkup } from '../render.js';
import { addMessage, createChatState, replaceMessage, resetChat } from '../chat-state.js';
import { currentLocale, setLocale, t } from '../i18n.js';

test('escapes user-visible values', () => {
  assert.equal(escapeHtml('<script>alert(1)</script>'), '&lt;script&gt;alert(1)&lt;/script&gt;');
});

test('renders structured rows as a table and chart', () => {
  const data = [{ tool_name: 'get_sales_by_product', data: [{ product_key: 'P-104', total: '125.50' }, { product_key: 'P-105', total: '80.00' }] }];
  assert.match(tableMarkup(data), /P-104/);
  assert.match(chartMarkup(data), /aria-label="Visual comparison/);
});

test('renders a useful empty table state', () => {
  assert.match(tableMarkup([{ tool_name: 'find_stockout_products', data: ['P-104'] }]), /No tabular rows are available/);
});

test('labels negative and unsupported states', () => {
  assert.equal(statusLabel('insufficient_data'), 'Insufficient evidence');
  assert.equal(statusLabel('unsupported'), 'Out of scope');
});

test('supports English by default and switches interface translations', () => {
  assert.equal(currentLocale(), 'en');
  assert.equal(t('send'), 'Send');
  setLocale('es');
  assert.equal(t('send'), 'Enviar');
  assert.equal(statusLabel('unsupported'), 'Fuera de alcance');
  setLocale('pt');
  assert.equal(t('send'), 'Enviar');
  assert.equal(statusLabel('completed'), 'Concluído');
  setLocale('en');
});

test('keeps multiple chat turns in order and preserves the session id', () => {
  const state = createChatState('session-1');
  const userId = addMessage(state, { role: 'user', question: 'What happened to sales?' });
  const assistantId = addMessage(state, { role: 'assistant', pending: true });

  assert.equal(state.conversationId, 'session-1');
  assert.deepEqual(state.messages.map((message) => message.role), ['user', 'assistant']);
  assert.equal(replaceMessage(state, assistantId, { role: 'assistant', data: { status: 'completed' } }), true);
  assert.equal(state.messages[0].id, userId);
});

test('reset starts a new empty session', () => {
  const state = resetChat();
  assert.ok(state.conversationId);
  assert.deepEqual(state.messages, []);
});
