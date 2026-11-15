// "Up next" block at the end of a lesson. Appended to the last .lesson-page,
// so the pager's existing show/hide logic makes it appear only on the last
// page. Clicking it selects the next leaf in the curriculum tree and submits
// the existing generate form via requestSubmit(), so loading.js still shows
// its overlay. Works when the desktop sidebar is collapsed (form hidden).
(function () {
    var pages = document.querySelectorAll(".lesson-page");
    var form = document.querySelector("form[data-loading-message]");
    var current = document.querySelector(".tree input.node-radio:checked");
    // No lesson, no form, or no ?node= in the URL: nothing to anchor on.
    if (pages.length === 0 || !form || !current) return;

    var radios = Array.prototype.slice.call(
        document.querySelectorAll(".tree input.node-radio")
    );
    var index = radios.indexOf(current);
    var next = index >= 0 && index < radios.length - 1 ? radios[index + 1] : null;

    function leafTitle(radio) {
        var label = radio.closest("label");
        var span = label ? label.querySelector(".leaf-text") : null;
        return span ? span.textContent.trim() : "";
    }

    function detailWord() {
        var select = document.getElementById("detail_level");
        if (!select || select.selectedIndex < 0) return "";
        var text = select.options[select.selectedIndex].textContent.trim();
        var cut = text.indexOf(" (");
        return cut >= 0 ? text.slice(0, cut) : text;
    }

    function hintText() {
        var word = detailWord();
        return word
            ? "Generates a new " + word + " lesson, usually 30–60 seconds."
            : "Generates a new lesson, usually 30–60 seconds.";
    }

    var block = document.createElement("section");
    block.className = "up-next";
    block.setAttribute("aria-label", "Up next");

    if (next) {
        var title = leafTitle(next);

        var label = document.createElement("div");
        label.className = "up-next-label";
        label.textContent = "Up next";

        var button = document.createElement("button");
        button.type = "button";
        button.className = "up-next-button";
        button.textContent = title;

        var hint = document.createElement("p");
        hint.className = "up-next-hint";
        hint.textContent = hintText();

        block.appendChild(label);
        block.appendChild(button);
        block.appendChild(hint);

        // Keep the hint accurate if the detail level is changed in the sidebar.
        var select = document.getElementById("detail_level");
        if (select) {
            select.addEventListener("change", function () {
                hint.textContent = hintText();
            });
        }

        function reset() {
            current.checked = true;
            button.disabled = false;
            button.textContent = title;
        }

        button.addEventListener("click", function () {
            if (button.disabled) return;
            next.checked = true;
            if (!form.checkValidity()) {
                // Should not happen (a radio is checked and the select has a
                // default), but never leave the button stuck on "Starting…".
                reset();
                return;
            }
            button.disabled = true;
            button.textContent = "Starting…";

            if (typeof form.requestSubmit === "function") {
                form.requestSubmit();
            } else {
                var event = new Event("submit", { bubbles: true, cancelable: true });
                if (form.dispatchEvent(event)) form.submit();
            }
        });

        // Back from the job page can restore this page from the bfcache with
        // the button disabled and the next radio still checked.
        window.addEventListener("pageshow", function (event) {
            if (event.persisted) reset();
        });
    } else {
        var done = document.createElement("p");
        done.className = "up-next-end";
        done.textContent = "You've reached the last lesson in this curriculum.";
        block.appendChild(done);
    }

    pages[pages.length - 1].appendChild(block);

    var wrap = document.querySelector(".lesson-wrap");
    if (wrap) wrap.classList.add("has-up-next");
})();
