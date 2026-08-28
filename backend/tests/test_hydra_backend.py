import base64
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from hydra_backend import ValidationError, decode_audio, ingest_rss, process_turn, validate_turn


def test_mock_turn_contract():
    result = process_turn({"version": "hydra/v1", "message": "hello"})
    assert result["provider"] == "mock"
    assert result["response"]["audio_base64"] is None
    assert "request_id" in result["heartbeat"] or "request_id" in result


def test_schema_and_tool_validation():
    try:
        validate_turn({"version": "wrong", "message": "x"})
        assert False
    except ValidationError:
        pass


def test_base64_limits_and_decode():
    assert decode_audio(base64.b64encode(b"audio").decode()) == b"audio"
    try:
        decode_audio("not-base64")
        assert False
    except ValidationError:
        pass


def test_rss_sanitizes_and_deduplicates():
    feed = """<rss><channel><item><title>Hello &lt;b&gt;world&lt;/b&gt;</title>
    <description><![CDATA[<script>alert(1)</script> safe]]></description><link>https://x/1</link></item>
    <item><title>Hello world</title><description>other</description><link>https://x/1</link></item>
    </channel></rss>"""
    entries = ingest_rss(feed, "approved")
    assert len(entries) == 1
    assert "<" not in entries[0]["title"] + entries[0]["description"]
    assert entries[0]["source"] == "approved"
