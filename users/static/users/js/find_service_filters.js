class TradesSearch {
  constructor({ apiUrl, profileBaseUrl }) {
    this.apiUrl = apiUrl;
    this.profileBaseUrl = profileBaseUrl;

    this.category = document.getElementById("categorySelect");
    this.subcategory = document.getElementById("subcategorySelect");
    this.province = document.getElementById("provinceSelect");
    this.city = document.getElementById("citySelect");

    this.meta = document.getElementById("resultsMeta");
    this.grid = document.getElementById("resultsGrid");

    if (
      !this.category ||
      !this.subcategory ||
      !this.province ||
      !this.city ||
      !this.meta ||
      !this.grid
    ) {
      console.warn("TradesSearch: missing required DOM elements.");
      return;
    }

    // Cache all subcategory options except default
    this.defaultSubOption =
      this.subcategory.querySelector("option[value='']") || null;
    this.allSubOptions = Array.from(this.subcategory.querySelectorAll("option"))
      .filter((opt) => opt.value);

    // Cache all city options except default
    this.defaultCityOption =
      this.city.querySelector("option[value='']") || null;
    this.allCityOptions = Array.from(this.city.querySelectorAll("option"))
      .filter((opt) => opt.value);

    this.bind();

    // Run once on load
    this.filterSubcategories({ preserveSelection: true });
    this.filterCities({ preserveSelection: true });

    // Load results on first paint
    this.fetchAndRender();
  }

  bind() {
    this.category.addEventListener("change", () => {
      this.filterSubcategories({ preserveSelection: false });
      this.fetchAndRender();
    });

    this.subcategory.addEventListener("change", () => this.fetchAndRender());

    this.province.addEventListener("change", () => {
      this.filterCities({ preserveSelection: false });
      this.fetchAndRender();
    });

    this.city.addEventListener("change", () => this.fetchAndRender());
  }

  filterSubcategories({ preserveSelection = true } = {}) {
    const catId = this.category.value;
    const prevValue = this.subcategory.value;

    this.subcategory.innerHTML = "";

    if (this.defaultSubOption) {
      this.subcategory.appendChild(this.defaultSubOption);
    } else {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "All subcategories";
      this.subcategory.appendChild(opt);
    }

    if (!catId) {
      this.subcategory.disabled = true;
      this.subcategory.value = "";
      return;
    }

    this.subcategory.disabled = false;

    const matching = this.allSubOptions.filter(
      (opt) => opt.dataset.category === catId
    );
    matching.forEach((opt) => this.subcategory.appendChild(opt));

    if (preserveSelection && prevValue) {
      const stillExists = Array.from(this.subcategory.options).some(
        (o) => o.value === prevValue
      );
      this.subcategory.value = stillExists ? prevValue : "";
    } else {
      this.subcategory.value = "";
    }
  }

  filterCities({ preserveSelection = true } = {}) {
    const provinceValue = this.province.value;
    const prevValue = this.city.value;

    this.city.innerHTML = "";

    if (this.defaultCityOption) {
      this.city.appendChild(this.defaultCityOption);
    } else {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "All cities";
      this.city.appendChild(opt);
    }

    if (!provinceValue) {
      this.city.disabled = false;
      this.allCityOptions.forEach((opt) => this.city.appendChild(opt));

      if (preserveSelection && prevValue) {
        const stillExists = Array.from(this.city.options).some(
          (o) => o.value === prevValue
        );
        this.city.value = stillExists ? prevValue : "";
      } else {
        this.city.value = "";
      }
      return;
    }

    this.city.disabled = false;

    const matching = this.allCityOptions.filter(
      (opt) => opt.dataset.province === provinceValue
    );
    matching.forEach((opt) => this.city.appendChild(opt));

    if (preserveSelection && prevValue) {
      const stillExists = Array.from(this.city.options).some(
        (o) => o.value === prevValue
      );
      this.city.value = stillExists ? prevValue : "";
    } else {
      this.city.value = "";
    }
  }

  buildQuery() {
    const params = new URLSearchParams();

    if (this.category.value) params.set("category", this.category.value);
    if (this.subcategory.value) params.set("subcategory", this.subcategory.value);
    if (this.province.value) params.set("province", this.province.value);
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
            Try removing one or more filters.
          </div>
        `;
        return;
      }

      this.grid.innerHTML = data.results.map((p) => this.cardHtml(p)).join("");
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