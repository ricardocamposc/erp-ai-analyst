import { currentLocale, t } from './i18n.js';

export const escapeHtml = (value) => String(value ?? '').replace(/[&<>'\"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '\"': '&quot;' })[char]);

export function flattenStructuredData(structuredData = []) {
  return structuredData.flatMap((entry) => {
    const data = entry?.data;
    if (!Array.isArray(data)) return [];
    return data.filter((row) => row && typeof row === 'object' && !Array.isArray(row)).map((row) => ({ ...row, __tool_name: entry.tool_name }));
  });
}

export function tableMarkup(structuredData = []) {
  const rows = flattenStructuredData(structuredData);
  if (!rows.length) return `<p class="muted">${escapeHtml(t('noTabularRows'))}</p>`;
  const keys = [...new Set(rows.flatMap((row) => Object.keys(row).filter((key) => key !== '__tool_name')))];
  const header = keys.map((key) => `<th>${escapeHtml(key.replaceAll('_', ' '))}</th>`).join('');
  const body = rows.slice(0, 40).map((row) => `<tr>${keys.map((key) => `<td>${escapeHtml(typeof row[key] === 'object' ? JSON.stringify(row[key]) : row[key])}</td>`).join('')}</tr>`).join('');
  return `<div class="table-wrap"><table class="data-table"><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function formatResultValue(value) {
  if (value == null) return '—';
  if (typeof value === 'object') return JSON.stringify(value);
  const text = String(value);
  const dateMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})(?:T|$)/);
  if (dateMatch) {
    const date = new Date(`${dateMatch[1]}-${dateMatch[2]}-${dateMatch[3]}T00:00:00Z`);
    if (!Number.isNaN(date.valueOf())) {
      return new Intl.DateTimeFormat(currentLocale() === 'pt' ? 'pt-BR' : currentLocale(), { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(date);
    }
  }
  return text;
}

export function resultTableMarkup(result) {
  if (!result?.columns?.length || !result?.rows?.length) return '';
  const columns = result.columns;
  const header = columns.map((column) => `<th>${escapeHtml(String(column).replaceAll('_', ' '))}</th>`).join('');
  const body = result.rows.slice(0, 500).map((row) => `<tr>${columns.map((column) => `<td>${escapeHtml(formatResultValue(row[column]))}</td>`).join('')}</tr>`).join('');
  return `<div class="table-wrap"><table class="data-table result-set-table"><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function chartRows(structuredData = []) {
  const rows = flattenStructuredData(structuredData);
  if (!rows.length) return null;
  const labelKey = ['product_key', 'customer_key', 'supplier_key', 'cost_center_key', 'concept', 'account_group', 'period'].find((key) => rows.some((row) => row[key] != null));
  const valueKey = ['total', 'amount', 'value', 'absolute_change', 'outstanding_quantity', 'cost'].find((key) => rows.some((row) => Number.isFinite(Number(row[key]))));
  if (!labelKey || !valueKey) return null;
  return rows.slice(0, 8).map((row) => ({ label: String(row[labelKey]), value: Number(row[valueKey]) })).filter((row) => Number.isFinite(row.value));
}

export function chartMarkup(structuredData = []) {
  const rows = chartRows(structuredData);
  if (!rows?.length) return '';
  const max = Math.max(...rows.map((row) => Math.abs(row.value)), 1);
  const width = 760; const baseline = 145; const barWidth = Math.max(28, Math.floor((width - 40) / rows.length) - 14);
  const bars = rows.map((row, index) => { const height = Math.max(4, Math.round(Math.abs(row.value) / max * 105)); const x = 25 + index * ((width - 30) / rows.length); const y = row.value < 0 ? baseline : baseline - height; return `<rect class="bar" x="${x}" y="${y}" width="${barWidth}" height="${height}" rx="5"><title>${escapeHtml(row.label)}: ${row.value}</title></rect><text x="${x + barWidth / 2}" y="164" text-anchor="middle">${escapeHtml(row.label.slice(0, 13))}</text>`; }).join('');
  return `<div class="chart-wrap"><svg class="chart" viewBox="0 0 ${width} 180" role="img" aria-label="${escapeHtml(t('visualComparison'))}"><line class="axis" x1="20" x2="${width - 10}" y1="${baseline}" y2="${baseline}" />${bars}</svg></div>`;
}

export function statusLabel(status) { return ({ completed: t('completed'), insufficient_data: t('insufficientEvidence'), unsupported: t('outOfScope'), failed: t('failed') })[status] || status; }
