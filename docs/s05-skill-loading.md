# s05: Skills (技能加载)

> 两层技能注入避免了系统提示膨胀: 在系统提示中放技能名称 (低成本), 在 tool_result 中按需放入完整技能内容。

## 问题

智能体需要针对不同领域遵循特定的工作流: git 约定、测试模式、代码审查清单。简单粗暴的做法是把所有内容都塞进系统提示。但系统提示的有效注意力是有限的 -- 文本太多, 模型就会开始忽略其中一部分。

如果你有 10 个技能, 每个 2000 token, 那就是 20,000 token 的系统提示。模型关注开头和结尾, 但会略过中间部分。更糟糕的是, 这些技能中大部分与当前任务无关。文件编辑任务不需要 git 工作流说明。

两层方案解决了这个问题: 第一层在系统提示中放入简短的技能描述 (每个技能约 100 token)。第二层只在模型调用 `load_skill` 时, 才将完整的技能内容加载到 tool_result 中。模型知道有哪些技能可用 (低成本), 按需加载它们 (只在相关时)。

## 解决方案

```
System prompt (Layer 1 -- always present):
+--------------------------------------+
| You are a coding agent.              |
| Skills available:                    |
|   - git: Git workflow helpers        |  ~100 tokens/skill
|   - test: Testing best practices     |
+--------------------------------------+

When model calls load_skill("git"):
+--------------------------------------+
| tool_result (Layer 2 -- on demand):  |
| <skill name="git">                   |
|   Full git workflow instructions...  |  ~2000 tokens
|   Step 1: ...                        |
|   Step 2: ...                        |
| </skill>                             |
+--------------------------------------+
```

## 工作原理

1. 技能文件以 Markdown 格式存放在 `.skills/` 目录中, 带有 YAML frontmatter。

```
.skills/
  git.md       # ---\n description: Git workflow\n ---\n ...
  test.md      # ---\n description: Testing patterns\n ---\n ...
```

2. SkillLoader 解析 frontmatter, 分离元数据和正文。

```python
class SkillLoader:
    def _parse_frontmatter(self, text: str) -> tuple:
        match = re.match(
            r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL
        )
        if not match:
            return {}, text
        meta = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta, match.group(2).strip()
```

3. 第一层: `get_descriptions()` 返回简短描述, 用于系统提示。

```python
def get_descriptions(self) -> str:
    lines = []
    for name, skill in self.skills.items():
        desc = skill["meta"].get("description", "No description")
        lines.append(f"  - {name}: {desc}")
    return "\n".join(lines)

SYSTEM = f"""You are a coding agent at {WORKDIR}.
Skills available:
{SKILL_LOADER.get_descriptions()}"""
```

4. 第二层: `get_content()` 返回用 `<skill>` 标签包裹的完整正文。

```python
def get_content(self, name: str) -> str:
    skill = self.skills.get(name)
    if not skill:
        return f"Error: Unknown skill '{name}'."
    return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"
```

5. `load_skill` 工具只是 dispatch map 中的又一个条目。

```python
TOOL_HANDLERS = {
    # ...base tools...
    "load_skill": lambda **kw: SKILL_LOADER.get_content(kw["name"]),
}
```

## 核心代码

SkillLoader 类 (来自 `agents/s05_skill_loading.py`, 第 51-97 行):

```python
class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills = {}
        for f in sorted(skills_dir.glob("*.md")):
            text = f.read_text()
            meta, body = self._parse_frontmatter(text)
            self.skills[f.stem] = {
                "meta": meta, "body": body
            }

    def get_descriptions(self) -> str:
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "")
            lines.append(f"  - {name}: {desc}")
        return "\n".join(lines)

    def get_content(self, name: str) -> str:
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Unknown skill '{name}'."
        return (f"<skill name=\"{name}\">\n"
                f"{skill['body']}\n</skill>")
```

## 相对 s04 的变更


| 组件     | 之前 (s04)      | 之后 (s05)               |
| -------- | --------------- | ------------------------ |
| Tools    | 5 (基础 + task) | 5 (基础 + load_skill)    |
| 系统提示 | 静态字符串      | + 技能描述列表           |
| 知识库   | 无              | .skills/*.md 文件        |
| 注入方式 | 无              | 两层 (系统提示 + result) |

## 设计原理

两层注入解决了注意力预算问题。将所有技能内容放入系统提示会在未使用的技能上浪费 token。第一层 (紧凑摘要) 总共约 120 token。第二层 (完整内容) 通过 tool_result 按需加载。这可以扩展到数十个技能而不降低模型注意力质量。关键洞察是: 模型只需要知道有哪些技能 (低成本) 就能决定何时加载某个技能 (高成本)。这与软件模块系统中的懒加载原则相同。

## 试一试

```sh
cd learn-claude-code
python agents/s05_skill_loading.py
```

可以尝试的提示:

1. `What skills are available?`
2. `Load the agent-builder skill and follow its instructions`
3. `I need to do a code review -- load the relevant skill first`
4. `Build an MCP server using the mcp-builder skill`

Message(id='0600ab4f58d721ffd49ed741cc7f420c', container=None, content=[ThinkingBlock(signature='90cb72bf3779d727df9c29be7882a1742aeca64733617d55cd15d32f92bf43e6', thinking='The user wants to do a code review and is asking me to load the relevant skill first. Based on the available skills, I should load the "code-review" skill.', type='thinking'), ToolUseBlock(id='call_function_zcnwejs1pp1f_1', caller=None, input={'name': 'code-review'}, name='load_skill', type='tool_use')], model='MiniMax-M2.5', role='assistant', stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=695, output_tokens=64, server_tool_use=None, service_tier=None), base_resp={'status_code': 0, 'status_msg': ''})

## Skill 与 Function Calling 的关系

`skill` 和 function calling 很像，但不是一回事。

- function calling / tool calling 解决的是“让模型可以做什么”，也就是给模型执行能力。
- skill 解决的是“让模型按什么方法做事”，也就是给模型流程、规范、偏好和领域策略。

在这个实现里，skill 是通过 `load_skill` 这个工具按需加载的，所以它的技术落点仍然是 tool calling：

```python
TOOL_HANDLERS = {
    "load_skill": lambda **kw: SKILL_LOADER.get_content(kw["name"]),
}
```

但从语义上看，两者分工不同：

- tool 是手，负责执行动作。
- skill 是操作手册，负责告诉模型应该如何组织这些动作。

最常见的组合方式是：

1. 模型先从系统提示里知道有哪些 skill 可用。
2. 需要某种领域策略时，调用 `load_skill(...)`。
3. 读完 skill 里的说明后，再去调用普通工具完成实际工作。

## Skills 主要解决什么问题

### 1. 控制系统提示的膨胀

如果把所有领域知识都直接塞进 system prompt，prompt 会很快变得又长又杂。skill 的两层注入方式把这个问题拆开：

- 第一层只在 system prompt 中放简短描述。
- 第二层只在真正需要时，才把完整 skill 正文通过 `tool_result` 注入上下文。

这样做的核心收益是：模型始终知道“有哪些能力说明书存在”，但不必永远背着所有说明书一起工作。

### 2. 解决“模型会用工具，但不会按预期流程用工具”的问题

很多任务不是缺工具，而是缺方法。例如：

- 代码评审需要先看风险，再看回归，再看测试缺口。
- 构建 MCP server 需要遵守特定结构和约束。
- PDF 处理往往有固定步骤和注意事项。

这些内容更像“工作流”和“检查清单”，而不是单个函数。skill 正适合承载这种信息。

### 3. 让领域知识和行为规范可复用

把这类流程写成独立 `SKILL.md` 后：

- 多个 agent 可以复用同一份规范。
- 修改某个领域流程时，不需要重写 agent 主循环。
- 知识和代码解耦，维护成本更低。

## Skills 的优点

- 模块化。不同领域规则可以拆成独立 skill 文件。
- 按需加载。比把所有说明都常驻在 system prompt 里更节省上下文。
- 可复用。多个 agent 可以共享同一套技能定义。
- 易维护。更新 skill 文件通常比改 agent 内部逻辑更简单。
- 灵活。适合承载流程、规范、偏好、检查清单这类“软逻辑”。

## Skills 的缺点

- 不是硬约束。skill 本质上仍然是 prompt 注入，模型可能不加载、误加载，或没有完全遵守。
- 依赖模型判断。模型要先决定“什么时候该加载哪个 skill”，这一步本身可能出错。
- 有额外 token 和轮次成本。需要先发现 skill，再调用 `load_skill`，再继续执行任务。
- skill 之间可能冲突。如果两个 skill 的规范不一致，模型会受到干扰。
- 不适合承载必须精确执行的逻辑。精确规则更应该落在真实代码和工具实现里。

## 什么时候用 Skill，什么时候用 Tool

可以用一个简单标准判断：

- 如果你要的是“执行一个确定动作”，用 tool。
- 如果你要的是“让模型按一套方法工作”，用 skill。

因此，skill 不是 function calling 的替代品，而是 function calling 之上的一层行为说明和领域策略。更准确地说：

- tool 定义 capability
- skill 定义 policy

一个成熟 agent 往往同时需要这两层。
