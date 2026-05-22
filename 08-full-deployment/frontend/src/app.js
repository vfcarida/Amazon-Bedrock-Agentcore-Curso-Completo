/**
 * app.js -- Main application logic for Aria.
 *
 * Responsibilities:
 *   - Bootstrap authentication flow
 *   - Manage chat sessions (list, create, switch)
 *   - Send messages with streaming fetch
 *   - Render markdown responses with tool-use indicators
 *   - Handle UI interactions (input, sidebar, keyboard shortcuts)
 */

import {
    login,
    handleCallback,
    getIdToken,
    logout,
    getUserInfo,
    isAuthenticated,
} from './auth.js';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const config  = window.ARIA_CONFIG || {};
const API_URL = (config.API_URL || '').replace(/\/$/, '');  // REST API (chat, sessions, history)

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let currentSessionId = null;
let sessions         = [];
let isStreaming       = false;
let currentStreamBuffer = '';

// Track whether we've already created the DynamoDB record for the current session
let sessionRecordCreated = false;

// ---------------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------------

const $app            = document.getElementById('app');
const $messages       = document.getElementById('messages');
const $chatContainer  = document.getElementById('chat-container');
const $welcomeScreen  = document.getElementById('welcome-screen');
const $input          = document.getElementById('message-input');
const $sendBtn        = document.getElementById('send-btn');
const $sessionsList   = document.getElementById('sessions-list');
const $newChatBtn     = document.getElementById('new-chat-btn');
const $logoutBtn      = document.getElementById('logout-btn');
const $userName       = document.getElementById('user-name');
const $userAvatar     = document.getElementById('user-avatar');
const $authLoading    = document.getElementById('auth-loading');

// ---------------------------------------------------------------------------
// Markdown renderer configuration
// ---------------------------------------------------------------------------

if (typeof marked !== 'undefined') {
    marked.setOptions({
        breaks: true,
        gfm: true,
        highlight: function (code, lang) {
            return `<code class="language-${lang || 'text'}">${escapeHtml(code)}</code>`;
        },
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderMarkdown(text) {
    if (typeof marked !== 'undefined') {
        try {
            return marked.parse(text);
        } catch {
            return escapeHtml(text);
        }
    }
    return escapeHtml(text).replace(/\n/g, '<br>');
}

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------

async function init() {
    // Check for OAuth callback
    const params = new URLSearchParams(window.location.search);

    if (params.has('code')) {
        $authLoading.classList.add('visible');
        const success = await handleCallback();
        $authLoading.classList.remove('visible');

        if (!success) {
            console.error('[app] Authentication callback failed');
            login();
            return;
        }
    }

    // If not authenticated, redirect to login
    if (!isAuthenticated()) {
        login();
        return;
    }

    // Authenticated -- initialize the UI
    $authLoading.classList.remove('visible');
    setupUserInfo();
    setupEventListeners();
    await loadSessions();
}

function setupUserInfo() {
    const user = getUserInfo();
    if (user) {
        const name = user.email || user.name || user.sub || 'User';
        $userName.textContent = name;
        $userAvatar.textContent = name.charAt(0).toUpperCase();
    }
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------

function setupEventListeners() {
    // Send message
    $sendBtn.addEventListener('click', handleSend);

    $input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    // Auto-resize textarea
    $input.addEventListener('input', () => {
        $input.style.height = 'auto';
        $input.style.height = Math.min($input.scrollHeight, 200) + 'px';
        $sendBtn.disabled = $input.value.trim().length === 0;
    });

    // New chat
    $newChatBtn.addEventListener('click', createNewSession);

    // Logout
    $logoutBtn.addEventListener('click', logout);
}

// ---------------------------------------------------------------------------
// Sessions
// ---------------------------------------------------------------------------

async function loadSessions() {
    try {
        const token = await getIdToken();
        if (!token) { login(); return; }

        const response = await fetch(`${API_URL}/sessions`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.ok) {
            const data = await response.json();
            sessions = Array.isArray(data) ? data : (data.sessions || []);
            renderSessions();
        } else {
            console.error('[app] Failed to load sessions:', response.status);
            sessions = [];
            renderSessions();
        }
    } catch (err) {
        console.error('[app] Error loading sessions:', err);
        sessions = [];
        renderSessions();
    }
}

function renderSessions() {
    $sessionsList.innerHTML = '';

    if (sessions.length === 0) {
        $sessionsList.innerHTML = `
            <div class="sessions-empty">
                <p>No conversations yet</p>
            </div>
        `;
        return;
    }

    // Sort sessions by most recent first
    // API returns camelCase (sessionId, createdAt) from AgentCore Memory
    const sorted = [...sessions].sort((a, b) => {
        const dateA = a.updatedAt || a.updated_at || a.createdAt || a.created_at;
        const dateB = b.updatedAt || b.updated_at || b.createdAt || b.created_at;
        return new Date(dateB) - new Date(dateA);
    });

    for (const session of sorted) {
        const id = session.sessionId || session.session_id;
        const el = document.createElement('button');
        el.className = 'session-item' + (id === currentSessionId ? ' active' : '');
        el.dataset.sessionId = id;

        const title = session.title || 'New conversation';
        const date  = formatRelativeDate(session.updatedAt || session.updated_at || session.createdAt || session.created_at);

        el.innerHTML = `
            <div class="session-title">${escapeHtml(title)}</div>
            <div class="session-meta">
                <span class="session-date">${date}</span>
                <button class="session-delete" title="Delete conversation">&times;</button>
            </div>
        `;

        el.addEventListener('click', (e) => {
            if (e.target.closest('.session-delete')) return;
            switchSession(id);
        });
        el.querySelector('.session-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteSession(id);
        });
        $sessionsList.appendChild(el);
    }
}

async function switchSession(sessionId) {
    if (sessionId === currentSessionId) return;

    currentSessionId = sessionId;
    sessionRecordCreated = true;  // Existing session already has a DDB record
    renderSessions();
    $welcomeScreen.style.display = 'none';
    $messages.innerHTML = '';

    await loadHistory(sessionId);
}

async function loadHistory(sessionId) {
    try {
        const token = await getIdToken();
        if (!token) { login(); return; }

        const response = await fetch(`${API_URL}/history/${sessionId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (!response.ok) {
            console.error('[app] Failed to load history:', response.status);
            return;
        }

        const history = await response.json();

        $messages.innerHTML = '';
        for (const msg of history) {
            if (msg.role === 'user') {
                appendUserMessage(msg.content);
            } else if (msg.role === 'assistant') {
                appendAssistantMessage(msg.content, false);
            }
        }

        scrollToBottom();
    } catch (err) {
        console.error('[app] Error loading history:', err);
    }
}

function createNewSession() {
    currentSessionId = generateUUID();
    sessionRecordCreated = false;
    renderSessions();
    $messages.innerHTML = '';
    $welcomeScreen.style.display = 'flex';
    $input.focus();
}

async function deleteSession(sessionId) {
    if (!confirm('Delete this conversation? This cannot be undone.')) return;

    try {
        const token = await getIdToken();
        if (!token) { login(); return; }

        const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (!response.ok) {
            console.error('[app] Failed to delete session:', response.status);
            return;
        }

        // Remove from local sessions list
        sessions = sessions.filter(s => (s.sessionId || s.session_id) !== sessionId);

        // If we deleted the active session, reset the view
        if (sessionId === currentSessionId) {
            currentSessionId = null;
            $messages.innerHTML = '';
            $welcomeScreen.style.display = 'flex';
        }

        renderSessions();
    } catch (err) {
        console.error('[app] Error deleting session:', err);
    }
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

async function handleSend() {
    const message = $input.value.trim();
    if (!message || isStreaming) return;

    // Ensure we have a session
    if (!currentSessionId) {
        currentSessionId = generateUUID();
        sessionRecordCreated = false;
    }

    // Create the session record in DynamoDB on the first message
    if (!sessionRecordCreated) {
        sessionRecordCreated = true;
        const token = await getIdToken();
        if (!token) { login(); return; }
        const title = message.length > 60 ? message.slice(0, 57) + '...' : message;
        fetch(`${API_URL}/sessions/${currentSessionId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title }),
        }).catch(err => console.error('[app] Failed to create session record:', err));
    }

    // Hide welcome screen
    $welcomeScreen.style.display = 'none';

    // Render user message
    appendUserMessage(message);

    // Clear input
    $input.value = '';
    $input.style.height = 'auto';
    $sendBtn.disabled = true;

    // Send to API with streaming
    await sendMessage(message);

    // Refresh sessions list (the new message may have created/updated a session)
    await loadSessions();
}

async function sendMessage(message) {
    isStreaming = true;
    currentStreamBuffer = '';

    const token = await getIdToken();
    if (!token) {
        login();
        return;
    }

    // Create assistant message container with thinking indicator
    const { messageEl, contentEl } = createAssistantBubble();
    showThinkingIndicator(contentEl);
    scrollToBottom();

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: message,
                session_id: currentSessionId,
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('[app] Chat request failed:', response.status, errorText);
            contentEl.innerHTML = `<div class="error-message">Request failed (${response.status}). Please try again.</div>`;
            isStreaming = false;
            return;
        }

        // Stream the response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            processChunk(chunk, contentEl);
            scrollToBottom();
        }

        // Final render pass to ensure complete markdown
        finishStreaming(contentEl);
    } catch (err) {
        console.error('[app] Streaming error:', err);
        if (currentStreamBuffer.length === 0) {
            contentEl.innerHTML = `<div class="error-message">Connection error. Please check your network and try again.</div>`;
        } else {
            finishStreaming(contentEl);
        }
    }

    isStreaming = false;
}

// ---------------------------------------------------------------------------
// Chunk processing
// ---------------------------------------------------------------------------

const TOOL_INDICATORS = {
    code_interpreter: { label: 'Running code',       icon: 'terminal' },
    browser:          { label: 'Browsing the web',    icon: 'globe' },
    browser_tool:     { label: 'Browsing the web',    icon: 'globe' },
    task_management:  { label: 'Managing tasks',      icon: 'checklist' },
    memory:           { label: 'Searching memory',    icon: 'brain' },
    mcp_tool:         { label: 'Using tool',          icon: 'tool' },
};

const TOOL_ICONS = {
    terminal:  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>',
    globe:     '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>',
    checklist: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>',
    brain:     '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"></path></svg>',
    tool:      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>',
};

// Buffer for incomplete SSE lines across chunks
let sseLineBuffer = '';

function processChunk(chunk, contentEl) {
    // Accumulate with any leftover partial line from the previous chunk
    const raw = sseLineBuffer + chunk;
    const lines = raw.split('\n');

    // The last element may be an incomplete line -- save it for next chunk
    sseLineBuffer = lines.pop() || '';

    for (const line of lines) {
        if (!line.startsWith('data: ')) continue;

        const payload = line.substring(6); // strip "data: "

        // Skip Python repr debug lines (start with "{'data'" or similar)
        if (payload.startsWith('"') || payload.startsWith("'") || payload.startsWith("{'")) continue;

        let parsed;
        try {
            parsed = JSON.parse(payload);
        } catch {
            continue; // not valid JSON -- skip
        }

        // --- Text delta from the model ---
        const delta = parsed?.event?.contentBlockDelta?.delta;
        if (delta?.text) {
            // Hide thinking indicator on first content
            hideThinkingIndicator(contentEl);

            // Trim leading whitespace/newlines from the very start of the response
            if (currentStreamBuffer.length === 0) {
                currentStreamBuffer += delta.text.replace(/^\n+/, '');
            } else {
                currentStreamBuffer += delta.text;
            }
        }

        // --- Tool-use markers (inline JSON from agent) ---
        if (parsed?.tool && parsed?.status) {
            const toolName = parsed.tool;
            const status   = parsed.status;
            const indicator = TOOL_INDICATORS[toolName] || { label: toolName, icon: 'tool' };

            if (status === 'running') {
                showToolIndicator(contentEl, indicator);
            } else if (status === 'complete') {
                hideToolIndicator(contentEl, toolName);
            }
        }

        // --- Tool use start (show indicator when model invokes a tool) ---
        if (parsed?.event?.contentBlockStart?.start?.toolUse) {
            const toolName = parsed.event.contentBlockStart.start.toolUse.name || '';
            // Map known agent tool names to our indicator keys
            const key = toolName.includes('code_interpreter') ? 'code_interpreter'
                      : toolName.includes('browser') ? 'browser'
                      : toolName.includes('task') ? 'task_management'
                      : toolName.includes('memory') ? 'memory'
                      : 'mcp_tool';
            const indicator = TOOL_INDICATORS[key] || { label: toolName, icon: 'tool' };
            showToolIndicator(contentEl, indicator);
        }

        // --- Tool use complete (content block stop after tool use) ---
        if (parsed?.event?.contentBlockStop != null && contentEl.querySelector('.tool-pill.active')) {
            // Mark the most recent active tool indicator as complete
            const activePills = contentEl.querySelectorAll('.tool-pill.active');
            if (activePills.length > 0) {
                const pill = activePills[activePills.length - 1];
                pill.classList.remove('active');
                pill.classList.add('complete');
                const spinner = pill.querySelector('.tool-spinner');
                if (spinner) spinner.remove();
            }
        }
    }

    // Render the accumulated buffer as markdown
    const rendered = renderMarkdown(currentStreamBuffer);
    const markdownContainer = contentEl.querySelector('.message-markdown');
    if (markdownContainer) {
        markdownContainer.innerHTML = rendered;
    }
}

function showToolIndicator(contentEl, indicator) {
    let indicatorBar = contentEl.querySelector('.tool-indicators');
    if (!indicatorBar) {
        indicatorBar = document.createElement('div');
        indicatorBar.className = 'tool-indicators';
        contentEl.insertBefore(indicatorBar, contentEl.firstChild);
    }

    const pill = document.createElement('div');
    pill.className = 'tool-pill active';
    pill.dataset.tool = indicator.label;
    pill.innerHTML = `
        ${TOOL_ICONS[indicator.icon] || ''}
        <span>${escapeHtml(indicator.label)}</span>
        <div class="tool-spinner"></div>
    `;
    indicatorBar.appendChild(pill);
}

function hideToolIndicator(contentEl, toolName) {
    const indicatorBar = contentEl.querySelector('.tool-indicators');
    if (!indicatorBar) return;

    const indicator = TOOL_INDICATORS[toolName];
    if (!indicator) return;

    const pills = indicatorBar.querySelectorAll('.tool-pill');
    for (const pill of pills) {
        if (pill.dataset.tool === indicator.label) {
            pill.classList.remove('active');
            pill.classList.add('complete');
            const spinner = pill.querySelector('.tool-spinner');
            if (spinner) spinner.remove();
        }
    }
}

function showThinkingIndicator(contentEl) {
    const indicator = document.createElement('div');
    indicator.className = 'thinking-indicator';
    indicator.innerHTML = `
        <div class="thinking-dots">
            <span></span><span></span><span></span>
        </div>
    `;
    contentEl.insertBefore(indicator, contentEl.firstChild);
}

function hideThinkingIndicator(contentEl) {
    const indicator = contentEl.querySelector('.thinking-indicator');
    if (indicator) indicator.remove();
}

function finishStreaming(contentEl) {
    hideThinkingIndicator(contentEl);
    const rendered = renderMarkdown(currentStreamBuffer);
    const markdownContainer = contentEl.querySelector('.message-markdown');
    if (markdownContainer) {
        markdownContainer.innerHTML = rendered;
    }
    currentStreamBuffer = '';
    sseLineBuffer = '';
}

// ---------------------------------------------------------------------------
// Message rendering
// ---------------------------------------------------------------------------

function appendUserMessage(content) {
    const el = document.createElement('div');
    el.className = 'message message-user';
    el.innerHTML = `<div class="message-bubble user-bubble"><div class="message-content">${escapeHtml(content)}</div></div>`;
    $messages.appendChild(el);
    scrollToBottom();
}

function appendAssistantMessage(content, streaming = true) {
    const { contentEl } = createAssistantBubble();
    const markdownContainer = contentEl.querySelector('.message-markdown');
    if (markdownContainer) {
        markdownContainer.innerHTML = renderMarkdown(content);
    }
    scrollToBottom();
}

function createAssistantBubble() {
    const el = document.createElement('div');
    el.className = 'message message-assistant';
    el.innerHTML = `
        <div class="assistant-avatar">A</div>
        <div class="message-bubble assistant-bubble">
            <div class="message-content">
                <div class="message-markdown"></div>
            </div>
        </div>
    `;
    $messages.appendChild(el);

    return {
        messageEl: el,
        contentEl: el.querySelector('.message-content'),
    };
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function scrollToBottom() {
    $chatContainer.scrollTop = $chatContainer.scrollHeight;
}

function generateUUID() {
    if (typeof crypto.randomUUID === 'function') {
        return crypto.randomUUID();
    }
    // Fallback for older browsers
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

function formatRelativeDate(dateStr) {
    if (!dateStr) return '';

    const date = new Date(dateStr);
    const now  = new Date();
    const diffMs = now - date;
    const diffMins  = Math.floor(diffMs / 60_000);
    const diffHours = Math.floor(diffMs / 3_600_000);
    const diffDays  = Math.floor(diffMs / 86_400_000);

    if (diffMins < 1)   return 'Just now';
    if (diffMins < 60)  return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7)   return `${diffDays}d ago`;

    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

// ---------------------------------------------------------------------------
// Initialize
// ---------------------------------------------------------------------------

init();
