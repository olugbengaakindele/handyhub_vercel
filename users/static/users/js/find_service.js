let latestResults = [];

function escapeHtml(str) {
  return String(str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getProfileDisplayName(profile) {
  return (
    profile.name ||
    profile.business_name ||
    profile.username ||
    "Tradesperson"
  ).trim();
}

function getProfileSortName(profile) {
  return getProfileDisplayName(profile).toLowerCase();
}

function buildProfileCard(profile, profileBaseUrl) {
  const displayName = getProfileDisplayName(profile);

  const imageHtml = profile.image
    ? `<img src="${profile.image}" class="w-12 h-12 rounded-full object-cover border border-emerald-200" alt="Profile image" />`
    : `<div class="w-12 h-12 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-xs">No Img</div>`;

  const summary = (profile.summary || "").trim();
  const summaryHtml = summary
    ? `<p class="text-sm text-slate-600 mt-2 line-clamp-3">${escapeHtml(summary)}</p>`
    : "";

  const location = `${escapeHtml(profile.city || "")}${profile.province ? ", " + escapeHtml(profile.province) : ""}`;
  const profileUrl = `${profileBaseUrl}${profile.profile_id}/`;

  return `
    <a href="${profileUrl}"
       class="block bg-white border border-slate-200 rounded-2xl p-5 hover:border-emerald-300 hover:shadow-sm transition">
      <div class="flex items-center gap-4">
        ${imageHtml}
        <div class="min-w-0">
          <div class="font-extrabold text-slate-800 truncate">${escapeHtml(displayName)}</div>
          <div class="text-sm text-slate-500 truncate">${escapeHtml(profile.business_name || "")}</div>
          <div class="text-xs text-slate-500 mt-1">${location}</div>
        </div>
      </div>
      ${summaryHtml}
    </a>
  `;
}

function sortResults(results, sortValue) {
  const sorted = [...results];

  if (sortValue === "name_asc") {
    sorted.sort(function (a, b) {
      return getProfileSortName(a).localeCompare(getProfileSortName(b));
    });
  }

  if (sortValue === "name_desc") {
    sorted.sort(function (a, b) {
      return getProfileSortName(b).localeCompare(getProfileSortName(a));
    });
  }

  if (sortValue === "oldest") {
    sorted.sort(function (a, b) {
      return new Date(a.created_at || 0) - new Date(b.created_at || 0);
    });
  }

  if (sortValue === "newest") {
    sorted.sort(function (a, b) {
      return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    });
  }

  return sorted;
}

function renderEmptyResults(resultsGrid) {
  resultsGrid.innerHTML = `
    <div class="col-span-full bg-white border border-slate-200 rounded-2xl p-6 text-slate-600">
      <div class="font-extrabold text-slate-800 mb-1">No tradespeople found</div>
      Try removing one or more filters.
    </div>
  `;
}

function renderResults(resultsGrid, results, profileBaseUrl, sortSelect) {
  const sortValue = sortSelect ? sortSelect.value : "newest";
  const sortedResults = sortResults(results, sortValue);

  if (!sortedResults.length) {
    renderEmptyResults(resultsGrid);
    return;
  }

  resultsGrid.innerHTML = sortedResults
    .map(function (profile) {
      return buildProfileCard(profile, profileBaseUrl);
    })
    .join("");
}

function rebuildSubcategories(categorySelect, subcategorySelect, allSubOptions, preserveSelection) {
  const selectedCategory = categorySelect.value;
  const previousValue = subcategorySelect.value;

  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "All subcategories";

  subcategorySelect.innerHTML = "";
  subcategorySelect.appendChild(defaultOption);

  if (!selectedCategory) {
    subcategorySelect.disabled = true;
    subcategorySelect.value = "";
    return;
  }

  subcategorySelect.disabled = false;

  const matchingOptions = allSubOptions.filter(function (option) {
    return option.dataset.category === selectedCategory;
  });

  matchingOptions.forEach(function (option) {
    subcategorySelect.appendChild(option.cloneNode(true));
  });

  if (preserveSelection && previousValue) {
    const exists = Array.from(subcategorySelect.options).some(function (option) {
      return option.value === previousValue;
    });
    subcategorySelect.value = exists ? previousValue : "";
  } else {
    subcategorySelect.value = "";
  }
}

function rebuildCities(provinceSelect, citySelect, allCityOptions, preserveSelection) {
  const selectedProvince = provinceSelect.value;
  const previousValue = citySelect.value;

  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "All cities";

  citySelect.innerHTML = "";
  citySelect.appendChild(defaultOption);

  const matchingOptions = allCityOptions.filter(function (option) {
    if (!selectedProvince) return true;
    return option.dataset.province === selectedProvince;
  });

  matchingOptions.forEach(function (option) {
    citySelect.appendChild(option.cloneNode(true));
  });

  citySelect.disabled = false;

  if (preserveSelection && previousValue) {
    const exists = Array.from(citySelect.options).some(function (option) {
      return option.value === previousValue;
    });
    citySelect.value = exists ? previousValue : "";
  } else {
    citySelect.value = "";
  }
}

function buildSearchQuery(categorySelect, subcategorySelect, provinceSelect, citySelect) {
  const params = new URLSearchParams();

  if (categorySelect.value) params.set("category", categorySelect.value);
  if (subcategorySelect.value) params.set("subcategory", subcategorySelect.value);
  if (provinceSelect.value) params.set("province", provinceSelect.value);
  if (citySelect.value) params.set("city", citySelect.value);

  return params.toString();
}

async function fetchAndRenderResults(config) {
  const {
    apiUrl,
    profileBaseUrl,
    categorySelect,
    subcategorySelect,
    provinceSelect,
    citySelect,
    sortSelect,
    resultsMeta,
    resultsGrid,
  } = config;

  const queryString = buildSearchQuery(
    categorySelect,
    subcategorySelect,
    provinceSelect,
    citySelect
  );

  const url = queryString ? `${apiUrl}?${queryString}` : apiUrl;

  resultsMeta.textContent = "Searching…";
  resultsGrid.innerHTML = "";

  try {
    const response = await fetch(url, { method: "GET" });

    if (!response.ok) {
      resultsMeta.textContent = "Could not load results.";
      console.error("API request failed:", response.status, response.statusText);
      return;
    }

    const data = await response.json();

    latestResults = data.results || [];

    resultsMeta.textContent = `${data.count} tradesperson(s) found`;

    renderResults(resultsGrid, latestResults, profileBaseUrl, sortSelect);

  } catch (error) {
    console.error("Network/API error:", error);
    resultsMeta.textContent = "Network error loading results.";
  }
}

function initFindServicePage() {
  const categorySelect = document.getElementById("categorySelect");
  const subcategorySelect = document.getElementById("subcategorySelect");
  const provinceSelect = document.getElementById("provinceSelect");
  const citySelect = document.getElementById("citySelect");
  const sortSelect = document.getElementById("sortSelect");
  const resultsMeta = document.getElementById("resultsMeta");
  const resultsGrid = document.getElementById("resultsGrid");

  if (
    !categorySelect ||
    !subcategorySelect ||
    !provinceSelect ||
    !citySelect ||
    !resultsMeta ||
    !resultsGrid
  ) {
    console.warn("find_service.js: required DOM elements not found.");
    return;
  }

  if (!window.TRADES_SEARCH_API_URL || !window.TRADES_PROFILE_BASE_URL) {
    console.warn("find_service.js: missing TRADES_SEARCH_API_URL or TRADES_PROFILE_BASE_URL.");
    return;
  }

  const allSubOptions = Array.from(subcategorySelect.querySelectorAll("option")).filter(function (option) {
    return option.value;
  });

  const allCityOptions = Array.from(citySelect.querySelectorAll("option")).filter(function (option) {
    return option.value;
  });

  const config = {
    apiUrl: window.TRADES_SEARCH_API_URL,
    profileBaseUrl: window.TRADES_PROFILE_BASE_URL,
    categorySelect,
    subcategorySelect,
    provinceSelect,
    citySelect,
    sortSelect,
    resultsMeta,
    resultsGrid,
  };

  rebuildSubcategories(categorySelect, subcategorySelect, allSubOptions, true);
  rebuildCities(provinceSelect, citySelect, allCityOptions, true);

  fetchAndRenderResults(config);

  categorySelect.addEventListener("change", function () {
    rebuildSubcategories(categorySelect, subcategorySelect, allSubOptions, false);
    fetchAndRenderResults(config);
  });

  subcategorySelect.addEventListener("change", function () {
    fetchAndRenderResults(config);
  });

  provinceSelect.addEventListener("change", function () {
    rebuildCities(provinceSelect, citySelect, allCityOptions, false);
    fetchAndRenderResults(config);
  });

  citySelect.addEventListener("change", function () {
    fetchAndRenderResults(config);
  });

  if (sortSelect) {
    sortSelect.addEventListener("change", function () {
      renderResults(resultsGrid, latestResults, window.TRADES_PROFILE_BASE_URL, sortSelect);
    });
  }
}

document.addEventListener("DOMContentLoaded", initFindServicePage);