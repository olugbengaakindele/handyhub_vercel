class TradesSearch {
  constructor({ apiUrl, profileBaseUrl }) {
    this.apiUrl = apiUrl;
    this.profileBaseUrl = profileBaseUrl;

    this.category = document.getElementById("categorySelect");
    this.subcategory = document.getElementById("subcategorySelect");
    this.city = document.getElementById("citySelect");

    this.meta = document.getElementById("resultsMeta");
    this.grid = document.getElementById("resultsGrid");

    if (!this.category || !this.subcategory || !this.city || !this.meta || !this.grid) {
      console.warn("TradesSearch: missing required DOM elements.");
      return;
    }

    // ✅ Cache ALL subcategory options (except the first default)
    this.defaultSubOption = this.subcategory.querySelector("option[value='']") || null;
    this.allSubOptions = Array.from(this.subcategory.querySelectorAll("option"))
      .filter(opt => opt.value); // only real options

    this.bind();

    // ✅ Run once on load (supports coming from homepage with ?category=ID)
    this.filterSubcategories({ preserveSelection: true });

    // ✅ Load results on first paint
    this.fetchAndRender();
  }

  bind() {
    this.category.addEventListener("change", () => {
      this.filterSubcategories({ preserveSelection: false });
      this.fetchAndRender();
    });

    this.subcategory.addEventListener("change", () => this.fetchAndRender());
    this.city.addEventListener("change", () => this.fetchAndRender());
  }

  filterSubcategories({ preserveSelection = true } = {}) {
    const catId = this.category.value;
    const prevValue = this.subcategory.value;

    // Clear and rebuild list every time (most reliable)
    this.subcategory.innerHTML = "";
    if (this.defaultSubOption) {
      this.subcategory.appendChild(this.defaultSubOption);
    } else {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "All subcategories";
      this.subcategory.appendChild(opt);
    }

    // No category => disable + show only default
    if (!catId) {
      this.subcategory.disabled = true;
      this.subcategory.value = "";
      return;
    }

    // Category selected => enable and append only matching subcategories
    this.subcategory.disabled = false;

    const matching = this.allSubOptions.filter(opt => opt.dataset.category === catId);
    matching.forEach(opt => this.subcategory.appendChild(opt));

    // Preserve selection only if it still exists in the rebuilt list
    if (preserveSelection && prevValue) {
      const stillExists = Array.from(this.subcategory.options).some(o => o.value === prevValue);
      this.subcategory.value = stillExists ? prevValue : "";
    } else {
      // If user changed category, clear subcategory (better UX)
      this.subcategory.value = "";
    }
  }

  buildQuery() {
    const params = new URLSearchParams();
    if (this.category.value) params.set("category", this.category.value);
    if (this.subcategory.value) params.set("subcategory", this.subcategory.value);
    if (this.city.value) params.set("city", this.city.value);
    return params.toString();
  }

  async fetchAndRender() {
    const qs = this.buildQuery();
    const url = qs ? `${this.apiUrl}?${qs}` : this.apiUrl;

    this.meta.textContent = "Searching…";
    this.grid.innerHTML = "";

    try {
      const res = await fetch(url, { method: "GET" });
      if (!res.ok) {
        this.meta.textContent = "Could not load results.";
        return;
      }

      const data = await res.json();
      this.meta.textContent = `${data.count} tradesperson(s) found`;

      if (!data.results || !data.results.length) {
        this.grid.innerHTML = `
          <div class="col-span-full bg-white border border-slate-200 rounded-2xl p-6 text-slate-600">
            <div class="font-extrabold text-slate-800 mb-1">No tradespeople found</div>
            Try removing the city or subcategory filter.
          </div>`;
        return;
      }

      this.grid.innerHTML = data.results.map(p => this.cardHtml(p)).join("");
    } catch (e) {
      console.error(e);
      this.meta.textContent = "Network error loading results.";
    }
  }

  cardHtml(p) {
    const img = p.image
      ? `<img src="${p.image}" class="w-12 h-12 rounded-full object-cover border border-emerald-200" />`
      : `<div class="w-12 h-12 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-xs">No Img</div>`;

    const summary = (p.summary || "").trim();
    const summaryLine = summary
      ? `<p class="text-sm text-slate-600 mt-2 line-clamp-3">${this.escape(summary)}</p>`
      : "";

    const profileUrl = `${this.profileBaseUrl}${p.profile_id}/`;

    return `
      <a href="${profileUrl}"
         class="block bg-white border border-slate-200 rounded-2xl p-5 hover:border-emerald-300 hover:shadow-sm transition">
        <div class="flex items-center gap-4">
          ${img}
          <div class="min-w-0">
            <div class="font-extrabold text-slate-800 truncate">${this.escape(p.name || "Tradesperson")}</div>
            <div class="text-sm text-slate-500 truncate">${this.escape(p.business_name || "")}</div>
            <div class="text-xs text-slate-500 mt-1">${this.escape(p.city || "")}${p.province ? ", " + this.escape(p.province) : ""}</div>
          </div>
        </div>
        ${summaryLine}
      </a>
    `;
  }

  escape(str) {
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }
}

// Auto-init
document.addEventListener("DOMContentLoaded", () => {
  if (!window.TRADES_SEARCH_API_URL || !window.TRADES_PROFILE_BASE_URL) {
    console.warn("Missing TRADES_SEARCH_API_URL / TRADES_PROFILE_BASE_URL");
    return;
  }

  new TradesSearch({
    apiUrl: window.TRADES_SEARCH_API_URL,
    profileBaseUrl: window.TRADES_PROFILE_BASE_URL,
  });
});
