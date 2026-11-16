// Collapsible curriculum pane. Toggles .sidebar-collapsed on main.app;
// sidebar.css applies it on desktop widths only. The pane (and its generate
// form) stays in the DOM, so the form keeps working after collapse/reopen.
(function () {
    var STORAGE_KEY = "adaptive-learning:curriculum-collapsed";

    var app = document.querySelector("main.app");
    var toggle = document.querySelector(".sidebar-toggle");
    if (!app || !toggle) return;

    function readStored() {
        try {
            return window.localStorage.getItem(STORAGE_KEY) === "1";
        } catch (e) {
            return false;
        }
    }

    function writeStored(collapsed) {
        try {
            window.localStorage.setItem(STORAGE_KEY, collapsed ? "1" : "0");
        } catch (e) {
            // Storage unavailable (private mode, blocked): state just won't persist.
        }
    }

    var reopen = document.createElement("button");
    reopen.type = "button";
    reopen.className = "sidebar-reopen";
    reopen.setAttribute("aria-expanded", "false");
    reopen.textContent = "Show curriculum";
    app.insertAdjacentElement("afterend", reopen);

    function apply(collapsed) {
        app.classList.toggle("sidebar-collapsed", collapsed);
        toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }

    function setCollapsed(collapsed) {
        apply(collapsed);
        writeStored(collapsed);
        // Move focus to the control that is still visible.
        (collapsed ? reopen : toggle).focus();
    }

    toggle.addEventListener("click", function () {
        setCollapsed(!app.classList.contains("sidebar-collapsed"));
    });
    reopen.addEventListener("click", function () {
        setCollapsed(false);
    });

    apply(readStored());
})();
