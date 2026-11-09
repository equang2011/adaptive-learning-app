"""Tests for background generation jobs.

The real generators call an LLM, so these tests swap them for fakes.
"""

import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.curriculum import Curriculum
from app.routes import internal
from app.services import jobs, rate_limit

client = TestClient(app)

FAKE_CURRICULUM = {
    "title": "Docker basics",
    "description": "A short course.",
    "nodes": [
        {"id": "n1", "title": "Containers", "objective": "Run one.", "children": []},
    ],
}


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Write generations to a temp dir and reset in-memory state."""
    monkeypatch.setattr(internal, "DATA_DIR", tmp_path)
    monkeypatch.setattr(internal, "LESSON_DATA_DIR", tmp_path / "lessons")
    monkeypatch.setattr(rate_limit, "_calls", [])
    jobs._jobs.clear()


def wait_for_job(job_id: str, timeout: float = 5.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        body = client.get(f"/internal/jobs/{job_id}/status").json()
        if body["status"] != "running":
            return body
        time.sleep(0.02)
    raise AssertionError("job did not finish in time")


def start_curriculum_job() -> str:
    response = client.post(
        "/internal/curriculum",
        data={"topic": "Docker basics"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/internal/jobs/")
    return location.rsplit("/", 1)[1]


def test_curriculum_job_runs_in_background_and_links_to_result(monkeypatch):
    monkeypatch.setattr(
        internal,
        "generate_curriculum",
        lambda **kwargs: Curriculum.model_validate(FAKE_CURRICULUM),
    )

    job_id = start_curriculum_job()

    # The waiting page renders while (or after) the job runs.
    status = wait_for_job(job_id)
    assert status["status"] == "done"
    assert status["result_url"].startswith("/internal/curriculum/curriculum_")

    # The result has its own URL, so a refresh reloads it instead of
    # re-generating.
    page = client.get(status["result_url"])
    assert page.status_code == 200
    assert "Docker basics" in page.text

    # Revisiting the job page after it's done jumps straight to the result.
    revisit = client.get(f"/internal/jobs/{job_id}", follow_redirects=False)
    assert revisit.status_code == 303
    assert revisit.headers["location"] == status["result_url"]


def test_waiting_page_shows_timer_while_running(monkeypatch):
    release = jobs.threading.Event()

    def slow_generate(**kwargs):
        release.wait(timeout=5)
        return Curriculum.model_validate(FAKE_CURRICULUM)

    monkeypatch.setattr(internal, "generate_curriculum", slow_generate)

    job_id = start_curriculum_job()
    try:
        page = client.get(f"/internal/jobs/{job_id}")
        assert page.status_code == 200
        assert "Elapsed:" in page.text
        assert 'data-elapsed="' in page.text
    finally:
        release.set()
        wait_for_job(job_id)


def test_failed_job_reports_generic_error(monkeypatch):
    def broken_generate(**kwargs):
        raise RuntimeError("secret upstream details")

    monkeypatch.setattr(internal, "generate_curriculum", broken_generate)

    job_id = start_curriculum_job()
    status = wait_for_job(job_id)

    assert status["status"] == "failed"
    assert "secret upstream details" not in status["error"]

    page = client.get(f"/internal/jobs/{job_id}")
    assert "Generation failed" in page.text


def test_unknown_job_returns_404():
    assert client.get("/internal/jobs/nope/status").status_code == 404
    page = client.get("/internal/jobs/nope")
    assert page.status_code == 404
    assert "couldn't be found" in page.text


def test_validation_still_fails_fast_without_starting_a_job():
    response = client.post(
        "/internal/curriculum",
        data={"topic": "x" * (internal.MAX_TOPIC_LENGTH + 1)},
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert jobs._jobs == {}


def test_expired_jobs_are_removed(monkeypatch):
    old = jobs.Job(id="old", kind="curriculum", status=jobs.DONE)
    old.finished_at = time.time() - jobs.JOB_TTL_SECONDS - 1
    running = jobs.Job(id="still-running", kind="curriculum")
    jobs._jobs.update({"old": old, "still-running": running})

    with jobs._lock:
        jobs._remove_expired()

    assert "old" not in jobs._jobs
    # Running jobs are never removed, however old.
    assert "still-running" in jobs._jobs


def test_curriculum_view_rejects_path_traversal():
    response = client.get("/internal/curriculum/..%2Fsecrets.json")
    assert response.status_code in (400, 404)


def test_lesson_job_links_to_curriculum_with_lesson(monkeypatch, tmp_path):
    from app.models.lesson import PaginatedLesson

    curriculum = Curriculum.model_validate(FAKE_CURRICULUM)
    curriculum_path = internal.save_curriculum(
        curriculum=curriculum, topic="Docker basics", model="fake"
    )

    fake_lesson = PaginatedLesson.model_validate(
        {
            "node_id": "n1",
            "title": "Running your first container",
            "objective": "Run one.",
            "estimated_minutes": 5,
            "total_pages": 1,
            "plan": [],
            "pages": [
                {
                    "page_number": 1,
                    "title": "Page one",
                    "introduction": "Intro.",
                    "sections": [],
                    "example": "docker run hello-world",
                }
            ],
            "page_summaries": ["Summary."],
        }
    )
    monkeypatch.setattr(
        internal, "generate_paginated_lesson", lambda **kwargs: fake_lesson
    )

    response = client.post(
        "/internal/lesson",
        data={"curriculum_filename": curriculum_path.name, "node_id": "n1"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    job_id = response.headers["location"].rsplit("/", 1)[1]

    status = wait_for_job(job_id)
    assert status["status"] == "done"
    assert "lesson=lesson_" in status["result_url"]
    assert "node=n1" in status["result_url"]

    page = client.get(status["result_url"])
    assert page.status_code == 200
    assert "Running your first container" in page.text
