class TradesSearch {
  constructor({ apiUrl, profileBaseUrl }) {
    this.apiUrl = apiUrl;
    this.profileBaseUrl = profileBaseUrl;

    this.category = document.getElementById("categorySelect");
    this.subcategory = document.getElementById("subcategorySelect");
    this.province = document.getElementById("provinceSelect");
    this.city = document.getElementById("citySelect");
    this.sort = document.getElementById("sortSelect"); // ✅ NEW

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

    this.defaultSubOption =
      this.subcategory.querySelector("option[value='']") || null;

    this.allSubOptions = Array.from(this.subcategory.querySelectorAll("option"))
      .filter((opt) => opt.value);

    this.defaultCityOption =
      this.city.querySelector("option[value='']") || null;

    this.allCityOptions = Array.from(this.city.querySelectorAll("option"))
      .filter((opt) => opt.value);

    this.bind();
    this.filterSubcategories({ preserveSelection: true });
    this.filterCities({ preserveSelection: true });

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

    // ✅ SORT EVENT
    if (this.sort) {
      this.sort.addEventListener("change", () => this.fetchAndRender());
    }
  }

  filterSubcategories({ preserveSelection = true } = {}) {
    const catId = this.category.value;
    const prevValue = this.subcategory.value;

    this.subcategory.innerHTML = "";

    const defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = "All subcategories";
    this.subcategory.appendChild(defaultOpt);

    if (!catId) {
      this.subcategory.disabled = true;
      return;
    }

    this.subcategory.disabled = false;

    const matching = this.allSubOptions.filter(
      (opt) => opt.dataset.category === catId
    );

    matching.forEach((opt) => this.subcategory.appendChild(opt));

    if (preserveSelection && prevValue) {
      this.subcategory.value = prevValue;
    }
  }

  filterCities({ preserveSelection = true } = {}) {
    const provinceValue = this.province.value;
    const prevValue = this.city.value;

    this.city.innerHTML = "";

    const defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = "All cities";
    this.city.appendChild(defaultOpt);

    const matching = this.allCityOptions.filter((opt) => {
      if (!provinceValue) return true;
      return opt.dataset.province === provinceValue;
    });

    matching.forEach((opt) => this.city.appendChild(opt));

    if (preserveSelection && prevValue) {
      this.city.value = prevValue;
    }
  }

  buildQuery() {
    const params = new URLSearchParams();

    if (this.category.value) params.set("category", this.category.value);
    if (this.subcategory.value) params.set("subcategory", this.subcategory.value);
    if (this.province.value) params.set("province", this.province.value);
    if (this.city.value) params.set("city", this.city.value);

    // ✅ INCLUDE SORT
    if (this.sort && this.sort.value) {
      params.set("sort", this.sort.value);
    }

    return params.toString();
  }

  async fetchAndRender() {
    const qs = this.buildQuery();
    const url = qs ? `${this.apiUrl}?${qs}` : this.apiUrl;

    this.meta.textContent = "Searching…";
    this.grid.innerHTML = "";

    try {
      const res = await fetch(url);

      if (!res.ok) {
        this.meta.textContent = "Could not load results.";
        return;
      }

      const data = await res.json();

      this.meta.textContent = `${data.count} tradesperson(s) found`;

      if (!data.results || !data.results.length) {
        this.grid.innerHTML = `<div class="col-span-full">No results</div>`;
        return;
      }

      this.grid.innerHTML = data.results
        .map((p) => this.cardHtml(p))
        .join("");
    } catch (e) {
      console.error(e);
      this.meta.textContent = "Network error.";
    }
  }

  cardHtml(p) {
    const name =
      p.name || p.business_name || p.username || "Tradesperson";

    const img = p.image
      ? `<img src="${p.image}" class="w-12 h-12 rounded-full object-cover" />`
      : `<div class="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center text-xs">No Img</div>`;

    return `
      <a href="${this.profileBaseUrl}${p.profile_id}/"
         class="block border rounded-xl p-4 hover:shadow">
        <div class="flex gap-3">
          ${img}
          <div>
            <div class="font-bold">${name}</div>
            <div class="text-sm text-gray-500">${p.business_name || ""}</div>
            <div class="text-xs text-gray-500">${p.city || ""} ${p.province || ""}</div>
          </div>
        </div>
      </a>
    `;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new TradesSearch({
    apiUrl: window.TRADES_SEARCH_API_URL,
    profileBaseUrl: window.TRADES_PROFILE_BASE_URL,
  });
});