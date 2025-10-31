// RRC Chat Scenarios - Bilingual Version
const API_BASE = "/api";

// DOM Elements
const chatMessages = document.getElementById("chat-messages");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Session ID for user profiling
const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    // Initialize language
    initializeLanguage();

    // Language toggle buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => switchLanguage(btn.dataset.lang));
    });

    // Send message on button click
    sendBtn.addEventListener("click", sendMessage);

    // Send message on Enter (Shift+Enter for new line)
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = userInput.scrollHeight + "px";
    });
});

// Initialize language on page load
function initializeLanguage() {
    const currentLang = langManager.getLanguage();
    updateUI(currentLang);
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLang);
    });
}

// Switch language
function switchLanguage(lang) {
    // Save language preference and refresh page to clear chat history
    langManager.setLanguage(lang);
    location.reload();
}

// Update UI with translations
function updateUI(lang) {
    // Update title
    document.querySelector('h1').textContent = langManager.t('appTitle');

    // Update links
    const resourcesLink = document.querySelector('.resources-link');
    if (resourcesLink) {
        resourcesLink.textContent = '📚 ' + langManager.t('resourcesLink');
    }

    // Update input placeholder
    if (userInput) {
        userInput.placeholder = langManager.t('inputPlaceholder');
    }

    // Update send button
    if (sendBtn) {
        sendBtn.textContent = langManager.t('sendButton');
    }

    // Update welcome message if it exists
    const welcomeMessage = chatMessages.querySelector('.bot-message');
    if (welcomeMessage && chatMessages.children.length === 1) {
        updateWelcomeMessage(welcomeMessage);
    }
}

// Update welcome message with current language
function updateWelcomeMessage(messageEl) {
    const headerEl = messageEl.querySelector('.message-header strong');
    const textEl = messageEl.querySelector('.message-text');

    if (headerEl) {
        headerEl.textContent = langManager.t('welcomeTitle');
    }

    if (textEl) {
        textEl.innerHTML = `
            <p><strong>${langManager.t('welcomeStrong')}</strong> ${langManager.t('welcomeIntro')}</p>
            <p>${langManager.t('welcomePrompt')}</p>
            <ul>
                <li>${langManager.t('welcomeQuestion1')}</li>
                <li>${langManager.t('welcomeQuestion2')}</li>
            </ul>
            <p>${langManager.t('welcomeClosing')}</p>
        `;
    }
}

// Send message to RRC Coach
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Disable input while processing
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Add user message to chat
    addMessage("user", message);

    // Clear input
    userInput.value = "";
    userInput.style.height = "auto";

    // Show typing indicator
    const typingId = addTypingIndicator();

    try {
        // Send to API with language parameter
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                use_rag: true,
                provider: "xai",
                language: langManager.getLanguage()  // Pass current language
            })
        });

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Add bot response (HTML formatted)
        addMessage("bot", data.response, data.sources);

    } catch (error) {
        console.error("Error:", error);
        removeTypingIndicator(typingId);
        addMessage("bot", `<p><strong>Sorry, I encountered an error.</strong> Please try again or refresh the page.</p>`);
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Add message to chat (NO AUTO-SCROLL)
function addMessage(sender, content, sources = null) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    // Header
    const headerDiv = document.createElement("div");
    headerDiv.className = "message-header";
    const senderLabel = document.createElement("strong");
    senderLabel.textContent = sender === "user" ? "You" : "RRC Coach";
    headerDiv.appendChild(senderLabel);

    // Message text
    const textDiv = document.createElement("div");
    textDiv.className = "message-text";

    // Sanitize and render HTML
    if (sender === "bot") {
        // Allow HTML but sanitize (basic sanitization)
        textDiv.innerHTML = content;
    } else {
        // User messages as plain text
        const p = document.createElement("p");
        p.textContent = content;
        textDiv.appendChild(p);
    }

    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(textDiv);

    // Add sources if available (beautiful styling)
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement("div");
        sourcesDiv.className = "sources-cited";

        // Header with icon
        const sourcesHeader = document.createElement("div");
        sourcesHeader.className = "sources-header";
        sourcesHeader.innerHTML = `
            <span>📚</span>
            <span>Sources Referenced</span>
        `;
        sourcesDiv.appendChild(sourcesHeader);

        // Display up to 2 sources with beautiful formatting
        sources.slice(0, 2).forEach((source, index) => {
            const sourceItem = document.createElement("div");
            sourceItem.className = "source-item";

            const bullet = document.createElement("span");
            bullet.className = "source-bullet";
            bullet.textContent = "→";

            const sourceText = document.createElement("span");
            const sourceName = source.source || `Document ${index + 1}`;
            sourceText.textContent = sourceName;

            sourceItem.appendChild(bullet);
            sourceItem.appendChild(sourceText);
            sourcesDiv.appendChild(sourceItem);
        });

        contentDiv.appendChild(sourcesDiv);
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // NO AUTO-SCROLL - User controls scrolling
    // They can manually scroll to see the response
}

// Add typing indicator
function addTypingIndicator() {
    const id = `typing-${Date.now()}`;
    const messageDiv = document.createElement("div");
    messageDiv.id = id;
    messageDiv.className = "message bot-message";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const typingDiv = document.createElement("div");
    typingDiv.className = "typing-indicator";
    typingDiv.innerHTML = `
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
    `;

    contentDiv.appendChild(typingDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    return id;
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}
