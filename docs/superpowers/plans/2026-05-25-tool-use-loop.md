# Python Claude Code Core Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python implementation of Claude Code that first runs a complete model/tool loop, then incrementally migrates the TypeScript `src` project into Python.

**Architecture:** The Python project mirrors the TypeScript architecture in layers: message model, tool interface, tool execution, tool orchestration, model adapter, query loop, and query engine. Short term implements a small runnable subset; medium term fills in Claude Code behavior; long term migrates the full TypeScript module surface.

**Tech Stack:** Python 3.11+, Anthropic SDK, pytest, pytest-asyncio. Use standard-library validation in the short term; introduce pydantic only when schema validation becomes complex enough to justify it.

---

## Migration North Star

The source of truth is `/Users/liuhaodong/rc-project/claude-code/src`.

Core TypeScript files to mirror first:

| TypeScript source | Python target | Purpose |
|---|---|---|
| `/Users/liuhaodong/rc-project/claude-code/src/types/message.ts` | `pyclaude/messages.py` | Message and content block types |
| `/Users/liuhaodong/rc-project/claude-code/src/Tool.ts` | `pyclaude/tools/base.py` | Tool contract |
| `/Users/liuhaodong/rc-project/claude-code/src/services/tools/toolExecution.ts` | `pyclaude/tool_execution.py` | Run one tool use |
| `/Users/liuhaodong/rc-project/claude-code/src/services/tools/toolOrchestration.ts` | `pyclaude/tool_orchestration.py` | Batch/concurrency orchestration |
| `/Users/liuhaodong/rc-project/claude-code/src/services/tools/StreamingToolExecutor.ts` | `pyclaude/tool_executor.py` | Streaming executor facade; short term can be non-streaming internally |
| `/Users/liuhaodong/rc-project/claude-code/src/query.ts` | `pyclaude/query_loop.py` | Model/tool loop |
| `/Users/liuhaodong/rc-project/claude-code/src/QueryEngine.ts` | `pyclaude/query_engine.py` | Session-facing query API |
| `/Users/liuhaodong/rc-project/claude-code/src/tools/FileReadTool/FileReadTool.ts` | `pyclaude/tools/file_read.py` | Read tool |
| `/Users/liuhaodong/rc-project/claude-code/src/tools/FileWriteTool/FileWriteTool.ts` | `pyclaude/tools/file_write.py` | Write tool |
| `/Users/liuhaodong/rc-project/claude-code/src/tools/BashTool/BashTool.tsx` | `pyclaude/tools/bash.py` | Bash tool |

## Long / Medium / Short Roadmap

### Short Term: Runnable Core

Deliverable: `uv run pyclaude "read README.md"` can call the model, execute `file_read`, return `tool_result`, call the model again, and print the final answer.

Scope:
- Message content blocks: text, tool_use, tool_result.
- Tool interface with TS-compatible names where practical.
- Tools: `file_read`, `file_write`, `bash`.
- Tool execution: input validation, missing-tool error, exception-to-tool-result.
- Tool orchestration: read-only tools may run concurrently; write/bash tools run serially.
- Query loop: model -> tool_use -> tool_result -> model until no tool_use.
- QueryEngine + CLI integration.

Out of scope for short term:
- Streaming tool execution.
- Background bash tasks.
- Sandbox override.
- MCP.
- Hooks.
- Compact/context collapse.
- TUI rendering.

### Medium Term: Usable Claude Code Subset

Deliverable: Python version supports common local coding sessions.

Scope:
- Streaming text deltas and tool-use detection.
- Permission rules for read/write/bash.
- File edit tool.
- Grep and Glob tools.
- TodoWrite tool.
- Better BashTool: timeout in milliseconds, description, interrupt behavior, background tasks.
- Tool progress events.
- Tool result storage for large outputs.
- Session transcript and history.
- Basic context loading from project instruction files.

### Long Term: Full TypeScript Migration

Deliverable: Python project reaches feature parity with the TypeScript `src` tree.

Migration order:
1. Query system: `query.ts`, `query/config.ts`, `query/deps.ts`, `query/transitions.ts`, `query/tokenBudget.ts`.
2. Tool system: `Tool.ts`, `tools.ts`, `services/tools/*`.
3. Core tools: Read, Write, Edit, Bash, Grep, Glob, TodoWrite.
4. Agent/task tools: Task, Agent, task lifecycle, background workers.
5. Context system: attachments, memory, CLAUDE.md loading, compact, file state cache.
6. CLI and interactive shell: commands, slash commands, rendering, user prompts.
7. Extensions: MCP, hooks, skills, plugins, LSP, web tools, notebook tools, remote/session features.

Each long-term module gets its own focused plan before implementation.

---

## Short-Term File Structure

### Modify

| File | New responsibility |
|---|---|
| `pyclaude/messages.py` | Content blocks, messages, stream events |
| `pyclaude/model_adapter.py` | Call Anthropic Messages API with tools and parse full assistant message |
| `pyclaude/query_deps.py` | Dependency injection for tests |
| `pyclaude/query_loop.py` | Core model/tool loop |
| `pyclaude/query_engine.py` | Session wrapper |
| `pyclaude/bootstrap.py` | CLI bootstrap |
| `pyclaude/tools/base.py` | Tool base contract |
| `pyclaude/tools/registry.py` | Default tool registry |

### Create

| File | Responsibility |
|---|---|
| `pyclaude/tool_execution.py` | Execute one `ToolUseBlock` |
| `pyclaude/tool_orchestration.py` | Execute tool-use batches |
| `pyclaude/tools/file_read.py` | `file_read` |
| `pyclaude/tools/file_write.py` | `file_write` |
| `pyclaude/tools/bash.py` | `bash` |
| `tests/conftest.py` | Fake model helpers |
| `tests/test_messages.py` | Message serialization |
| `tests/test_tools_base.py` | Tool base behavior |
| `tests/test_tools_file_read.py` | FileReadTool |
| `tests/test_tools_file_write.py` | FileWriteTool |
| `tests/test_tools_bash.py` | BashTool |
| `tests/test_tool_execution.py` | Single tool execution |
| `tests/test_tool_orchestration.py` | Tool batch behavior |
| `tests/test_query_loop.py` | Multi-turn model/tool loop |
| `tests/test_query_engine.py` | QueryEngine integration |

---

## Task 1: Message Model

**Files:**
- Modify: `pyclaude/messages.py`
- Test: `tests/test_messages.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_messages.py`:

```python
from pyclaude.messages import (
    AssistantMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)


def test_user_text_message_to_api_dict():
    msg = UserMessage.text("hello")
    assert msg.to_api_dict() == {"role": "user", "content": "hello"}


def test_assistant_tool_use_message_to_api_dict():
    msg = AssistantMessage(
        content=[
            TextBlock(text="Reading file."),
            ToolUseBlock(id="toolu_1", name="file_read", input={"file_path": "/tmp/a.txt"}),
        ],
        stop_reason="tool_use",
    )
    assert msg.tool_use_blocks[0].name == "file_read"
    assert msg.text == "Reading file."
    assert msg.to_api_dict()["content"][1] == {
        "type": "tool_use",
        "id": "toolu_1",
        "name": "file_read",
        "input": {"file_path": "/tmp/a.txt"},
    }


def test_tool_result_block_error_serialization():
    block = ToolResultBlock(tool_use_id="toolu_1", content="boom", is_error=True)
    assert block.to_api_dict() == {
        "type": "tool_result",
        "tool_use_id": "toolu_1",
        "content": "boom",
        "is_error": True,
    }


def test_user_tool_result_message_to_api_dict():
    msg = UserMessage.tool_results([
        ToolResultBlock(tool_use_id="toolu_1", content="ok"),
    ])
    assert msg.to_api_dict() == {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "toolu_1", "content": "ok"},
        ],
    }
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/test_messages.py -v`

Expected: FAIL because `TextBlock`, `ToolUseBlock`, `ToolResultBlock`, and new constructors do not exist.

- [ ] **Step 3: Implement message model**

Rewrite `pyclaude/messages.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class TextBlock:
    text: str
    type: str = field(default="text", init=False)

    def to_api_dict(self) -> dict[str, Any]:
        return {"type": "text", "text": self.text}


@dataclass(frozen=True)
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
    type: str = field(default="tool_use", init=False)

    def to_api_dict(self) -> dict[str, Any]:
        return {"type": "tool_use", "id": self.id, "name": self.name, "input": self.input}


@dataclass(frozen=True)
class ToolResultBlock:
    tool_use_id: str
    content: str
    is_error: bool = False
    type: str = field(default="tool_result", init=False)

    def to_api_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": "tool_result",
            "tool_use_id": self.tool_use_id,
            "content": self.content,
        }
        if self.is_error:
            result["is_error"] = True
        return result


ContentBlock = TextBlock | ToolUseBlock | ToolResultBlock


@dataclass(frozen=True)
class UserMessage:
    content: str | list[ToolResultBlock]
    role: Literal["user"] = field(default="user", init=False)

    @classmethod
    def text(cls, text: str) -> "UserMessage":
        return cls(content=text)

    @classmethod
    def tool_results(cls, results: list[ToolResultBlock]) -> "UserMessage":
        return cls(content=results)

    def to_api_dict(self) -> dict[str, Any]:
        if isinstance(self.content, str):
            return {"role": self.role, "content": self.content}
        return {"role": self.role, "content": [block.to_api_dict() for block in self.content]}


@dataclass(frozen=True)
class AssistantMessage:
    content: list[TextBlock | ToolUseBlock]
    stop_reason: str = "end_turn"
    role: Literal["assistant"] = field(default="assistant", init=False)

    @property
    def text(self) -> str:
        return "".join(block.text for block in self.content if isinstance(block, TextBlock))

    @property
    def tool_use_blocks(self) -> list[ToolUseBlock]:
        return [block for block in self.content if isinstance(block, ToolUseBlock)]

    def to_api_dict(self) -> dict[str, Any]:
        return {"role": self.role, "content": [block.to_api_dict() for block in self.content]}


Message = UserMessage | AssistantMessage


@dataclass(frozen=True)
class PartialEvent:
    content: str
    type: str = field(default="partial", init=False)


@dataclass(frozen=True)
class AssistantMessageEvent:
    message: AssistantMessage
    type: str = field(default="assistant_message", init=False)


@dataclass(frozen=True)
class ToolResultEvent:
    tool_use_id: str
    tool_name: str
    content: str
    is_error: bool
    type: str = field(default="tool_result", init=False)


@dataclass(frozen=True)
class AbortedEvent:
    type: str = field(default="aborted", init=False)
```

- [ ] **Step 4: Run test to verify pass**

Run: `uv run pytest tests/test_messages.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pyclaude/messages.py tests/test_messages.py
git commit -m "refactor: add content block message model"
```

---

## Task 2: Tool Base Contract

**Files:**
- Modify: `pyclaude/tools/base.py`
- Test: `tests/test_tools_base.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_tools_base.py`:

```python
import pytest

from pyclaude.tools.base import Tool, ToolResult


class EchoTool(Tool):
    name = "echo"
    description_text = "Echo input text."
    input_schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }

    async def call(self, input, context=None):
        return ToolResult(content=input["text"])

    def is_read_only(self, input=None):
        return True


@pytest.mark.asyncio
async def test_tool_call_returns_result():
    result = await EchoTool().call({"text": "hi"})
    assert result.content == "hi"
    assert result.is_error is False


def test_tool_api_definition():
    assert EchoTool().to_api_definition() == {
        "name": "echo",
        "description": "Echo input text.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    }


def test_default_concurrency_and_destructive_flags():
    tool = EchoTool()
    assert tool.is_concurrency_safe({"text": "hi"}) is True
    assert tool.is_destructive({"text": "hi"}) is False
    assert tool.needs_permission({"text": "hi"}) is False
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/test_tools_base.py -v`

Expected: FAIL because the current base contract is incomplete.

- [ ] **Step 3: Implement Tool base**

Rewrite `pyclaude/tools/base.py` with:

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    content: str
    is_error: bool = False


class Tool(ABC):
    name: str
    description_text: str
    input_schema: dict[str, Any]

    @abstractmethod
    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        pass

    def description(self, input: dict[str, Any] | None = None) -> str:
        return self.description_text

    @abstractmethod
    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        pass

    def is_concurrency_safe(self, input: dict[str, Any] | None = None) -> bool:
        return self.is_read_only(input)

    def is_destructive(self, input: dict[str, Any] | None = None) -> bool:
        return False

    def interrupt_behavior(self) -> str:
        return "block"

    def needs_permission(self, input: dict[str, Any] | None = None) -> bool:
        return not self.is_read_only(input)

    def validate_input(self, input: dict[str, Any]) -> None:
        required = self.input_schema.get("required", [])
        for key in required:
            if key not in input:
                raise ValueError(f"Missing required input: {key}")

    def to_api_definition(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description_text,
            "input_schema": self.input_schema,
        }
```

- [ ] **Step 4: Run test to verify pass**

Run: `uv run pytest tests/test_tools_base.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pyclaude/tools/base.py tests/test_tools_base.py
git commit -m "refactor: align Tool base with TypeScript core contract"
```

---

## Task 3: Core Tools

**Files:**
- Create: `pyclaude/tools/file_read.py`
- Create: `pyclaude/tools/file_write.py`
- Create: `pyclaude/tools/bash.py`
- Modify: `pyclaude/tools/registry.py`
- Test: `tests/test_tools_file_read.py`
- Test: `tests/test_tools_file_write.py`
- Test: `tests/test_tools_bash.py`

- [ ] **Step 1: Write failing FileReadTool tests**

Create `tests/test_tools_file_read.py`:

```python
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
```

- [ ] **Step 2: Write failing FileWriteTool tests**

Create `tests/test_tools_file_write.py`:

```python
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
```

- [ ] **Step 3: Write failing BashTool tests**

Create `tests/test_tools_bash.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify failure**

Run: `uv run pytest tests/test_tools_file_read.py tests/test_tools_file_write.py tests/test_tools_bash.py -v`

Expected: FAIL because the tool modules do not exist.

- [ ] **Step 5: Implement FileReadTool**

Create `pyclaude/tools/file_read.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from pyclaude.tools.base import Tool, ToolResult


class FileReadTool(Tool):
    name = "file_read"
    description_text = "Read a file from the local filesystem."
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "The absolute path to the file to read"},
            "offset": {"type": "integer", "description": "The 1-based line number to start reading from"},
            "limit": {"type": "integer", "description": "The number of lines to read"},
            "pages": {"type": "string", "description": "Page range for PDF files; accepted but not used in the short-term text reader"},
        },
        "required": ["file_path"],
    }

    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        self.validate_input(input)
        file_path = Path(input["file_path"]).expanduser()
        if not file_path.exists():
            return ToolResult(content=f"File not found: {file_path}", is_error=True)
        if file_path.is_dir():
            return ToolResult(content=f"Path is a directory: {file_path}", is_error=True)
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return ToolResult(content=f"Error reading file: {exc}", is_error=True)

        offset = input.get("offset", 1)
        limit = input.get("limit")
        start = max(0, int(offset) - 1)
        selected = lines[start:] if limit is None else lines[start : start + int(limit)]
        return ToolResult(content="\n".join(f"{i}|{line}" for i, line in enumerate(selected, start=start + 1)))

    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        return True
```

- [ ] **Step 6: Implement FileWriteTool**

Create `pyclaude/tools/file_write.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from pyclaude.tools.base import Tool, ToolResult


class FileWriteTool(Tool):
    name = "file_write"
    description_text = "Write content to a local file."
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "The absolute path to the file to write"},
            "content": {"type": "string", "description": "The content to write to the file"},
        },
        "required": ["file_path", "content"],
    }

    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        self.validate_input(input)
        file_path = Path(input["file_path"]).expanduser()
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(input["content"], encoding="utf-8")
        except OSError as exc:
            return ToolResult(content=f"Error writing file: {exc}", is_error=True)
        return ToolResult(content=f"Successfully wrote {file_path}")

    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        return False

    def is_destructive(self, input: dict[str, Any] | None = None) -> bool:
        return True
```

- [ ] **Step 7: Implement BashTool**

Create `pyclaude/tools/bash.py`:

```python
from __future__ import annotations

import asyncio
from typing import Any

from pyclaude.tools.base import Tool, ToolResult


class BashTool(Tool):
    name = "bash"
    description_text = "Run a shell command."
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The command to execute"},
            "timeout": {"type": "integer", "description": "Optional timeout in seconds"},
            "description": {"type": "string", "description": "Short description of what this command does"},
            "run_in_background": {"type": "boolean", "description": "Accepted for TS compatibility; foreground execution in short term"},
            "dangerouslyDisableSandbox": {"type": "boolean", "description": "Accepted for TS compatibility; ignored in short term"},
        },
        "required": ["command"],
    }

    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        self.validate_input(input)
        timeout = int(input.get("timeout", 120))
        proc = await asyncio.create_subprocess_shell(
            input["command"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return ToolResult(content=f"Timeout: command exceeded {timeout}s", is_error=True)

        output_parts = []
        if stdout:
            output_parts.append(stdout.decode("utf-8", errors="replace"))
        if stderr:
            output_parts.append("STDERR:\n" + stderr.decode("utf-8", errors="replace"))
        if proc.returncode:
            output_parts.append(f"Exit code: {proc.returncode}")
        return ToolResult(content="\n".join(output_parts) or "(no output)", is_error=proc.returncode != 0)

    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        return False

    def interrupt_behavior(self) -> str:
        return "cancel"
```

- [ ] **Step 8: Register default tools**

Rewrite `pyclaude/tools/registry.py`:

```python
from __future__ import annotations

from pyclaude.tools.base import Tool
from pyclaude.tools.bash import BashTool
from pyclaude.tools.file_read import FileReadTool
from pyclaude.tools.file_write import FileWriteTool


def get_default_tools() -> dict[str, Tool]:
    tools: list[Tool] = [FileReadTool(), FileWriteTool(), BashTool()]
    return {tool.name: tool for tool in tools}
```

- [ ] **Step 9: Run tests to verify pass**

Run: `uv run pytest tests/test_tools_file_read.py tests/test_tools_file_write.py tests/test_tools_bash.py -v`

Expected: all tests PASS.

- [ ] **Step 10: Commit**

```bash
git add pyclaude/tools/base.py pyclaude/tools/registry.py pyclaude/tools/file_read.py pyclaude/tools/file_write.py pyclaude/tools/bash.py tests/test_tools_file_read.py tests/test_tools_file_write.py tests/test_tools_bash.py
git commit -m "feat: add core read write bash tools"
```

---

## Task 4: Tool Execution and Orchestration

**Files:**
- Create: `pyclaude/tool_execution.py`
- Create: `pyclaude/tool_orchestration.py`
- Modify: `pyclaude/tool_executor.py`
- Test: `tests/test_tool_execution.py`
- Test: `tests/test_tool_orchestration.py`

- [ ] **Step 1: Write failing execution tests**

Create `tests/test_tool_execution.py`:

```python
import pytest

from pyclaude.messages import ToolUseBlock
from pyclaude.tool_execution import run_tool_use
from pyclaude.tools.base import Tool, ToolResult


class EchoTool(Tool):
    name = "echo"
    description_text = "Echo."
    input_schema = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}

    async def call(self, input, context=None):
        return ToolResult(content=input["text"])

    def is_read_only(self, input=None):
        return True


@pytest.mark.asyncio
async def test_run_tool_use_success():
    block = ToolUseBlock(id="toolu_1", name="echo", input={"text": "hi"})
    result = await run_tool_use(block, {"echo": EchoTool()})
    assert result.tool_use_id == "toolu_1"
    assert result.content == "hi"
    assert result.is_error is False


@pytest.mark.asyncio
async def test_run_tool_use_missing_tool():
    block = ToolUseBlock(id="toolu_1", name="missing", input={})
    result = await run_tool_use(block, {})
    assert result.is_error is True
    assert "No such tool" in result.content
```

- [ ] **Step 2: Write failing orchestration tests**

Create `tests/test_tool_orchestration.py`:

```python
import pytest

from pyclaude.messages import ToolUseBlock
from pyclaude.tool_orchestration import run_tools
from pyclaude.tools.base import Tool, ToolResult


class ReadTool(Tool):
    name = "read"
    description_text = "Read."
    input_schema = {"type": "object", "properties": {}, "required": []}

    async def call(self, input, context=None):
        return ToolResult(content="read")

    def is_read_only(self, input=None):
        return True


class WriteTool(Tool):
    name = "write"
    description_text = "Write."
    input_schema = {"type": "object", "properties": {}, "required": []}

    async def call(self, input, context=None):
        return ToolResult(content="write")

    def is_read_only(self, input=None):
        return False


@pytest.mark.asyncio
async def test_run_tools_returns_results_in_tool_use_order():
    blocks = [
        ToolUseBlock(id="toolu_1", name="read", input={}),
        ToolUseBlock(id="toolu_2", name="write", input={}),
    ]
    results = await run_tools(blocks, {"read": ReadTool(), "write": WriteTool()})
    assert [result.tool_use_id for result in results] == ["toolu_1", "toolu_2"]
    assert [result.content for result in results] == ["read", "write"]
```

- [ ] **Step 3: Run tests to verify failure**

Run: `uv run pytest tests/test_tool_execution.py tests/test_tool_orchestration.py -v`

Expected: FAIL because modules do not exist.

- [ ] **Step 4: Implement single tool execution**

Create `pyclaude/tool_execution.py`:

```python
from __future__ import annotations

from pyclaude.messages import ToolResultBlock, ToolUseBlock
from pyclaude.tools.base import Tool


async def run_tool_use(
    tool_use: ToolUseBlock,
    tools: dict[str, Tool],
    context: object | None = None,
) -> ToolResultBlock:
    tool = tools.get(tool_use.name)
    if tool is None:
        return ToolResultBlock(
            tool_use_id=tool_use.id,
            content=f"No such tool available: {tool_use.name}",
            is_error=True,
        )
    try:
        tool.validate_input(tool_use.input)
        result = await tool.call(tool_use.input, context=context)
    except Exception as exc:
        return ToolResultBlock(tool_use_id=tool_use.id, content=f"Tool error: {exc}", is_error=True)
    return ToolResultBlock(tool_use_id=tool_use.id, content=result.content, is_error=result.is_error)
```

- [ ] **Step 5: Implement orchestration**

Create `pyclaude/tool_orchestration.py`:

```python
from __future__ import annotations

import asyncio

from pyclaude.messages import ToolResultBlock, ToolUseBlock
from pyclaude.tool_execution import run_tool_use
from pyclaude.tools.base import Tool


def _is_concurrency_safe(tool_use: ToolUseBlock, tools: dict[str, Tool]) -> bool:
    tool = tools.get(tool_use.name)
    if tool is None:
        return True
    try:
        return tool.is_concurrency_safe(tool_use.input)
    except Exception:
        return False


async def run_tools(
    tool_uses: list[ToolUseBlock],
    tools: dict[str, Tool],
    context: object | None = None,
) -> list[ToolResultBlock]:
    results: list[ToolResultBlock] = []
    batch: list[ToolUseBlock] = []

    async def flush_batch() -> None:
        nonlocal batch
        if not batch:
            return
        batch_results = await asyncio.gather(*(run_tool_use(block, tools, context=context) for block in batch))
        results.extend(batch_results)
        batch = []

    for tool_use in tool_uses:
        if _is_concurrency_safe(tool_use, tools):
            batch.append(tool_use)
            continue
        await flush_batch()
        results.append(await run_tool_use(tool_use, tools, context=context))
    await flush_batch()
    return results
```

- [ ] **Step 6: Keep tool_executor facade**

Rewrite `pyclaude/tool_executor.py`:

```python
from __future__ import annotations

from pyclaude.messages import ToolResultBlock, ToolUseBlock
from pyclaude.tool_orchestration import run_tools
from pyclaude.tools.base import Tool


class ToolExecutor:
    def __init__(self, tools: dict[str, Tool]) -> None:
        self.tools = tools

    async def execute(self, tool_uses: list[ToolUseBlock], context: object | None = None) -> list[ToolResultBlock]:
        return await run_tools(tool_uses, self.tools, context=context)
```

- [ ] **Step 7: Run tests to verify pass**

Run: `uv run pytest tests/test_tool_execution.py tests/test_tool_orchestration.py -v`

Expected: all tests PASS.

- [ ] **Step 8: Commit**

```bash
git add pyclaude/tool_execution.py pyclaude/tool_orchestration.py pyclaude/tool_executor.py tests/test_tool_execution.py tests/test_tool_orchestration.py
git commit -m "feat: add tool execution and orchestration layers"
```

---

## Task 5: Model Adapter and Query Loop

**Files:**
- Modify: `pyclaude/model_adapter.py`
- Modify: `pyclaude/query_deps.py`
- Modify: `pyclaude/query_loop.py`
- Test: `tests/conftest.py`
- Test: `tests/test_query_loop.py`

- [ ] **Step 1: Add fake model helpers**

Create `tests/conftest.py`:

```python
import pytest

from pyclaude.messages import AssistantMessage, TextBlock, ToolUseBlock


def assistant_text(text: str) -> AssistantMessage:
    return AssistantMessage(content=[TextBlock(text=text)], stop_reason="end_turn")


def assistant_tool_use(tool_name: str, input: dict, tool_use_id: str = "toolu_1", text: str = "") -> AssistantMessage:
    content = []
    if text:
        content.append(TextBlock(text=text))
    content.append(ToolUseBlock(id=tool_use_id, name=tool_name, input=input))
    return AssistantMessage(content=content, stop_reason="tool_use")


class FakeModel:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses[len(self.calls) - 1]


@pytest.fixture
def assistant_text_factory():
    return assistant_text


@pytest.fixture
def assistant_tool_use_factory():
    return assistant_tool_use


@pytest.fixture
def fake_model_class():
    return FakeModel
```

- [ ] **Step 2: Write failing query loop tests**

Create `tests/test_query_loop.py`:

```python
import pytest

from pyclaude.app_state import AppState
from pyclaude.messages import AssistantMessageEvent, ToolResultEvent
from pyclaude.query_deps import QueryDeps
from pyclaude.query_loop import query
from pyclaude.tools.base import Tool, ToolResult


class EchoTool(Tool):
    name = "echo"
    description_text = "Echo."
    input_schema = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}

    async def call(self, input, context=None):
        return ToolResult(content=input["text"])

    def is_read_only(self, input=None):
        return True


@pytest.mark.asyncio
async def test_query_loop_executes_tool_and_calls_model_again(
    assistant_tool_use_factory,
    assistant_text_factory,
    fake_model_class,
):
    model = fake_model_class([
        assistant_tool_use_factory("echo", {"text": "hello"}, tool_use_id="toolu_1"),
        assistant_text_factory("done"),
    ])
    events = []
    async for event in query(
        prompt="say hello",
        state=AppState(),
        tools={"echo": EchoTool()},
        deps=QueryDeps(call_model=model),
    ):
        events.append(event)

    assert len(model.calls) == 2
    assert any(isinstance(event, ToolResultEvent) and event.content == "hello" for event in events)
    assert isinstance(events[-1], AssistantMessageEvent)
    assert events[-1].message.text == "done"
    second_call_messages = model.calls[1]["messages"]
    assert second_call_messages[-1]["content"][0]["type"] == "tool_result"
```

- [ ] **Step 3: Run test to verify failure**

Run: `uv run pytest tests/test_query_loop.py -v`

Expected: FAIL because the current loop streams plain text and does not execute tools.

- [ ] **Step 4: Implement model adapter**

Rewrite `pyclaude/model_adapter.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from anthropic import AsyncAnthropic

from pyclaude.messages import AssistantMessage, TextBlock, ToolUseBlock
from pyclaude.tools.base import Tool

DEFAULT_MODEL = "claude-opus-4-6"
DEFAULT_MAX_TOKENS = 64000


@dataclass(frozen=True)
class ModelConfig:
    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS


def parse_api_response(raw: Any) -> AssistantMessage:
    content = []
    for block in raw.content:
        if block.type == "text":
            content.append(TextBlock(text=block.text))
        elif block.type == "tool_use":
            content.append(ToolUseBlock(id=block.id, name=block.name, input=block.input))
    return AssistantMessage(content=content, stop_reason=getattr(raw, "stop_reason", "end_turn") or "end_turn")


async def call_model(
    *,
    messages: list[dict[str, Any]],
    tools: dict[str, Tool],
    config: ModelConfig | None = None,
) -> AssistantMessage:
    cfg = config or ModelConfig()
    client = AsyncAnthropic()
    kwargs: dict[str, Any] = {
        "model": cfg.model,
        "max_tokens": cfg.max_tokens,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = [tool.to_api_definition() for tool in tools.values()]
    response = await client.messages.create(**kwargs)
    return parse_api_response(response)
```

- [ ] **Step 5: Implement query deps**

Rewrite `pyclaude/query_deps.py`:

```python
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pyclaude.messages import AssistantMessage


@dataclass(frozen=True)
class QueryDeps:
    call_model: Callable[..., Awaitable[AssistantMessage]]


def production_deps() -> QueryDeps:
    from pyclaude.model_adapter import call_model

    return QueryDeps(call_model=call_model)
```

- [ ] **Step 6: Implement query loop**

Rewrite `pyclaude/query_loop.py`:

```python
from __future__ import annotations

from collections.abc import AsyncIterator

from pyclaude.app_state import AppState
from pyclaude.messages import AssistantMessageEvent, ToolResultEvent, UserMessage
from pyclaude.query_deps import QueryDeps, production_deps
from pyclaude.tool_executor import ToolExecutor
from pyclaude.tools.base import Tool


async def query(
    *,
    prompt: str,
    state: AppState,
    tools: dict[str, Tool],
    deps: QueryDeps | None = None,
) -> AsyncIterator[object]:
    resolved_deps = deps or production_deps()
    executor = ToolExecutor(tools)

    state.messages.append(UserMessage.text(prompt))

    while not state.aborted:
        api_messages = [message.to_api_dict() for message in state.messages]
        assistant_message = await resolved_deps.call_model(messages=api_messages, tools=tools)
        state.messages.append(assistant_message)
        yield AssistantMessageEvent(message=assistant_message)

        tool_uses = assistant_message.tool_use_blocks
        if not tool_uses:
            return

        tool_results = await executor.execute(tool_uses)
        for tool_use, result in zip(tool_uses, tool_results, strict=True):
            yield ToolResultEvent(
                tool_use_id=result.tool_use_id,
                tool_name=tool_use.name,
                content=result.content,
                is_error=result.is_error,
            )
        state.messages.append(UserMessage.tool_results(tool_results))
```

- [ ] **Step 7: Run query loop tests**

Run: `uv run pytest tests/test_query_loop.py -v`

Expected: all tests PASS.

- [ ] **Step 8: Commit**

```bash
git add pyclaude/model_adapter.py pyclaude/query_deps.py pyclaude/query_loop.py tests/conftest.py tests/test_query_loop.py
git commit -m "feat: implement core model tool query loop"
```

---

## Task 6: QueryEngine and CLI Bootstrap

**Files:**
- Modify: `pyclaude/app_state.py`
- Modify: `pyclaude/query_engine.py`
- Modify: `pyclaude/bootstrap.py`
- Test: `tests/test_query_engine.py`

- [ ] **Step 1: Write failing QueryEngine test**

Create `tests/test_query_engine.py`:

```python
import pytest

from pyclaude.query_deps import QueryDeps
from pyclaude.query_engine import QueryEngine
from pyclaude.tools.base import Tool, ToolResult


class EchoTool(Tool):
    name = "echo"
    description_text = "Echo."
    input_schema = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}

    async def call(self, input, context=None):
        return ToolResult(content=input["text"])

    def is_read_only(self, input=None):
        return True


@pytest.mark.asyncio
async def test_query_engine_returns_events(
    assistant_tool_use_factory,
    assistant_text_factory,
    fake_model_class,
):
    model = fake_model_class([
        assistant_tool_use_factory("echo", {"text": "hi"}),
        assistant_text_factory("done"),
    ])
    engine = QueryEngine(tools={"echo": EchoTool()}, deps=QueryDeps(call_model=model))
    events = await engine.submit_message("run")
    assert events[-1].message.text == "done"
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/test_query_engine.py -v`

Expected: FAIL because `QueryEngine` does not accept deps and current state type is old.

- [ ] **Step 3: Implement AppState**

Rewrite `pyclaude/app_state.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field

from pyclaude.messages import Message


@dataclass
class AppState:
    messages: list[Message] = field(default_factory=list)
    aborted: bool = False
```

- [ ] **Step 4: Implement QueryEngine**

Rewrite `pyclaude/query_engine.py`:

```python
from __future__ import annotations

from pyclaude.app_state import AppState
from pyclaude.messages import AbortedEvent
from pyclaude.query_deps import QueryDeps
from pyclaude.query_loop import query
from pyclaude.tools.base import Tool


class QueryEngine:
    def __init__(
        self,
        *,
        tools: dict[str, Tool],
        state: AppState | None = None,
        deps: QueryDeps | None = None,
    ) -> None:
        self.tools = tools
        self.state = state or AppState()
        self.deps = deps

    def abort(self) -> None:
        self.state.aborted = True

    async def submit_message(self, prompt: str) -> list[object]:
        if self.state.aborted:
            return [AbortedEvent()]
        events: list[object] = []
        async for event in query(prompt=prompt, state=self.state, tools=self.tools, deps=self.deps):
            events.append(event)
        return events
```

- [ ] **Step 5: Implement bootstrap**

Rewrite `pyclaude/bootstrap.py`:

```python
from __future__ import annotations

import asyncio

from pyclaude.messages import AssistantMessageEvent, ToolResultEvent
from pyclaude.query_engine import QueryEngine
from pyclaude.tools.registry import get_default_tools


def run_cli(args, extra_tools: dict | None = None) -> dict:
    prompt = args.prompt or ""
    if not prompt:
        return {"mode": "repl", "message": "Interactive mode not yet implemented."}

    tools = get_default_tools()
    if extra_tools:
        tools.update(extra_tools)

    engine = QueryEngine(tools=tools)
    events = asyncio.run(engine.submit_message(prompt))
    output = []
    for event in events:
        if isinstance(event, AssistantMessageEvent) and event.message.text:
            output.append(event.message.text)
        elif isinstance(event, ToolResultEvent):
            output.append(f"[{event.tool_name}] {event.content}")
    return {"mode": "prompt", "prompt": prompt, "events": events, "output": "\n".join(output)}
```

- [ ] **Step 6: Run tests**

Run: `uv run pytest tests/test_query_engine.py tests/test_query_loop.py -v`

Expected: all tests PASS.

- [ ] **Step 7: Run full short-term test suite**

Run: `uv run pytest tests/ -v`

Expected: all tests PASS.

- [ ] **Step 8: Verify CLI starts**

Run: `uv run pyclaude --version`

Expected: command exits successfully and prints the package version or CLI help/version text.

- [ ] **Step 9: Commit**

```bash
git add pyclaude/app_state.py pyclaude/query_engine.py pyclaude/bootstrap.py tests/test_query_engine.py
git commit -m "feat: wire query engine and cli bootstrap"
```

---

## Short-Term Acceptance Criteria

- `uv run pytest tests/ -v` passes.
- `uv run pyclaude --version` starts without import errors.
- Query loop test proves the second model call receives a `tool_result`.
- Tool schemas use TypeScript-compatible names: `file_path`, `command`, `timeout`, `description`, `run_in_background`, `dangerouslyDisableSandbox`.
- `pyclaude/tool_executor.py` remains as the executor facade for future `StreamingToolExecutor` migration.

## Medium-Term Backlog

Implement these as separate plans after the runnable core lands:

1. Streaming response and streaming tool-use parsing.
2. Permission modes and allow/deny rules.
3. FileEditTool, GrepTool, GlobTool, TodoWriteTool.
4. Bash background task lifecycle.
5. Tool progress messages and interrupt handling.
6. Tool result storage for large outputs.
7. Context loading from project instruction files.
8. Session transcript and history.
9. Compact/token budget.
10. Interactive CLI commands.

## Long-Term Backlog

Each item receives its own migration plan:

1. Full query system parity.
2. Full Tool interface parity.
3. All tools in `/Users/liuhaodong/rc-project/claude-code/src/tools`.
4. Agent/task execution.
5. MCP.
6. Hooks.
7. Skills and plugins.
8. LSP.
9. Web tools.
10. Notebook tools.
11. Remote/session/team features.
12. TUI rendering.

## Self-Review

- Spec coverage: short term covers runnable model/tool loop; medium and long term cover progressive TS migration.
- Placeholder scan: no unresolved placeholder tokens are used.
- Type consistency: all file tool inputs use `file_path`; tool result events use `content`; query loop and executor both use `ToolUseBlock` and `ToolResultBlock`.
- Architecture consistency: `tool_executor.py` is retained as the Python facade matching the TypeScript executor path.
