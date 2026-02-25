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

    this.limit = config.limit;

    if (!this.container || !this.provinceSelect || !this.countEl || !this.limitEl) {
      return; // fail silently if page doesn't have expected markup
    }

    this.checkboxes = Array.from(this.container.querySelectorAll(this.checkboxSelector));
    this.cards = Array.from(this.container.querySelectorAll(this.cardSelector));
    this.groups = Array.from(this.container.querySelectorAll(this.groupSelector));

    this.bindEvents();
    this.updateCount();
    this.applyLimitRules();
    this.applyProvinceFilter(this.provinceSelect.value);
  }

  bindEvents() {
    // Checkbox changes
    this.checkboxes.forEach(cb => {
      cb.addEventListener("change", () => {
        this.updateCount();
        this.applyLimitRules();
      });
    });

    // Province filter
    this.provinceSelect.addEventListener("change", () => {
      this.applyProvinceFilter(this.provinceSelect.value);
      this.applyLimitRules(); // ensure disable rules re-apply to visible items
    });

    // Clear filter
    if (this.clearBtn) {
      this.clearBtn.addEventListener("click", () => {
        this.provinceSelect.value = "ALL";
        this.applyProvinceFilter("ALL");
        this.applyLimitRules();
      });
    }
  }

  getSelectedCount() {
    return this.checkboxes.filter(cb => cb.checked).length;
  }

  updateCount() {
    const count = this.getSelectedCount();
    this.countEl.textContent = String(count);
    this.limitEl.textContent = String(this.limit);
  }

  applyLimitRules() {
    const selectedCount = this.getSelectedCount();
    const limitReached = selectedCount >= this.limit;

    this.cards.forEach(card => {
      const cb = card.querySelector(this.checkboxSelector);
      if (!cb) return;

      // Only enforce on visible cards
      const isHidden = card.classList.contains("hidden");
      if (isHidden) return;

      if (limitReached && !cb.checked) {
        cb.disabled = true;
        card.classList.add("opacity-50", "pointer-events-none");
      } else {
        cb.disabled = false;
        card.classList.remove("opacity-50", "pointer-events-none");
      }
    });
  }

  applyProvinceFilter(provinceValue) {
    // Show/hide cards
    this.cards.forEach(card => {
      const cardProvince = card.getAttribute("data-province") || "";
      const matches = provinceValue === "ALL" || cardProvince === provinceValue;

      if (matches) {
        card.classList.remove("hidden");
      } else {
        card.classList.add("hidden");

        // Important: if a hidden item was disabled by limit rules,
        // re-enable it so it doesn't stay "stuck" when filter changes.
        const cb = card.querySelector(this.checkboxSelector);
        if (cb) cb.disabled = false;
        card.classList.remove("opacity-50", "pointer-events-none");
      }
    });

    // Hide metro groups that have zero visible cards
    this.groups.forEach(group => {
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
  const scriptTag = document.querySelector('script[src*="service_area_selector.js"]');
  const limitFromData = scriptTag?.dataset?.serviceAreaLimit;
  const limit = Number(limitFromData || 5);

  new ServiceAreaSelector({
    containerSelector: "#serviceAreasContainer",
    provinceSelectSelector: "#provinceFilter",
    clearBtnSelector: "#clearProvince",
    countSelector: "#selectedCount",
    limitSelector: "#limitCount",
    checkboxSelector: "[data-area-checkbox]",
    cardSelector: "[data-area-card]",
    groupSelector: ".metro-group",
    limit: limit,
  });
});