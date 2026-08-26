const translations = {
  en: {
    language: 'Language',
    eyebrow: 'ERP · ANALYTICS · EVIDENCE',
    title: 'Ask your ERP.',
    newConversation: 'New conversation',
    lead: 'Explore sales, inventory, purchasing, payroll, and accounting with traceable answers.',
    analyst: 'ERP Analyst',
    you: 'You',
    session: 'Analysis session',
    sessionLabel: 'Session',
    emptyTitle: 'What would you like to investigate?',
    emptyDescription: 'Ask a question and receive an answer with evidence from the synthetic ERP.',
    starterLabel: 'Try:',
    sales: 'Sales',
    supplyChain: 'Supply chain',
    payrollAccounting: 'Payroll / accounting',
    outOfScope: 'Out of scope',
    questionLabel: 'Business question',
    placeholder: 'Type a business question…',
    send: 'Send',
    analyzing: 'Analyzing',
    retry: 'Retry',
    noAdditionalInformation: 'No additional information.',
    tool: 'tool', result: 'result', query: 'Query', noAnswer: 'No answer available.',
    noEvidence: 'No evidence was generated for this request.',
    guardrailsApplied: 'Guardrails applied',
    approved: 'Approved',
    rejectedReview: 'Rejected or requires review',
    dynamicTraceability: 'Dynamic query traceability',
    generatedSql: 'Generated and validated SQL',
    rowsReturned: 'Rows returned',
    sqlHash: 'SQL hash',
    notAvailable: 'not available',
    keyFindings: 'Key findings',
    analysisPerformed: 'Analysis performed',
    evidenceProvenance: 'Evidence and provenance',
    structuredData: 'Structured data',
    technicalTraceability: 'View technical traceability and evidence',
    limitation: 'Limitation',
    warningsLimits: 'Warnings and limits',
    insufficientFallback: 'The request did not produce sufficient evidence.',
    queryResult: 'Query result',
    noTabularRows: 'No tabular rows are available for this analysis.',
    visualComparison: 'Visual comparison of structured data',
    completed: 'Completed',
    insufficientEvidence: 'Insufficient evidence',
    failed: 'Failed',
    unknownError: 'Unknown error.',
    serviceUnavailable: 'The analysis service is unavailable.',
    apiHint: 'Check that the API is available and try again.'
  },
  es: {
    language: 'Idioma', eyebrow: 'ERP · ANÁLISIS · EVIDENCIA', title: 'Pregunta a tu ERP.', newConversation: 'Nueva conversación',
    lead: 'Explora ventas, inventario, compras, nómina y contabilidad con respuestas trazables.', analyst: 'Analista ERP', you: 'Tú', session: 'Sesión de análisis', sessionLabel: 'Sesión',
    emptyTitle: '¿Qué te gustaría investigar?', emptyDescription: 'Haz una pregunta y recibe una respuesta con evidencia del ERP sintético.', starterLabel: 'Prueba:', sales: 'Ventas', supplyChain: 'Cadena de suministro', payrollAccounting: 'Nómina / contabilidad', outOfScope: 'Fuera de alcance', questionLabel: 'Pregunta de negocio', placeholder: 'Escribe una pregunta de negocio…', send: 'Enviar', analyzing: 'Analizando', retry: 'Reintentar', noAdditionalInformation: 'No hay información adicional.', noEvidence: 'No se generó evidencia para esta solicitud.', guardrailsApplied: 'Controles de seguridad aplicados', approved: 'Aprobada', rejectedReview: 'Rechazada o requiere revisión', dynamicTraceability: 'Trazabilidad de la consulta dinámica', generatedSql: 'SQL generado y validado', rowsReturned: 'Filas devueltas', sqlHash: 'Hash del SQL', notAvailable: 'no disponible', keyFindings: 'Hallazgos clave', analysisPerformed: 'Análisis realizado', evidenceProvenance: 'Evidencia y procedencia', structuredData: 'Datos estructurados', technicalTraceability: 'Ver trazabilidad técnica y evidencia', limitation: 'Limitación', warningsLimits: 'Advertencias y límites', insufficientFallback: 'La solicitud no produjo evidencia suficiente.', queryResult: 'Resultado de la consulta', noTabularRows: 'No hay filas tabulares disponibles para este análisis.', visualComparison: 'Comparación visual de datos estructurados', completed: 'Completado', insufficientEvidence: 'Evidencia insuficiente', failed: 'Fallido', unknownError: 'Error desconocido.', serviceUnavailable: 'El servicio de análisis no está disponible.', apiHint: 'Verifica que la API esté disponible e inténtalo de nuevo.'
  },
  pt: {
    language: 'Idioma', eyebrow: 'ERP · ANÁLISE · EVIDÊNCIAS', title: 'Pergunte ao seu ERP.', newConversation: 'Nova conversa',
    lead: 'Explore vendas, estoque, compras, folha de pagamento e contabilidade com respostas rastreáveis.', analyst: 'Analista de ERP', you: 'Você', session: 'Sessão de análise', sessionLabel: 'Sessão',
    emptyTitle: 'O que você gostaria de investigar?', emptyDescription: 'Faça uma pergunta e receba uma resposta com evidências do ERP sintético.', starterLabel: 'Experimente:', sales: 'Vendas', supplyChain: 'Cadeia de suprimentos', payrollAccounting: 'Folha / contabilidade', outOfScope: 'Fora do escopo', questionLabel: 'Pergunta de negócio', placeholder: 'Digite uma pergunta de negócio…', send: 'Enviar', analyzing: 'Analisando', retry: 'Tentar novamente', noAdditionalInformation: 'Não há informações adicionais.', noEvidence: 'Nenhuma evidência foi gerada para esta solicitação.', guardrailsApplied: 'Controles de segurança aplicados', approved: 'Aprovada', rejectedReview: 'Rejeitada ou requer revisão', dynamicTraceability: 'Rastreabilidade da consulta dinâmica', generatedSql: 'SQL gerado e validado', rowsReturned: 'Linhas retornadas', sqlHash: 'Hash do SQL', notAvailable: 'indisponível', keyFindings: 'Principais descobertas', analysisPerformed: 'Análise realizada', evidenceProvenance: 'Evidências e procedência', structuredData: 'Dados estruturados', technicalTraceability: 'Ver rastreabilidade técnica e evidências', limitation: 'Limitação', warningsLimits: 'Avisos e limites', insufficientFallback: 'A solicitação não produziu evidências suficientes.', queryResult: 'Resultado da consulta', noTabularRows: 'Não há linhas tabulares disponíveis para esta análise.', visualComparison: 'Comparação visual de dados estruturados', completed: 'Concluído', insufficientEvidence: 'Evidências insuficientes', failed: 'Falhou', unknownError: 'Erro desconhecido.', serviceUnavailable: 'O serviço de análise está indisponível.', apiHint: 'Verifique se a API está disponível e tente novamente.'
  }
};

const storage = typeof globalThis.localStorage?.getItem === 'function' ? globalThis.localStorage : null;
let locale = storage?.getItem('erp-ai-locale') || 'en';
if (!translations[locale]) locale = 'en';

export function currentLocale() { return locale; }
export function t(key) { return translations[locale][key] || translations.en[key] || key; }
export function setLocale(nextLocale) {
  if (!translations[nextLocale]) return locale;
  locale = nextLocale;
  storage?.setItem('erp-ai-locale', locale);
  return locale;
}

export function applyTranslations(root = document) {
  root.querySelectorAll('[data-i18n]').forEach((element) => { element.textContent = t(element.dataset.i18n); });
  root.querySelectorAll('[data-i18n-attr]').forEach((element) => {
    const [attribute, key] = element.dataset.i18nAttr.split(':');
    element.setAttribute(attribute, t(key));
  });
  document.documentElement.lang = locale === 'pt' ? 'pt-BR' : locale;
}
