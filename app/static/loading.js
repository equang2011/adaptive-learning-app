// Shows a loading overlay when a form marked with data-loading-message is
// submitted: disables the submit button, shows a spinner and an elapsed timer.
(function () {
    document.querySelectorAll("form[data-loading-message]").forEach(function (form) {
        var overlay = null;
        var timerId = null;

        function buildOverlay() {
            var el = document.createElement("div");
            el.className = "loading-overlay";
            el.hidden = true;
            el.innerHTML =
                '<div class="loading-panel" role="status" aria-live="polite">' +
                '<div class="loading-spinner" aria-hidden="true"></div>' +
                '<p class="loading-message"></p>' +
                '<p class="loading-elapsed">Elapsed: 0s</p>' +
                "</div>";
            el.querySelector(".loading-message").textContent =
                form.dataset.loadingMessage;
            document.body.appendChild(el);
            return el;
        }

        function stop() {
            if (timerId !== null) {
                clearInterval(timerId);
                timerId = null;
            }
            if (overlay) overlay.hidden = true;
            form.querySelectorAll('button[type="submit"]').forEach(function (btn) {
                btn.disabled = false;
            });
        }

        form.addEventListener("submit", function () {
            // Runs after the browser's own validation passes.
            overlay = overlay || buildOverlay();
            var elapsedEl = overlay.querySelector(".loading-elapsed");
            var start = Date.now();
            elapsedEl.textContent = "Elapsed: 0s";
            overlay.hidden = false;

            // Disable after the form data has been collected for this submit.
            setTimeout(function () {
                form.querySelectorAll('button[type="submit"]').forEach(function (btn) {
                    btn.disabled = true;
                });
            }, 0);

            timerId = setInterval(function () {
                elapsedEl.textContent =
                    "Elapsed: " + Math.floor((Date.now() - start) / 1000) + "s";
            }, 1000);
        });

        // Coming back via the browser's Back button can restore the page
        // mid-loading from cache; reset it.
        window.addEventListener("pageshow", function (event) {
            if (event.persisted) stop();
        });
    });
})();
