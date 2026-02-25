#!/usr/bin/env python3
"""
s01_agent_loop.py - The Agent Loop

The entire secret of an AI coding agent in one pattern:

    while stop_reason == "tool_use":
        response = LLM(messages, tools)
        execute tools
        append results

    +----------+      +-------+      +---------+
    |   User   | ---> |  LLM  | ---> |  Tool   |
    |  prompt  |      |       |      | execute |
    +----------+      +---+---+      +----+----+
                          ^               |
                          |   tool_result |
                          +---------------+
                          (loop continues)

This is the core loop: feed tool results back to the model
until the model decides to stop. Production agents layer
policy, hooks, and lifecycle controls on top.
"""

import os
import subprocess

from anthropic import Anthropic
from dotenv import load_dotenv

#获取.env中的配置，使用的是minimax 2.5
load_dotenv(override=True)

if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]
#提示词，定义一个角色，并且是作用于当前项目根目录的
SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."
#bash工具
"""
工具名是 bash
功能是“执行 shell 命令”
入参必须是一个 JSON 对象
且必须包含 command（字符串）
"""
TOOLS = [{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    },
}]


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        """
        command：要执行的命令字符串。
        shell=True：通过 shell 执行命令（Windows 下一般走 cmd.exe）。
        cwd=os.getcwd()：把命令执行目录设为当前工作目录。
        capture_output=True：捕获标准输出和标准错误（不直接打印到终端）。
        text=True：输出按文本字符串处理（r.stdout/r.stderr 是 str，不是 bytes）。
        timeout=120：最多执行 120 秒，超时会抛 subprocess.TimeoutExpired。
        """
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


# -- The core pattern: a while loop that calls tools until the model stops --
def agent_loop(messages: list):
    while True:
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8000,
        )
        # Append assistant turn
        """
        [ThinkingBlock(signature='91f2418bc1a2f995b04ee0f98a1e0e30d959198d3650d9f6eb8701d60fad22e1', thinking='The user wants me to create a hello.txt file in the scripts directory with some content. Let me first check if the scripts directory exists, then create the file.', type='thinking'), ToolUseBlock(id='call_function_lj57r7wdstzp_1', caller=None, input={'command': 'ls -la scripts 2>/dev/null || mkdir scripts'}, name='bash', type='tool_use')]
        [ThinkingBlock(signature='7e2cea72a66791ca38c51a5c61cde9f04fd9da4671ebabc58eb0800e427b5d75', thinking="It seems the scripts directory doesn't exist or there's an issue. Let me check the current directory and create the scripts directory if needed.", type='thinking'), ToolUseBlock(id='call_function_6mo8qqzh8bcy_1', caller=None, input={'command': 'mkdir -p scripts && echo "Hello! This is a test file created in the scripts directory. Welcome to Claude Code!" > scripts/hello.txt'}, name='bash', type='tool_use')]
        [ThinkingBlock(signature='2e869ab9d19165101e90f7865f6071837387dc73d87e6eb283567c75db672f45', thinking='The directory exists now. Let me just create the file with content.', type='thinking'), ToolUseBlock(id='call_function_ugv44cnd33go_1', caller=None, input={'command': 'echo "Hello! This is a test file created in the scripts directory. Welcome to Claude Code!" > scripts/hello.txt'}, name='bash', type='tool_use')]
        [ThinkingBlock(signature='8f12e65b8176e7cc5b765b960231381808011794717dd6f2f158d9d9fb27baf4', thinking='The file was created. Let me verify its contents to confirm.', type='thinking'), ToolUseBlock(id='call_function_21pckn9o4drt_1', caller=None, input={'command': 'cat scripts/hello.txt'}, name='bash', type='tool_use')]
        [ThinkingBlock(signature='c2b6b17fb0bfa47cb189c2477edfd5e1552cf5e48ec30087ca6aba6bdef992d8', thinking='The cat command is not available in Windows. Let me try another way to verify.', type='thinking'), ToolUseBlock(id='call_function_m01n74qycwt4_1', caller=None, input={'command': 'type scripts\\hello.txt'}, name='bash', type='tool_use')]
        [ThinkingBlock(signature='89f76478a095c196b7a2a2ce58c065b58bea111940843241a43add1df1ebfbea', thinking='The file was created successfully with the content. Let me provide a summary to the user.', type='thinking'), TextBlock(citations=None, text='已成功在 `scripts` 目录下创建 `hello.txt` 文件，文件内容如下：\n\n```\nHello! This is a test file created in the scripts directory. Welcome to Claude Code!\n```', type='text')]
        """
        messages.append({"role": "assistant", "content": response.content})
        # If the model didn't call a tool, we're done
        if response.stop_reason != "tool_use":
            return
        # Execute each tool call, collect results
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\033[33m$ {block.input['command']}\033[0m")
                output = run_bash(block.input["command"])
                print(output[:200])
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": output})
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})#{'role': 'user', 'content': '在scripts目录下创建一个hello.txt文件，文件中的内容可以是你随意生成的一段内容'}
        agent_loop(history)
        response_content = history[-1]["content"]
        if isinstance(response_content, list):
            for block in response_content:
                if hasattr(block, "text"):
                    print(block.text)
        print()
