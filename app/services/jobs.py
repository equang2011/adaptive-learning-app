"""In-memory background jobs for slow generation requests.

A generation call takes 30-60 seconds. Running it inside the HTTP request
means the result is lost if the browser drops the request (iOS does this when
a tab is backgrounded). Instead, a route starts a job here and redirects to a
job page; the page polls for status and follows `result_url` when it's done.

Jobs live in this process's memory, so they are lost on restart and are not
shared between multiple server processes. That's fine for one Railway
instance; a multi-instance deploy would need a shared store (e.g. Redis).
"""

import logging
import secrets
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# How many generations may run at once. Extra jobs wait in the queue.
MAX_WORKERS = 4

# Finished or failed jobs are forgotten after this long.
JOB_TTL_SECONDS = 60 * 60

RUNNING = "running"
DONE = "done"
FAILED = "failed"


@dataclass
class Job:
    id: str
    kind: str
    started_at: float = field(default_factory=time.time)
    status: str = RUNNING
    result_url: str | None = None
    error: str | None = None
    finished_at: float | None = None


_jobs: dict[str, Job] = {}
_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="job")


def start_job(kind: str, work: Callable[[], str]) -> Job:
    """Run `work` in the background. It must return the URL of the result."""
    # 128 random bits: job ids can't be guessed, so a job URL is effectively
    # private to whoever started it.
    job = Job(id=secrets.token_urlsafe(16), kind=kind)

    with _lock:
        _remove_expired()
        _jobs[job.id] = job

    _executor.submit(_run, job, work)
    return job


def get_job(job_id: str) -> Job | None:
    with _lock:
        return _jobs.get(job_id)


def _run(job: Job, work: Callable[[], str]) -> None:
    try:
        result_url = work()
    except Exception:
        # Log the details for us; show the user a generic message.
        logger.exception("Background %s job %s failed", job.kind, job.id)
        with _lock:
            job.status = FAILED
            job.error = "Generation failed. Please try again."
            job.finished_at = time.time()
        return

    with _lock:
        job.status = DONE
        job.result_url = result_url
        job.finished_at = time.time()


def _remove_expired() -> None:
    """Drop finished jobs older than the TTL. Caller must hold _lock."""
    cutoff = time.time() - JOB_TTL_SECONDS
    expired = [
        job_id
        for job_id, job in _jobs.items()
        if job.finished_at is not None and job.finished_at < cutoff
    ]
    for job_id in expired:
        del _jobs[job_id]
