// static/users/js/user_services_selector.js

class UserServicesSelector {
  constructor(config) {
    this.form = document.querySelector(config.formSelector);
    this.categorySelect = document.querySelector(config.categorySelectSelector);
    this.groups = Array.from(document.querySelectorAll(config.groupSelector));

    this.countEl = document.querySelector(config.countSelector);
    this.limitEl = document.querySelector(config.limitSelector);

    this.cardSelector = config.cardSelector || ".service-card";
    this.checkboxSelector = config.checkboxSelector || ".service-checkbox";

    const scriptTag = document.querySelector(config.scriptSelector);
    this.limit = Number(scriptTag?.dataset?.limit || config.limit || 10);

    if (!this.form || !this.categorySelect || !this.countEl || !this.limitEl) return;

    this.limitEl.textContent = String(this.limit);

    this.bindEvents();
    this.refresh(); // first paint
  }

  bindEvents() {
    // Category change
    this.categorySelect.addEventListener("change", () => {
      this.showSelectedCategoryGroup();
      this.refresh();
    });

    // Checkbox changes (event delegation)
    this.form.addEventListener("change", (e) => {
      const cb = e.target;
      if (cb && cb.matches(this.checkboxSelector)) {
        this.refresh();
      }
    });
  }

  showSelectedCategoryGroup() {
    const selectedCat = this.categorySelect.value;

    this.groups.forEach(group => {
      const match = group.dataset.category === selectedCat;
      group.classList.toggle("hidden", !match);
    });
  }

  getVisibleCheckboxes() {
    const selectedCat = this.categorySelect.value;
    if (!selectedCat) return [];

    const group = this.groups.find(g => g.dataset.category === selectedCat);
    if (!group) return [];

    return Array.from(group.querySelectorAll(this.checkboxSelector));
  }

  getVisibleSelectedCount() {
    return this.getVisibleCheckboxes().reduce((acc, cb) => acc + (cb.checked ? 1 : 0), 0);
  }

  applyLimitRules() {
    const checkboxes = this.getVisibleCheckboxes();
    const selectedCount = this.getVisibleSelectedCount();
    const limitReached = selectedCount >= this.limit;

    checkboxes.forEach(cb => {
      const shouldDisable = limitReached && !cb.checked;
      cb.disabled = shouldDisable;

      const card = cb.closest(this.cardSelector);
      if (!card) return;

      card.classList.toggle("opacity-50", shouldDisable);
      card.classList.toggle("cursor-not-allowed", shouldDisable);

      if (shouldDisable) {
        card.classList.remove("hover:bg-emerald-50", "hover:border-emerald-400");
      } else {
        card.classList.add("hover:bg-emerald-50", "hover:border-emerald-400");
      }
    });
  }

  refresh() {
    // Always ensure correct group is shown
    this.showSelectedCategoryGroup();

    // Count only visible category checkboxes
    const selectedCount = this.getVisibleSelectedCount();
    this.countEl.textContent = String(selectedCount);

    // Apply limit rules only when a category is selected
    if (this.categorySelect.value) {
      this.applyLimitRules();
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new UserServicesSelector({
    formSelector: "#userServicesForm",
    categorySelectSelector: "#categorySelect",
    groupSelector: ".subcategory-group",
    countSelector: "#selectedServiceCount",
    limitSelector: "#maxServiceCount",
    scriptSelector: 'script[src*="user_services_selector.js"]',
    checkboxSelector: ".service-checkbox",
    cardSelector: ".service-card",
    limit: 10,
  });
});