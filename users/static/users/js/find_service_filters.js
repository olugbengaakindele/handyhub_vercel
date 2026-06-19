function getCookie(name) {
  let cookieValue = null;

  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
      cookie = cookie.trim();

      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }

  return cookieValue;
}

class TradesSearch {
  constructor({ apiUrl, profileBaseUrl }) {
    this.apiUrl = apiUrl;
    this.profileBaseUrl = profileBaseUrl;

    this.category = document.getElementById("categorySelect");
    this.subcategory = document.getElementById("subcategorySelect");
    this.province = document.getElementById("provinceSelect");
    this.city = document.getElementById("citySelect");
    this.sort = document.getElementById("sortSelect");

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

    this.allSubOptions = Array.from(this.subcategory.querySelectorAll("option"))
      .filter((opt) => opt.value);

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
    const name = p.name || p.business_name || p.username || "Tradesperson";

    const img = p.image
      ? `<img src="${p.image}" class="w-12 h-12 rounded-full object-cover" />`
      : `<div class="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center text-xs">No Img</div>`;

    const verifiedBadge = p.email_verified
      ? `<span class="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-800">
          ✓ Verified Email
        </span>`
      : "";

    const memberSince = p.member_since
      ? `<span class="text-xs text-gray-500">Member since ${p.member_since}</span>`
      : "";

    return `
      <a href="${this.profileBaseUrl}${p.profile_id}/"
        class="block border rounded-xl p-4 hover:shadow bg-white">
        <div class="flex gap-3">
          ${img}

          <div class="flex-1">
            <div class="font-bold text-slate-900">${name}</div>

            ${p.business_name ? `<div class="text-sm text-gray-500">${p.business_name}</div>` : ""}

            <div class="mt-2 flex flex-wrap gap-2 items-center">
              ${verifiedBadge}
              ${memberSince}
            </div>

            <div class="mt-2 text-xs text-gray-500">
              ${p.city || ""} ${p.province || ""}
            </div>
          </div>
        </div>
      </a>
    `;
  }
}

class ServiceSuggestion {
  constructor() {
    this.input = document.getElementById("problemInput");
    this.button = document.getElementById("suggestServiceBtn");
    this.resultBox = document.getElementById("suggestionResult");

    if (!this.input || !this.button || !this.resultBox) {
      console.warn("ServiceSuggestion: missing DOM elements.");
      return;
    }

    this.bind();
  }

  bind() {
    this.button.addEventListener("click", () => this.suggest());
  }

  async suggest() {
    const problem = this.input.value.trim();

    this.resultBox.classList.remove("hidden");
    this.resultBox.innerHTML = "";

    if (!problem) {
      this.resultBox.innerHTML = `
        <div class="rounded-xl bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          Please describe the problem first.
        </div>
      `;
      return;
    }

    if (!window.SERVICE_SUGGESTION_API_URL) {
      this.resultBox.innerHTML = `
        <div class="rounded-xl bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          Suggestion API URL is missing.
        </div>
      `;
      return;
    }

    this.button.disabled = true;
    this.button.innerText = "Checking...";

    try {
      const response = await fetch(window.SERVICE_SUGGESTION_API_URL, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ problem: problem }),
      });

      const data = await response.json();

      if (!data.success) {
        this.resultBox.innerHTML = `
          <div class="rounded-xl bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 text-sm">
            ${data.message || data.error || "No matching service found."}
          </div>
        `;
        return;
      }

      const suggestion = data.suggestion;

      this.resultBox.innerHTML = `
        <div class="rounded-xl bg-emerald-50 border border-emerald-200 px-4 py-4">
          <p class="text-sm text-slate-700 mb-2">Suggested service:</p>

          <p class="font-bold text-emerald-800">
            ${suggestion.category_name} → ${suggestion.subcategory_name}
          </p>

          <a
            href="/find-service/?category=${suggestion.category_id}&subcategory=${suggestion.subcategory_id}"
            class="inline-flex mt-3 rounded-xl bg-emerald-600 px-4 py-2 text-white text-sm font-semibold hover:bg-emerald-700 transition"
          >
            Search this service
          </a>
        </div>
      `;
    } catch (error) {
      console.error("Suggestion error:", error);

      this.resultBox.innerHTML = `
        <div class="rounded-xl bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          Something went wrong. Please try again.
        </div>
      `;
    } finally {
      this.button.disabled = false;
      this.button.innerText = "Suggest Service";
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new TradesSearch({
    apiUrl: window.TRADES_SEARCH_API_URL,
    profileBaseUrl: window.TRADES_PROFILE_BASE_URL,
  });

  new ServiceSuggestion();
});