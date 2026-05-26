import pytest

from pyclaude.tools.file_write import FileWriteTool


@pytest.mark.asyncio
async def test_file_write_creates_parent_dirs(tmp_path):
    target = tmp_path / "nested" / "a.txt"
    result = await FileWriteTool().call({"file_path": str(target), "content": "hello"})
    assert result.is_error is False
    assert target.read_text(encoding="utf-8") == "hello"


def test_file_write_requires_permission():
    tool = FileWriteTool()
    assert tool.is_read_only({"file_path": "/tmp/a.txt", "content": "x"}) is False
    assert tool.needs_permission({"file_path": "/tmp/a.txt", "content": "x"}) is True
