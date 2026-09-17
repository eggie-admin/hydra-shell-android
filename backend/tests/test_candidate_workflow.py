import importlib
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

candidate = importlib.import_module("candidate_workflow")


def configure_tmp(monkeypatch, tmp_path):
    candidate._stages.clear()
    monkeypatch.setattr(candidate, "REPO_ROOT", tmp_path.resolve())
    monkeypatch.setattr(candidate, "STATE_ROOT", (tmp_path / ".state").resolve())
    return candidate.app.test_client()


def test_health_declares_no_shell(monkeypatch, tmp_path):
    client = configure_tmp(monkeypatch, tmp_path)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["human_approval_required"] is True
    assert body["shell_execution"] is False
    assert body["write_primitive"] == "utf8_file_replace_only"


def test_stage_then_explicit_approve_executes(monkeypatch, tmp_path):
    client = configure_tmp(monkeypatch, tmp_path)
    target = tmp_path / "project" / "hydra" / "doctrine" / "candidate.txt"
    target.parent.mkdir(parents=True)
    target.write_text("before\n", encoding="utf-8")

    staged = client.post(
        "/v1/mutations/stage",
        json={"path": "project/hydra/doctrine/candidate.txt", "content": "after\n"},
    )
    assert staged.status_code == 200
    mutation = staged.get_json()["mutation"]
    assert target.read_text(encoding="utf-8") == "before\n"

    blocked = client.post(
        f"/v1/mutations/{mutation['stage_id']}/execute",
        json={"confirm": "NOPE", "approval_token": mutation["approval_token"]},
    )
    assert blocked.status_code == 403
    assert target.read_text(encoding="utf-8") == "before\n"

    executed = client.post(
        f"/v1/mutations/{mutation['stage_id']}/execute",
        json={"confirm": "APPROVE", "approval_token": mutation["approval_token"]},
    )
    assert executed.status_code == 200
    body = executed.get_json()
    assert body["status"] == "EXECUTED_WITH_CHECKPOINT"
    assert body["human_approval_verified"] is True
    assert body["shell_execution"] is False
    assert target.read_text(encoding="utf-8") == "after\n"
    assert Path(body["checkpoint"]).joinpath("preimage.bin").read_bytes() == b"before\n"


def test_preimage_change_blocks_execution(monkeypatch, tmp_path):
    client = configure_tmp(monkeypatch, tmp_path)
    target = tmp_path / "safe.txt"
    target.write_text("one\n", encoding="utf-8")
    staged = client.post("/v1/mutations/stage", json={"path": "safe.txt", "content": "two\n"})
    mutation = staged.get_json()["mutation"]
    target.write_text("changed\n", encoding="utf-8")

    response = client.post(
        f"/v1/mutations/{mutation['stage_id']}/execute",
        json={"confirm": "APPROVE", "approval_token": mutation["approval_token"]},
    )
    assert response.status_code == 409
    assert response.get_json()["error"] == "preimage changed after staging"
    assert target.read_text(encoding="utf-8") == "changed\n"


def test_protected_paths_are_rejected(monkeypatch, tmp_path):
    client = configure_tmp(monkeypatch, tmp_path)
    for path in (".git/config", ".secrets/token", ".env", "../escape.txt"):
        response = client.post("/v1/mutations/stage", json={"path": path, "content": "x"})
        assert response.status_code == 400
