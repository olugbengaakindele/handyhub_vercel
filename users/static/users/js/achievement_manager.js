document.addEventListener("DOMContentLoaded", () => {
  const descriptionField = document.getElementById("id_description");
  const countEl = document.getElementById("achievementDescCount");

  if (!descriptionField || !countEl) return;

  const updateCount = () => {
    const len = descriptionField.value.length;
    countEl.textContent = `${len} / 300`;
  };

  descriptionField.addEventListener("input", updateCount);
  updateCount();
});