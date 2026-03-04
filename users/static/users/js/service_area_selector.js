// static/users/js/service_area_selector.js

class ServiceAreaSelector {
  constructor(config) {
    // Core elements
    this.container = document.querySelector(config.containerSelector);
    this.provinceSelect = document.querySelector(config.provinceSelectSelector);
    this.clearBtn = document.querySelector(config.clearBtnSelector);

    // Counter UI
    this.countEl = document.querySelector(config.countSelector);
    this.limitEl = document.querySelector(config.limitSelector);

    // Current selections UI (NEW)
    this.currentBox = document.querySelector(config.currentBoxSelector);
    this.currentCountEl = document.querySelector(config.currentCountSelector);

    this.limit = Number(config.limit || 0);

    // Must-have elements for the selector to work
    if (!this.container || !this.provinceSelect || !this.countEl || !this.limitEl) return;

    // Failsafe selectors
    this.cardSelector = config.cardSelector || "label";
    this.checkboxSelector = config.checkboxSelector || 'input[type="checkbox"]';
    this.groupSelector = config.groupSelector || ".metro-group";

    this.cards = Array.from(this.container.querySelectorAll(this.cardSelector))
      .filter(el => el.querySelector(this.checkboxSelector));

    this.checkboxes = this.cards
      .map(card => card.querySelector(this.checkboxSelector))
      .filter(Boolean);

    this.groups = Array.from(this.container.querySelectorAll(this.groupSelector));

    this.bindEvents();
    this.refresh(); // initial paint
  }

  bindEvents() {
    this.checkboxes.forEach(cb => {
      cb.addEventListener("change", () => this.refresh());
    });

    this.provinceSelect.addEventListener("change", () => this.refresh());

    if (this.clearBtn) {
      this.clearBtn.addEventListener("click", (e) => {
        e.preventDefault();
        this.provinceSelect.value = "ALL";
        this.refresh();
      });
    }
  }

  refresh() {
    this.updateCountUI();
    this.applyProvinceFilter(this.provinceSelect.value);
    this.applyLimitRules();
    this.renderCurrentSelections(); // ✅ NEW
  }

  getSelectedCount() {
    return this.checkboxes.reduce((acc, cb) => acc + (cb.checked ? 1 : 0), 0);
  }

  updateCountUI() {
    const count = this.getSelectedCount();
    this.countEl.textContent = String(count);
    this.limitEl.textContent = String(this.limit);

    if (this.currentCountEl) {
      this.currentCountEl.textContent = `${count} selected`;
    }
  }

  // Get province for a card safely
  getCardProvince(card) {
    const dp = (card.getAttribute("data-province") || "").trim();
    if (dp) return dp;

    const text = (card.innerText || "").trim();
    const match = text.match(/,\s*([A-Z]{2})\b/);
    return match ? match[1] : "";
  }

  applyProvinceFilter(provinceValue) {
    const isAll = provinceValue === "ALL";

    this.cards.forEach(card => {
      const prov = this.getCardProvince(card);
      const matches = isAll || prov === provinceValue;
      card.classList.toggle("hidden", !matches);
    });

    // hide metro groups with zero visible cards
    this.groups.forEach(group => {
      const visible = group.querySelectorAll(`${this.cardSelector}:not(.hidden)`);
      group.classList.toggle("hidden", visible.length === 0);
    });
  }

  applyLimitRules() {
    const selectedCount = this.getSelectedCount();
    const limitReached = selectedCount >= this.limit;

    this.cards.forEach(card => {
      const cb = card.querySelector(this.checkboxSelector);
      if (!cb) return;

      const isHidden = card.classList.contains("hidden");
      const shouldDisable = !isHidden && limitReached && !cb.checked;

      cb.disabled = shouldDisable;

      card.classList.toggle("opacity-50", shouldDisable);
      card.classList.toggle("cursor-not-allowed", shouldDisable);

      if (shouldDisable) {
        card.classList.remove("hover:bg-emerald-50", "hover:border-emerald-400");
      } else {
        card.classList.add("hover:bg-emerald-50", "hover:border-emerald-400");
      }
    });
  }

  // --------------------------
  // NEW: Current selections list
  // --------------------------
  getSelectedCards() {
    return this.cards.filter(card => {
      const cb = card.querySelector(this.checkboxSelector);
      return cb && cb.checked;
    });
  }

  // Safe HTML escape
  escapeHtml(str) {
    return String(str ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  renderCurrentSelections() {
    if (!this.currentBox) return;

    const selectedCards = this.getSelectedCards();

    if (selectedCards.length === 0) {
      this.currentBox.innerHTML = `
        <div class="text-sm text-slate-500 bg-slate-50 border border-slate-200 rounded-xl px-4 py-4">
          No service areas selected yet.
        </div>
      `;
      return;
    }

    // Sort by metro then by name
    selectedCards.sort((a, b) => {
      const am = (a.dataset.metro || "").localeCompare(b.dataset.metro || "");
      if (am !== 0) return am;
      return (a.dataset.areaName || "").localeCompare(b.dataset.areaName || "");
    });

    this.currentBox.innerHTML = selectedCards.map(card => {
      const areaId = card.dataset.areaId || "";
      const name = card.dataset.areaName || "Unknown";
      const city = card.dataset.city || "";
      const prov = card.dataset.province || "";
      const metro = card.dataset.metro || "";

      return `
        <div class="flex items-center justify-between bg-white border border-slate-200 rounded-xl px-4 py-3">
          <div class="min-w-0">
            <p class="text-sm font-semibold text-slate-800 truncate">${this.escapeHtml(name)}</p>
            <p class="text-xs text-slate-500 truncate">${this.escapeHtml(city)}, ${this.escapeHtml(prov)} • ${this.escapeHtml(metro)}</p>
          </div>

          <button
            type="button"
            class="inline-flex items-center gap-2 text-xs font-semibold text-red-600 hover:text-red-700"
            data-remove-id="${this.escapeHtml(areaId)}"
            title="Remove"
          >
            🗑️ Delete
          </button>
        </div>
      `;
    }).join("");

    // Delete button: uncheck and refresh (does NOT auto-save; user clicks Save)
    this.currentBox.querySelectorAll("[data-remove-id]").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-remove-id");
        const card = this.cards.find(c => c.dataset.areaId === id);
        if (!card) return;

        const cb = card.querySelector(this.checkboxSelector);
        if (cb) cb.checked = false;

        this.refresh();
      });
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const scriptTag = document.querySelector('script[src*="service_area_selector.js"]');
  const limit = Number(scriptTag?.dataset?.limit || 5);

  new ServiceAreaSelector({
    containerSelector: "#areasContainer",
    provinceSelectSelector: "#provinceFilter",
    clearBtnSelector: "#clearProvince",
    countSelector: "#selectedCount",
    limitSelector: "#maxCount",

    // If your template uses these classes, keep them. If not, it will still work.
    checkboxSelector: ".area-checkbox",
    cardSelector: ".area-card",
    groupSelector: ".metro-group",

    // NEW: current selections panel
    currentBoxSelector: "#currentAreasBox",
    currentCountSelector: "#currentAreasCount",

    limit,
  });
});