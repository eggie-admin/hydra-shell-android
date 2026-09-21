import importlib
import json
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
    assert body["proof_schema"] == "luhm-os.mutation-proof.v1"
    assert body["proof_renderers"] == ["json", "html", "chat_summary"]
    assert body["proof_contains_file_content"] is False
    assert body["proof_contains_approval_token"] is False


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
    assert "approval_token" in mutation
    assert target.read_text(encoding="utf-8") == "before\n"

    status = client.get(f"/v1/mutations/{mutation['stage_id']}")
    assert status.status_code == 200
    assert "approval_token" not in status.get_json()["mutation"]

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
    assert body["proof"]["schema"] == "luhm-os.mutation-proof.v1"
    assert body["proof"]["payload_sha256"]
    assert "LUHM_MUTATION_PROOF_V1" in body["proof"]["chat_summary"]
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


def test_proof_is_unavailable_before_execution(monkeypatch, tmp_path):
    client = configure_tmp(monkeypatch, tmp_path)
    staged = client.post("/v1/mutations/stage", json={"path": "proof.txt", "content": "candidate\n"})
    mutation = staged.get_json()["mutation"]
    assert client.get(f"/v1/mutations/{mutation['stage_id']}/proof.json").status_code == 404
    assert client.get(f"/v1/mutations/{mutation['stage_id']}/proof.html").status_code == 404


def test_html_json_and_chat_proofs_share_one_digest_and_exclude_sensitive_material(monkeypatch, tmp_path):
    client = configure_tmp(monkeypatch, tmp_path)
    target = tmp_path / "proof.txt"
    target.write_text("before\n", encoding="utf-8")
    staged = client.post(
        "/v1/mutations/stage",
        json={"path": "proof.txt", "content": "SENSITIVE-STAGED-CONTENT\n"},
    )
    mutation = staged.get_json()["mutation"]
    token = mutation["approval_token"]

    executed = client.post(
        f"/v1/mutations/{mutation['stage_id']}/execute",
        json={"confirm": "APPROVE", "approval_token": token},
    )
    assert executed.status_code == 200
    proof_meta = executed.get_json()["proof"]

    json_response = client.get(proof_meta["json_url"])
    assert json_response.status_code == 200
    assert json_response.headers["Cache-Control"] == "no-store"
    assert "attachment" in json_response.headers["Content-Disposition"]
    proof = json.loads(json_response.get_data(as_text=True))
    payload = proof["payload"]
    expected_digest = candidate.sha256_bytes(candidate.canonical_json_bytes(payload))
    assert proof["payload_sha256"] == expected_digest == proof_meta["payload_sha256"]
    assert proof["chat_summary"] == proof_meta["chat_summary"]
    assert payload["authority_grant"] == "NONE"
    assert payload["file_content_included"] is False
    assert payload["approval_token_included"] is False

    html_response = client.get(proof_meta["html_url"])
    assert html_response.status_code == 200
    assert html_response.headers["Cache-Control"] == "no-store"
    assert "default-src 'none'" in html_response.headers["Content-Security-Policy"]
    html_text = html_response.get_data(as_text=True)
    assert proof_meta["payload_sha256"] in html_text
    assert "LUHM_MUTATION_PROOF_V1" in html_text
    assert "authority_grant=none" in html_text

    all_proof_text = json_response.get_data(as_text=True) + html_text + proof_meta["chat_summary"]
    assert token not in all_proof_text
    assert "SENSITIVE-STAGED-CONTENT" not in all_proof_text
