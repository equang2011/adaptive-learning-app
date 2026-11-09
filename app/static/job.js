// Waiting page for a background generation job.
// Shows an elapsed timer and asks the server every few seconds whether the
// job is done. When it is, goes to the result page.
(function () {
    var POLL_EVERY_MS = 2000;

    var root = document.getElementById("job");
    var jobId = root.dataset.jobId;
    var elapsedEl = root.querySelector(".loading-elapsed");
    var workingEl = root.querySelector(".job-working");
    var failedEl = root.querySelector(".job-failed");
    var errorEl = root.querySelector(".job-error");

    // The server says how many seconds the job has been running. Work out when
    // that was by this device's clock, so the count survives reloads.
    var start = Date.now() - Number(root.dataset.elapsed) * 1000;
    var timerId = null;
    var pollId = null;
    var finished = false;

    function showElapsed() {
        var seconds = Math.max(0, Math.floor((Date.now() - start) / 1000));
        elapsedEl.textContent = "Elapsed: " + seconds + "s";
    }

    function finish() {
        finished = true;
        clearInterval(timerId);
        clearTimeout(pollId);
    }

    function showFailure(message) {
        finish();
        if (message) errorEl.textContent = message;
        workingEl.hidden = true;
        failedEl.hidden = false;
    }

    function scheduleNextCheck() {
        clearTimeout(pollId);
        if (!finished) pollId = setTimeout(checkStatus, POLL_EVERY_MS);
    }

    function checkStatus() {
        clearTimeout(pollId);
        fetch("/internal/jobs/" + encodeURIComponent(jobId) + "/status", {
            cache: "no-store",
        })
            .then(function (response) {
                if (response.status === 404) {
                    // Job is gone (expired or server restarted). Reloading
                    // shows the server's "couldn't be found" page.
                    finish();
                    window.location.reload();
                    return;
                }
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json().then(function (job) {
                    if (job.status === "done") {
                        finish();
                        // replace(), not assign(): Back from the result should
                        // skip this waiting page.
                        window.location.replace(job.result_url);
                    } else if (job.status === "failed") {
                        showFailure(job.error);
                    } else {
                        scheduleNextCheck();
                    }
                });
            })
            .catch(function () {
                // Network blip (common right after returning to the app).
                // The job is still running on the server; just try again.
                scheduleNextCheck();
            });
    }

    // Coming back from another app: update immediately rather than waiting
    // for the next scheduled check.
    document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === "visible" && !finished) {
            showElapsed();
            checkStatus();
        }
    });

    if (!failedEl.hidden) {
        finish();
        return;
    }

    showElapsed();
    timerId = setInterval(showElapsed, 1000);
    checkStatus();
})();
