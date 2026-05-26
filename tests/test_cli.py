from pyclaude.cli import entrypoint, main


def test_main_returns_version_payload():
    assert main(["--version"]) == {"mode": "version", "version": "0.1.0"}


def test_entrypoint_returns_success_for_version(capsys):
    assert entrypoint(["--version"]) == 0
    captured = capsys.readouterr()
    assert "0.1.0" in captured.out
