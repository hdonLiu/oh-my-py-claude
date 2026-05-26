import pytest

from pyclaude.tools.bash import BashTool


@pytest.mark.asyncio
async def test_bash_runs_command():
    result = await BashTool().call({"command": "echo hello"})
    assert result.is_error is False
    assert "hello" in result.content


@pytest.mark.asyncio
async def test_bash_nonzero_exit_is_error():
    result = await BashTool().call({"command": "exit 7"})
    assert result.is_error is True
    assert "Exit code: 7" in result.content


def test_bash_is_not_read_only():
    assert BashTool().is_read_only({"command": "echo hi"}) is False
