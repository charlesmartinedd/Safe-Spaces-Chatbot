const API_BASE = "/api";

const elements = {
    chatMessages: document.getElementById("chat-messages"),
    userInput: document.getElementById("user-input"),
    sendBtn: document.getElementById("send-btn"),
    fileInput: document.getElementById("file-input"),
    uploadBtn: document.getElementById("upload-btn"),
    uploadStatus: document.getElementById("upload-status"),
    clearDocsBtn: document.getElementById("clear-docs-btn"),
    ragToggle: document.getElementById("rag-toggle"),
    docCount: document.getElementById("doc-count"),
    statusTag: document.getElementById("status"),
    providerSelect: document.getElementById("provider-select"),
};

let availableProviders = [];
let defaultProvider = null;

document.addEventListener("DOMContentLoaded", () => {
    checkHealth();
    updateDocumentCount();

    elements.sendBtn.addEventListener("click", sendMessage);
    elements.userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    elements.uploadBtn.addEventListener("click", uploadDocument);
    elements.clearDocsBtn.addEventListener("click", clearDocuments);

    document.querySelectorAll(".scenario-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            elements.userInput.value = btn.dataset.scenario;
            elements.userInput.focus();
        });
    });
});

function formatProviderName(key) {
    if (!key || key === "unknown") return "Model";
    if (key === "openai") return "OpenAI";
    if (key === "xai") return "xAI Grok";
    return key.toUpperCase();
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        if (data.status === "healthy") {
            setStatus("Online", "healthy");
        } else {
            setStatus("Error", "error");
        }

        elements.docCount.textContent = data.documents_count ?? 0;
        defaultProvider = data.default_provider || null;
        availableProviders = Array.isArray(data.providers) ? data.providers : [];
        populateProviderOptions();
    } catch (error) {
        console.error("Health check failed:", error);
        setStatus("Offline", "error");
    }
}

function setStatus(text, state) {
    elements.statusTag.textContent = text;
    elements.statusTag.className = `status-tag ${state}`;
}

function populateProviderOptions() {
    const select = elements.providerSelect;
    select.innerHTML = "";

    if (!availableProviders.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "Not configured";
        select.appendChild(option);
        select.disabled = true;
        return;
    }

    availableProviders.forEach((provider) => {
        const option = document.createElement("option");
        option.value = provider;
        option.textContent = formatProviderName(provider);
        select.appendChild(option);
    });

    const fallback = defaultProvider && availableProviders.includes(defaultProvider)
        ? defaultProvider
        : availableProviders[0];

    select.value = fallback;
    select.disabled = false;
}

async function updateDocumentCount() {
    try {
        const response = await fetch(`${API_BASE}/documents/count`);
        const data = await response.json();
        elements.docCount.textContent = data.count ?? 0;
    } catch (error) {
        console.error("Failed to get document count:", error);
    }
}

async function sendMessage() {
    const message = elements.userInput.value.trim();
    if (!message) return;

    addMessage({ sender: "user", text: message, provider: formatProviderName(elements.providerSelect.value) });
    elements.userInput.value = "";
    elements.sendBtn.disabled = true;

    const loadingId = addLoadingMessage(formatProviderName(elements.providerSelect.value));

    try {
        const payload = {
            message,
            use_rag: elements.ragToggle.checked,
            provider: elements.providerSelect.disabled ? null : elements.providerSelect.value || null,
        };

        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        removeLoadingMessage(loadingId);

        if (!response.ok) {
            throw new Error(data.detail || "Request failed");
        }

        addMessage({
            sender: "bot",
            text: data.response,
            sources: data.sources,
            provider: formatProviderName(data.provider),
        });
    } catch (error) {
        console.error("Error sending message:", error);
        removeLoadingMessage(loadingId);
        addMessage({ sender: "bot", text: "Sorry, I encountered an error. Please try again.", provider: "System" });
    } finally {
        elements.sendBtn.disabled = false;
        elements.userInput.focus();
    }
}

function addMessage({ sender, text, sources = null, provider = null }) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const headerDiv = document.createElement("div");
    headerDiv.className = "message-header";

    const senderLabel = document.createElement("strong");
    senderLabel.textContent = sender === "user" ? "You" : "Safe Spaces Assistant";
    headerDiv.appendChild(senderLabel);

    if (provider) {
        const providerPill = document.createElement("span");
        providerPill.className = "provider-pill";
        providerPill.textContent = provider;
        headerDiv.appendChild(providerPill);
    }

    const messageText = document.createElement("p");
    messageText.textContent = text;

    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(messageText);

    if (sources && Array.isArray(sources) && sources.length > 0) {
        const sourcesDiv = document.createElement("div");
        sourcesDiv.className = "sources";
        const title = document.createElement("strong");
        title.textContent = "Knowledge base excerpts";
        sourcesDiv.appendChild(title);

        const list = document.createElement("ul");
        sources.slice(0, 5).forEach((item) => {
            const li = document.createElement("li");
            li.textContent = `${item.source || "Document"} (chunk ${item.chunk ?? 0})`;
            list.appendChild(li);
        });
        sourcesDiv.appendChild(list);
        contentDiv.appendChild(sourcesDiv);
    }

    messageDiv.appendChild(contentDiv);
    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function addLoadingMessage(providerLabel) {
    const loadingId = `loading-${Date.now()}`;
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";
    messageDiv.id = loadingId;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const headerDiv = document.createElement("div");
    headerDiv.className = "message-header";

    const senderLabel = document.createElement("strong");
    senderLabel.textContent = "Safe Spaces Assistant";
    headerDiv.appendChild(senderLabel);

    if (providerLabel) {
        const providerPill = document.createElement("span");
        providerPill.className = "provider-pill";
        providerPill.textContent = providerLabel;
        headerDiv.appendChild(providerPill);
    }

    const loadingDiv = document.createElement("div");
    loadingDiv.style.cssText = "display: flex; gap: 5px; margin-top: 5px;";
    loadingDiv.innerHTML = `
        <span class="loading"></span>
        <span class="loading"></span>
        <span class="loading"></span>
    `;

    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(loadingDiv);
    messageDiv.appendChild(contentDiv);
    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;

    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

async function uploadDocument() {
    const file = elements.fileInput.files[0];
    if (!file) {
        showUploadStatus("Please select a file", "error");
        return;
    }

    elements.uploadBtn.disabled = true;
    showUploadStatus("Uploading…", "success");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            showUploadStatus(`Successfully uploaded ${data.filename} (${data.chunks_created} chunks)`, "success");
            elements.fileInput.value = "";
            updateDocumentCount();
            checkHealth();
        } else {
            showUploadStatus(`Error: ${data.detail}`, "error");
        }
    } catch (error) {
        console.error("Upload error:", error);
        showUploadStatus("Upload failed. Please try again.", "error");
    } finally {
        elements.uploadBtn.disabled = false;
    }
}

function showUploadStatus(message, type) {
    elements.uploadStatus.style.display = "block";
    elements.uploadStatus.textContent = message;
    elements.uploadStatus.className = `status-message ${type}`;

    if (type === "success") {
        setTimeout(() => {
            elements.uploadStatus.style.display = "none";
        }, 5000);
    }
}

async function clearDocuments() {
    if (!confirm("Are you sure you want to clear all documents? This cannot be undone.")) {
        return;
    }

    elements.clearDocsBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/documents`, { method: "DELETE" });
        const data = await response.json();

        if (response.ok) {
            showUploadStatus("All documents cleared", "success");
            updateDocumentCount();
            checkHealth();
        } else {
            showUploadStatus(data.detail || "Failed to clear documents", "error");
        }
    } catch (error) {
        console.error("Clear error:", error);
        showUploadStatus("Failed to clear documents", "error");
    } finally {
        elements.clearDocsBtn.disabled = false;
    }
}
