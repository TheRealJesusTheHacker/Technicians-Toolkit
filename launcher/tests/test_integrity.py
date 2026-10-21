"""The in-window bundle file check (roadmap M3, launcher 1.0.5).

The bundle ships SHA256SUMS.txt covering every file it contains;
the window's Check bundle files button re-proves those hashes on
demand. These tests pin the proof's honesty: listed files are
verified byte for byte, damage and disappearance are problems in
plain language, a sums file that points outside the folder is
never followed — and the files a working bundle gains on the job
(a tool's data folder, certificates) are counted, not condemned.
"""

import hashlib

from toolkit_launcher.integrity import SUMS_NAME, verify_bundle_files


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bundle(root, files, sums=None, extra_sums_lines=""):
    root.mkdir(parents=True, exist_ok=True)
    for rel, data in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    if sums is None:
        sums = "".join(f"{_digest(data)}  {rel}\n" for rel, data in files.items())
    (root / SUMS_NAME).write_text(sums + extra_sums_lines, encoding="utf-8")
    return root


def test_all_listed_files_verify(tmp_path):
    _bundle(tmp_path, {"Tool.exe": b"tool", "sub/x.dll": b"dll"})
    report = verify_bundle_files(tmp_path)
    assert report.ok
    assert report.checked == 2
    assert report.problems == []
    assert report.extra == 0


def test_changed_file_is_a_problem(tmp_path):
    _bundle(tmp_path, {"Tool.exe": b"tool"})
    (tmp_path / "Tool.exe").write_bytes(b"tampered")
    report = verify_bundle_files(tmp_path)
    assert not report.ok
    assert report.checked == 0
    assert any("has changed" in p and "Tool.exe" in p for p in report.problems)


def test_missing_listed_file_is_a_problem(tmp_path):
    _bundle(tmp_path, {"Tool.exe": b"tool", "Gone.exe": b"gone"})
    (tmp_path / "Gone.exe").unlink()
    report = verify_bundle_files(tmp_path)
    assert not report.ok
    assert report.checked == 1
    assert any("missing" in p and "Gone.exe" in p for p in report.problems)


def test_missing_sums_file_is_a_designed_answer(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    report = verify_bundle_files(tmp_path)
    assert not report.ok
    assert not report.sums_found
    assert any("missing" in p for p in report.problems)


def test_unlisted_files_are_counted_not_condemned(tmp_path):
    """A working bundle gains files: Argus's data folder, Beerus's
    certificates. The check proves the shipped files; the rest is
    information, or every used bundle would read as damaged."""
    _bundle(tmp_path, {"Tool.exe": b"tool"})
    data = tmp_path / "ArgusData" / "settings.json"
    data.parent.mkdir()
    data.write_bytes(b"{}")
    report = verify_bundle_files(tmp_path)
    assert report.ok
    assert report.extra == 1


def test_sums_line_pointing_outside_is_never_followed(tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_bytes(b"secret-ish")
    sums = f"{_digest(b'secret-ish')}  ../outside.txt\n"
    _bundle(tmp_path / "bundle", {"Tool.exe": b"tool"}, sums=sums)
    report = verify_bundle_files(tmp_path / "bundle")
    assert not report.ok
    assert report.checked == 0
    assert any("points outside" in p for p in report.problems)


def test_trailing_blank_lines_are_tolerated(tmp_path):
    _bundle(tmp_path, {"Tool.exe": b"tool"}, extra_sums_lines="\n\n")
    report = verify_bundle_files(tmp_path)
    assert report.ok
