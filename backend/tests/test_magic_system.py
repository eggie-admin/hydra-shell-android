import pytest

from backend.magic_system import authorize_spell, compile_spell


def test_libra_is_read_only():
    plan = compile_spell("libra")
    assert plan.may_write_source is False
    assert plan.requires_human_approval is False


def test_cure_is_small_hotfix_and_not_release_promotion():
    plan = compile_spell("cure")
    assert plan.intent == "hotfix"
    assert plan.may_write_source is True
    assert plan.may_promote_release is False


def test_meteo_targets_testing_only():
    plan = compile_spell("meteo")
    assert plan.lane == "luhmos/testing"
    assert plan.may_promote_release is False


def test_curaga_requires_human_approval():
    blocked = authorize_spell("curaga", human_approved=False)
    assert blocked["ok"] is False
    assert "human_approval_required" in blocked["blocked_by"]


def test_ultima_is_compile_upload_install_not_release_promotion():
    plan = compile_spell("ultima")
    assert plan.intent == "compile-upload-install"
    assert plan.lane == "remote-forge-to-source-of-truth"
    assert plan.may_write_source is False
    assert plan.may_promote_release is False
    assert "Google Drive Source of Truth" in plan.action
    assert "Drive install link" in plan.action
    blocked = authorize_spell("ultima", human_approved=False, ci_green=True)
    assert blocked["ok"] is False
    approved = authorize_spell("ultima", human_approved=True, ci_green=True)
    assert approved["ok"] is True


def test_phoenix_never_guesses_rollback():
    plan = compile_spell("phoenix")
    assert plan.requires_human_approval is True
    assert "Never guess" in plan.action


def test_unknown_spell_fails_closed():
    with pytest.raises(ValueError):
        compile_spell("Zantetsuken")
