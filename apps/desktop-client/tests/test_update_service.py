"""Auto-Update service (services.update_service).

Covers version comparison, manifest parsing, download integrity (SHA-256),
and the Windows update.bat bridge generation. HTTP is served by an httpx
MockTransport - no network needed.
"""

import hashlib

import httpx
import pytest

import services.update_service as update_service_module
from services.update_service import (
    UpdateArtifact,
    UpdateError,
    UpdateService,
    build_update_script,
    is_newer,
    parse_version,
    verify_sha256,
)


class _StubClient:
    """Giả lập ApiClient: chỉ cần `.get()` trả về httpx.Response."""

    def __init__(self, response: httpx.Response):
        self._response = response
        self.calls = []

    def get(self, endpoint, params=None):
        self.calls.append(endpoint)
        return self._response


def _client_factory(handler):
    real_client = httpx.Client  # captured before monkeypatch

    def factory(*args, **kwargs):
        kwargs.pop("transport", None)
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    return factory


# ------------------------------------------------------------------------------
# Version comparison
# ------------------------------------------------------------------------------
def test_parse_version_ignores_non_numeric_suffixes():
    assert parse_version("2.5.0") == (2, 5, 0)
    assert parse_version("v2.5.1") == (2, 5, 1)


def test_is_newer_normal_boundary_and_equal():
    assert is_newer("2.5.0", "2.4.9") is True
    assert is_newer("2.5.0", "2.5") is False       # 2.5.0 == 2.5 (zero-padded)
    assert is_newer("2.10.0", "2.9.0") is True      # numeric, not lexicographic
    assert is_newer("2.4.0", "2.5.0") is False


def test_is_newer_handles_garbage_input():
    assert is_newer("abc", "1.0.0") is False
    assert is_newer("3.0.0", "") is True


# ------------------------------------------------------------------------------
# Manifest parsing + check_for_update
# ------------------------------------------------------------------------------
def _manifest_response(latest: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "success": True,
            "message": "Lấy thông tin phiên bản thành công",
            "data": {
                "latest_version": latest,
                "min_supported_version": "2.0.0",
                "mandatory": False,
                "notes": "- Fix bug",
                "published_at": "2026-10-19T00:00:00Z",
                "platforms": {
                    "windows": {
                        "artifact_type": "zip",
                        "url": "https://github.com/aita/releases/download/v2.5.0/AITA.zip",
                        "sha256": "a" * 64,
                        "size_bytes": 1000,
                        "entrypoint": "AITA.exe",
                    }
                },
            },
        },
    )


def test_check_for_update_returns_info_when_newer():
    service = UpdateService(api_client=_StubClient(_manifest_response("2.6.0")), current_version="2.5.0")
    info = service.check_for_update()
    assert info is not None
    assert info.latest_version == "2.6.0"
    assert info.artifact.artifact_type == "zip"
    assert info.artifact.entrypoint == "AITA.exe"


def test_check_for_update_returns_none_when_up_to_date():
    service = UpdateService(api_client=_StubClient(_manifest_response("2.5.0")), current_version="2.5.0")
    assert service.check_for_update() is None


def test_check_for_update_returns_none_on_bad_status():
    service = UpdateService(api_client=_StubClient(httpx.Response(500)), current_version="2.5.0")
    assert service.check_for_update() is None


def test_check_for_update_swallows_network_errors():
    class _Boom:
        def get(self, endpoint, params=None):
            raise httpx.ConnectError("down")

    assert UpdateService(api_client=_Boom()).check_for_update() is None


# ------------------------------------------------------------------------------
# Download + checksum
# ------------------------------------------------------------------------------
def _artifact(payload: bytes, sha: str) -> UpdateArtifact:
    return UpdateArtifact("exe", "https://example.com/AITA.exe", sha, len(payload), "AITA.exe")


def test_download_verifies_sha256(monkeypatch, tmp_path):
    payload = b"hello-aita"
    sha = hashlib.sha256(payload).hexdigest()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=payload, headers={"Content-Length": str(len(payload))})

    monkeypatch.setattr(update_service_module.httpx, "Client", _client_factory(handler))
    path = UpdateService(api_client=object()).download(_artifact(payload, sha), tmp_path)
    assert path.read_bytes() == payload
    assert not list(tmp_path.glob("*.part"))


def test_download_rejects_checksum_mismatch(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"tampered")

    monkeypatch.setattr(update_service_module.httpx, "Client", _client_factory(handler))
    with pytest.raises(UpdateError):
        UpdateService(api_client=object()).download(_artifact(b"tampered", "deadbeef" * 8), tmp_path)
    assert not list(tmp_path.iterdir())  # no leftover .part / file


def test_download_rejects_insecure_url(tmp_path):
    artifact = UpdateArtifact("exe", "http://example.com/AITA.exe", "", 0, "AITA.exe")
    with pytest.raises(UpdateError):
        UpdateService(api_client=object()).download(artifact, tmp_path)


def test_verify_sha256_empty_expected_is_ok(tmp_path):
    target = tmp_path / "f.bin"
    target.write_bytes(b"x")
    assert verify_sha256(target, "") is True
    assert verify_sha256(target, "0" * 64) is False


# ------------------------------------------------------------------------------
# update.bat bridge
# ------------------------------------------------------------------------------
def test_build_update_script_for_exe_copies_and_relaunches():
    script = build_update_script(
        artifact_type="exe",
        install_dir=r"C:\AITA",
        exe_name="AITA.exe",
        pid=4242,
        artifact_path=r"C:\Temp\AITA.exe",
    )
    assert "PID eq %PID%" in script
    assert r'set "NEW=C:\Temp\AITA.exe"' in script
    assert r'set "TARGET=C:\AITA\AITA.exe"' in script
    assert 'copy /Y "%NEW%" "%TARGET%"' in script
    assert 'start "" "%TARGET%"' in script


def test_build_update_script_for_zip_preserves_user_data():
    script = build_update_script(
        artifact_type="zip",
        install_dir=r"C:\AITA",
        exe_name="AITA.exe",
        pid=4242,
        payload_dir=r"C:\Temp\payload",
    )
    assert r'set "SRC=C:\Temp\payload"' in script
    assert r'set "TARGET=C:\AITA"' in script
    assert r'set "TARGET_EXE=C:\AITA\AITA.exe"' in script
    assert 'robocopy "%SRC%" "%TARGET%"' in script
    assert "/XD data" in script
    assert "*.db" in script
    assert 'start "" "%TARGET_EXE%"' in script
