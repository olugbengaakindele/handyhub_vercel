document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("userMenuBtn");
    const menu = document.getElementById("userDropdown");

    if (btn && menu) {
    btn.addEventListener("click", function (e) {
        e.stopPropagation();
        menu.classList.toggle("hidden");
    });

    document.addEventListener("click", function (event) {
        if (!menu.classList.contains("hidden")) {
        if (!menu.contains(event.target) && !btn.contains(event.target)) {
            menu.classList.add("hidden");
        }
        }
    });
    }
});