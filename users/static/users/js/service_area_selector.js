class ServiceAreaSelector {
  constructor(config) {
    this.container = document.querySelector(config.containerSelector);
    this.provinceSelect = document.querySelector(config.provinceSelectSelector);
    this.clearBtn = document.querySelector(config.clearBtnSelector);

    this.countEl = document.querySelector(config.countSelector);
    this.limitEl = document.querySelector(config.limitSelector);

    this.checkboxSelector = config.checkboxSelector;
    this.cardSelector = config.cardSelector;
    this.groupSelector = config.groupSelector;

    this.limit = Number(config.limit || 0);

    if (!this.container || !this.provinceSelect || !this.countEl || !this.limitEl) {
      return; // fail silently if markup isn't present
    }

    this.checkboxes = Array.from(this.container.querySelectorAll(this.checkboxSelector));
    this.cards = Array.from(this.container.querySelectorAll(this.cardSelector));
    this.groups = Array.from(this.container.querySelectorAll(this.groupSelector));

    this.bindEvents();

    // Initial paint
    this.updateCountUI();
    this.applyProvinceFilter(this.provinceSelect.value);
    this.applyLimitRules();
  }

  bindEvents() {
    // Checkbox changes
    this.checkboxes.forEach((cb) => {
      cb.addEventListener("change", () => {
        this.updateCountUI();
        this.applyLimitRules();
      });
    });

    // Province filter
    this.provinceSelect.addEventListener("change", () => {
      this.applyProvinceFilter(this.provinceSelect.value);
      this.applyLimitRules(); // re-apply disable styles to visible cards
    });

    // Clear filter (optional)
    if (this.clearBtn) {
      this.clearBtn.addEventListener("click", (e) => {
        e.preventDefault();
        this.provinceSelect.value = "ALL";
        this.applyProvinceFilter("ALL");
        this.applyLimitRules();
      });
    }
  }

  getSelectedCount() {
    return this.checkboxes.reduce((acc, cb) => acc + (cb.checked ? 1 : 0), 0);
  }

  updateCountUI() {
    const count = this.getSelectedCount();
    this.countEl.textContent = String(count);
    this.limitEl.textContent = String(this.limit);
  }

  /**
   * Disable/grey out unchecked items when limit is reached.
   * IMPORTANT: enforce across ALL items (not just visible),
   * so if user changes province filter, the rules remain correct.
   */
  applyLimitRules() {
    const selectedCount = this.getSelectedCount();
    const limitReached = selectedCount >= this.limit;

    this.cards.forEach((card) => {
      const cb = card.querySelector(this.checkboxSelector);
      if (!cb) return;

      // When limit is reached, disable unchecked
      if (limitReached && !cb.checked) {
        this.disableCard(card, cb);
      } else {
        this.enableCard(card, cb);
      }
    });
  }

  disableCard(card, cb) {
    cb.disabled = true;

    // Visual grey-out (do NOT block pointer events on the label, because that can block unchecking in some browsers)
    card.classList.add("opacity-50");
    card.classList.add("cursor-not-allowed");

    // Optional: reduce hover
    card.classList.remove("hover:bg-emerald-50", "hover:border-emerald-400");
  }

  enableCard(card, cb) {
    cb.disabled = false;
    card.classList.remove("opacity-50", "cursor-not-allowed");

    // Restore hover styles (if you use them)
    card.classList.add("hover:bg-emerald-50", "hover:border-emerald-400");
  }

  /**
   * Filters by province by hiding cards.
   * Also hides metro groups that have no visible cards.
   */
  applyProvinceFilter(provinceValue) {
    const isAll = provinceValue === "ALL";

    this.cards.forEach((card) => {
      const cardProvince = (card.getAttribute("data-province") || "").trim();
      const matches = isAll || cardProvince === provinceValue;

      if (matches) {
        card.classList.remove("hidden");
      } else {
        card.classList.add("hidden");
      }
    });

    // Hide groups with zero visible cards
    this.groups.forEach((group) => {
      const visibleCards = group.querySelectorAll(`${this.cardSelector}:not(.hidden)`);
      if (visibleCards.length === 0) {
        group.classList.add("hidden");
      } else {
        group.classList.remove("hidden");
      }
    });
  }
}

// Boot
document.addEventListener("DOMContentLoaded", () => {
  // Read limit from script tag dataset (recommended)
  const scriptTag = document.querySelector('script[src*="edit_service_areas.js"]');
  const limitFromData = scriptTag?.dataset?.limit;
  const limit = Number(limitFromData || 5);

  new ServiceAreaSelector({
    containerSelector: "#areasContainer",          // ✅ matches your template ID
    provinceSelectSelector: "#provinceFilter",
    clearBtnSelector: "#clearProvince",            // optional button id
    countSelector: "#selectedCount",
    limitSelector: "#maxCount",                    // ✅ matches your template ID
    checkboxSelector: ".area-checkbox",
    cardSelector: ".area-card",
    groupSelector: ".metro-group",
    limit: limit,
  });
});