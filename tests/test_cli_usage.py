"""CLI usage / unknown-subcommand I/O matrix."""

from __future__ import annotations

import pytest

from bmad_factory.cli.main import main


def test_unknown_subcommand_exits_60(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["not-a-command"])

    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert "error" in captured.err.lower() or "usage" in captured.err.lower()
