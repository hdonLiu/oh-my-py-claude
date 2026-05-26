import pytest

from pyclaude.tools.file_read import FileReadTool


@pytest.mark.asyncio
async def test_file_read_reads_lines_with_offset_and_limit(tmp_path):
    target = tmp_path / "a.txt"
    target.write_text("one\ntwo\nthree\n", encoding="utf-8")
    result = await FileReadTool().call({"file_path": str(target), "offset": 2, "limit": 1})
    assert result.is_error is False
    assert result.content == "2|two"


@pytest.mark.asyncio
async def test_file_read_missing_file_returns_tool_error():
    result = await FileReadTool().call({"file_path": "/no/such/file.txt"})
    assert result.is_error is True
    assert "File not found" in result.content


def test_file_read_schema_uses_ts_file_path_name():
    schema = FileReadTool().input_schema
    assert "file_path" in schema["properties"]
    assert schema["required"] == ["file_path"]
