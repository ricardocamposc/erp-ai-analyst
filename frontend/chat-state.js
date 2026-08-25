function randomId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `chat-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function createChatState(conversationId = randomId()) {
  return { conversationId, messages: [] };
}

export function addMessage(state, message) {
  const next = { id: randomId(), ...message };
  state.messages.push(next);
  return next.id;
}

export function replaceMessage(state, messageId, message) {
  const index = state.messages.findIndex((item) => item.id === messageId);
  if (index === -1) return false;
  state.messages[index] = { id: messageId, ...message };
  return true;
}

export function resetChat() { return createChatState(); }
