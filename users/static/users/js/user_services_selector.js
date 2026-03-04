// static/users/js/user_services_selector.js

class UserServicesSelector {
  constructor() {
    this.form = document.querySelector("#userServicesForm");
    this.categorySelect = document.querySelector("#categorySelect");
    this.groups = Array.from(document.querySelectorAll(".subcategory-group"));

    this.badge = document.querySelector("#serviceCounterBadge");
    this.countEl = document.querySelector("#selectedServiceCount");
    this.limitEl = document.querySelector("#maxServiceCount");

    const scriptTag = document.querySelector('script[src*="user_services_selector.js"]');
    this.limit = Number(scriptTag?.dataset?.limit || 10);

    // base (existing services)
    this.existingCount = Number(this.badge?.dataset?.existingCount || 0);

    if (!this.form || !this.categorySelect || !this.countEl || !this.limitEl) return;

    this.limitEl.textContent = String(this.limit);

    this.bindEvents();
    this.refresh();
  }

  bindEvents() {
    this.categorySelect.addEventListener("change", () => {
      this.showSelectedCategoryGroup();
      this.refresh();
    });

    // Event delegation: any checkbox change
    this.form.addEventListener("change", (e) => {
      if (e.target && e.target.matches(".service-checkbox")) {
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

    return Array.from(group.querySelectorAll(".service-checkbox"));
  }

  getVisibleSelectedCount() {
    return this.getVisibleCheckboxes().reduce((acc, cb) => acc + (cb.checked ? 1 : 0), 0);
  }

  getTotalSelectedCount() {
    return this.existingCount + this.getVisibleSelectedCount();
  }

  applyLimitRules() {
    const visibleCheckboxes = this.getVisibleCheckboxes();
    const totalSelected = this.getTotalSelectedCount();
    const limitReached = totalSelected >= this.limit;

    visibleCheckboxes.forEach(cb => {
      const shouldDisable = limitReached && !cb.checked;
      cb.disabled = shouldDisable;

      const card = cb.closest(".service-card");
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
    // ensure right group is shown
    this.showSelectedCategoryGroup();

    // update counter (existing + new)
    const totalSelected = this.getTotalSelectedCount();
    this.countEl.textContent = String(totalSelected);

    // enforce limit when category selected
    if (this.categorySelect.value) {
      this.applyLimitRules();
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new UserServicesSelector();
});