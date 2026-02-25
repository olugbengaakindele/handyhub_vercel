class ServiceAreaSelector {
  constructor(config) {
    this.container = document.querySelector(config.containerSelector);
    this.provinceSelect = document.querySelector(config.provinceSelectSelector);
    this.clearBtn = document.querySelector(config.clearBtnSelector);

    this.countEl = document.querySelector(config.countSelector);
    this.limitEl = document.querySelector(config.limitSelector);

    this.limit = Number(config.limit || 0);

    if (!this.container || !this.provinceSelect || !this.countEl || !this.limitEl) return;

    // ✅ Failsafe selectors (works even if classes are missing)
    this.cardSelector = config.cardSelector || "label";
    this.checkboxSelector = config.checkboxSelector || 'input[type="checkbox"]';
    this.groupSelector = config.groupSelector || ".metro-group";

    this.cards = Array.from(this.container.querySelectorAll(this.cardSelector))
      .filter(el => el.querySelector(this.checkboxSelector)); // only labels/cards that contain a checkbox

    this.checkboxes = this.cards
      .map(card => card.querySelector(this.checkboxSelector))
      .filter(Boolean);

    this.groups = Array.from(this.container.querySelectorAll(this.groupSelector));

    this.bindEvents();
    this.refresh();
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
  }

  getSelectedCount() {
    return this.checkboxes.reduce((acc, cb) => acc + (cb.checked ? 1 : 0), 0);
  }

  updateCountUI() {
    const count = this.getSelectedCount();
    this.countEl.textContent = String(count);
    this.limitEl.textContent = String(this.limit);
  }

  // ✅ Get province for a card safely
  getCardProvince(card) {
    // Preferred: data-province
    const dp = (card.getAttribute("data-province") || "").trim();
    if (dp) return dp;

    // Fallback: try to parse "City, MB" from the small text
    const text = (card.innerText || "").trim();
    const match = text.match(/,\s*([A-Z]{2})\b/); // finds ", MB"
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

      // optional: tone down hover when disabled
      if (shouldDisable) {
        card.classList.remove("hover:bg-emerald-50", "hover:border-emerald-400");
      } else {
        card.classList.add("hover:bg-emerald-50", "hover:border-emerald-400");
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const scriptTag = document.querySelector('script[src*="edit_service_areas.js"]');
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
    limit,
  });
});