// messaging/static/messaging/js/chat.js

class ChatApp {
  constructor(config) {
    // Elements
    this.chatBox = document.getElementById(config.chatBoxId);
    this.form = document.getElementById(config.formId);
    this.sendBtn = document.getElementById(config.sendBtnId);
    this.errorBox = document.getElementById(config.errorBoxId);
    this.uploadHint = document.getElementById(config.uploadHintId);
    this.imageInput = document.getElementById(config.imageInputId);
    this.contentInput = document.getElementById(config.contentInputId);

    // Endpoints + settings
    this.sendUrl = config.sendUrl;
    this.pollUrl = config.pollUrl;
    this.lastId = parseInt(config.lastId || "0", 10) || 0;
    this.pollInterval = config.pollInterval || 6000;

    this._assertRequired();
    this.init();
  }

  _assertRequired() {
    const missing = [];
    if (!this.chatBox) missing.push("chatBox");
    if (!this.form) missing.push("form");
    if (!this.sendBtn) missing.push("sendBtn");
    if (!this.errorBox) missing.push("errorBox");
    if (!this.uploadHint) missing.push("uploadHint");
    if (!this.imageInput) missing.push("imageInput");
    if (!this.contentInput) missing.push("contentInput");
    if (!this.sendUrl) missing.push("sendUrl");
    if (!this.pollUrl) missing.push("pollUrl");

    if (missing.length) {
      console.error("ChatApp init missing:", missing);
      throw new Error(`ChatApp init failed. Missing: ${missing.join(", ")}`);
    }
  }

  init() {
    this.scrollToBottom();
    this.bindEvents();
    this.startPolling();
  }

  bindEvents() {
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));
    this.imageInput.addEventListener("change", () => this.handleImageSelect());
  }

  // 1) CSRF from hidden input (best)
  getCSRFTokenFromForm() {
    const input = this.form.querySelector("input[name='csrfmiddlewaretoken']");
    return input ? input.value : "";
  }

  // 2) CSRF from cookie (fallback)
  getCSRFTokenFromCookie() {
    const name = "csrftoken=";
    const parts = document.cookie.split(";").map(s => s.trim());
    for (const p of parts) {
      if (p.startsWith(name)) return decodeURIComponent(p.substring(name.length));
    }
    return "";
  }

  getCSRFToken() {
    return this.getCSRFTokenFromForm() || this.getCSRFTokenFromCookie();
  }

  handleImageSelect() {
    const file = this.imageInput.files && this.imageInput.files[0] ? this.imageInput.files[0] : null;
    if (file) {
      this.uploadHint.classList.remove("hidden");
      this.uploadHint.textContent = `Selected: ${file.name}`;
    } else {
      this.uploadHint.classList.add("hidden");
      this.uploadHint.textContent = "";
    }
  }

  async safeJson(res) {
    try {
      return await res.json();
    } catch (_) {
      return null;
    }
  }

  formatDjangoErrors(errorsObj) {
    // { field: ["msg"], __all__: ["msg"] }
    const parts = [];
    try {
      for (const [field, msgs] of Object.entries(errorsObj || {})) {
        if (!Array.isArray(msgs)) continue;
        msgs.forEach((m) => {
          if (field === "__all__") parts.push(m);
          else parts.push(`${field}: ${m}`);
        });
      }
    } catch (_) {}
    return parts.length ? parts.join(" • ") : "";
  }

  async handleSubmit(e) {
    e.preventDefault();
    this.hideError();

    const text = (this.contentInput.value || "").trim();
    const hasImage = this.imageInput.files && this.imageInput.files.length > 0;

    if (!text && !hasImage) {
      return this.showError("Please type a message or attach an image.");
    }

    const formData = new FormData(this.form);

    this.sendBtn.disabled = true;
    this.sendBtn.textContent = "Sending...";

    try {
      const res = await fetch(this.sendUrl, {
        method: "POST",
        credentials: "same-origin", // ✅ IMPORTANT
        headers: {
          "X-CSRFToken": this.getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest"
        },
        body: formData
      });

      const data = await this.safeJson(res);

      // If Django returned form errors (400), show them
      if (data && data.errors) {
        const msg = this.formatDjangoErrors(data.errors) || "Could not send message.";
        this.showError(msg);
        return;
      }

      // If not OK and no JSON, show status and hint
      if (!res.ok) {
        if (res.status === 403) {
          this.showError("403 Forbidden (CSRF). Refresh the page and try again.");
        } else {
          this.showError(`Request failed (${res.status}). Check your Django terminal for the error.`);
        }
        return;
      }

      if (!data || !data.ok) {
        this.showError("Could not send message. Check your Django terminal for the error.");
        return;
      }

      // Success
      this.appendHtml(data.html);
      this.lastId = data.message_id;

      this.resetForm();
      this.scrollToBottom();
    } catch (err) {
      this.showError("Network error. Please try again.");
    } finally {
      this.sendBtn.disabled = false;
      this.sendBtn.textContent = "Send";
    }
  }

  async pollMessages() {
    try {
      const res = await fetch(`${this.pollUrl}?after_id=${this.lastId}`, {
        credentials: "same-origin", // ✅ IMPORTANT
        headers: { "X-Requested-With": "XMLHttpRequest" }
      });

      if (!res.ok) return;

      const data = await this.safeJson(res);
      if (!data || !data.ok) return;

      const chunks = data.html_chunks || [];
      if (!chunks.length) return;

      chunks.forEach((html) => this.appendHtml(html));
      this.lastId = data.last_id ?? this.lastId;
      this.scrollToBottom();
    } catch (_) {
      // silent MVP
    }
  }

  startPolling() {
    this._pollTimer = setInterval(() => this.pollMessages(), this.pollInterval);
  }

  appendHtml(html) {
    const container = this.chatBox.querySelector(".space-y-3");
    if (!container) return;

    const temp = document.createElement("div");
    temp.innerHTML = html;
    const node = temp.firstElementChild;
    if (node) container.appendChild(node);
  }

  scrollToBottom() {
    this.chatBox.scrollTop = this.chatBox.scrollHeight;
  }

  resetForm() {
    this.contentInput.value = "";
    this.imageInput.value = "";
    this.uploadHint.classList.add("hidden");
    this.uploadHint.textContent = "";
  }

  showError(msg) {
    this.errorBox.textContent = msg;
    this.errorBox.classList.remove("hidden");
  }

  hideError() {
    this.errorBox.textContent = "";
    this.errorBox.classList.add("hidden");
  }
}

window.ChatApp = ChatApp;
