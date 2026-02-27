# s03: TodoWrite (待办写入)

> TodoManager 让智能体能追踪自己的进度, 而 nag reminder 注入机制在它忘记更新时强制提醒。

## 问题

当智能体处理多步骤任务时, 它经常丢失对已完成和待办事项的追踪。没有显式的计划, 模型可能重复工作、跳过步骤或跑偏。用户也无法看到智能体内部的计划。

这个问题比听起来更严重。长对话会导致模型 "漂移" -- 随着上下文窗口被工具结果填满, 系统提示的影响力逐渐减弱。一个 10 步的重构任务可能完成了 1-3 步, 然后模型就开始即兴发挥, 因为它忘了第 4-10 步的存在。

解决方案是结构化状态: 一个模型显式写入的 TodoManager。模型创建计划, 工作时将项目标记为 in_progress, 完成后标记为 completed。nag reminder 机制在模型连续 3 轮以上不更新待办时注入提醒。

注: nag 阈值 3 轮是为教学可见性设的低值, 生产环境通常更高。从 s07 起, 课程转向 Task 看板处理持久化多步工作; TodoWrite 仍可用于轻量清单。

## 解决方案

```
+----------+      +-------+      +---------+
|   User   | ---> |  LLM  | ---> | Tools   |
|  prompt  |      |       |      | + todo  |
+----------+      +---+---+      +----+----+
                      ^               |
                      |   tool_result |
                      +---------------+
                            |
                +-----------+-----------+
                | TodoManager state     |
                | [ ] task A            |
                | [>] task B  <- doing  |
                | [x] task C            |
                +-----------------------+
                            |
                if rounds_since_todo >= 3:
                  inject <reminder> into tool_result
```

## 工作原理

1. TodoManager 验证并存储一组带状态的项目。同一时间只允许一个项目处于 `in_progress` 状态。

```python
class TodoManager:
    def __init__(self):
        self.items = []

    def update(self, items: list) -> str:
        validated = []
        in_progress_count = 0
        for item in items:
            status = item.get("status", "pending")
            if status == "in_progress":
                in_progress_count += 1
            validated.append({
                "id": item["id"],
                "text": item["text"],
                "status": status,
            })
        if in_progress_count > 1:
            raise ValueError("Only one task can be in_progress")
        self.items = validated
        return self.render()
```

2. `todo` 工具和其他工具一样添加到 dispatch map 中。

```python
TOOL_HANDLERS = {
    "bash":  lambda **kw: run_bash(kw["command"]),
    # ...other tools...
    "todo":  lambda **kw: TODO.update(kw["items"]),
}
```

3. nag reminder 在模型连续 3 轮以上不调用 `todo` 时, 向 tool_result 消息中注入 `<reminder>` 标签。

```python
def agent_loop(messages: list):
    rounds_since_todo = 0
    while True:
        if rounds_since_todo >= 3 and messages:
            last = messages[-1]
            if (last["role"] == "user"
                    and isinstance(last.get("content"), list)):
                last["content"].insert(0, {
                    "type": "text",
                    "text": "<reminder>Update your todos.</reminder>",
                })
        # ... rest of loop ...
        rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
```

4. 系统提示指导模型使用 todo 进行规划。

```python
SYSTEM = f"""You are a coding agent at {WORKDIR}.
Use the todo tool to plan multi-step tasks.
Mark in_progress before starting, completed when done.
Prefer tools over prose."""
```

## 核心代码

TodoManager 和 nag 注入 (来自 `agents/s03_todo_write.py`,
第 51-85 行和第 158-187 行):

```python
class TodoManager:
    def update(self, items: list) -> str:
        validated = []
        in_progress_count = 0
        for item in items:
            status = item.get("status", "pending")
            if status == "in_progress":
                in_progress_count += 1
            validated.append({
                "id": item["id"],
                "text": item["text"],
                "status": status,
            })
        if in_progress_count > 1:
            raise ValueError("Only one in_progress")
        self.items = validated
        return self.render()

# In agent_loop:
if rounds_since_todo >= 3:
    last["content"].insert(0, {
        "type": "text",
        "text": "<reminder>Update your todos.</reminder>",
    })
```

## 相对 s02 的变更

| 组件           | 之前 (s02)       | 之后 (s03)                   |
|----------------|------------------|--------------------------|
| Tools          | 4                | 5 (+todo)                |
| 规划           | 无               | 带状态的 TodoManager     |
| Nag 注入       | 无               | 3 轮后注入 `<reminder>`  |
| Agent loop     | 简单分发         | + rounds_since_todo 计数器|

## 设计原理

可见的计划能提高任务完成率, 因为模型可以自我监控进度。nag 机制创造了问责性 -- 没有它, 随着对话上下文增长和早期指令淡化, 模型可能在执行中途放弃计划。"同一时间只允许一个 in_progress" 的约束强制顺序聚焦, 防止上下文切换开销降低输出质量。这个模式之所以有效, 是因为它将模型的工作记忆外化为结构化状态, 使其能够在注意力漂移中存活。

## 试一试

```sh
cd learn-claude-code
python agents/s03_todo_write.py
```

可以尝试的提示:

1. `Refactor the file hello.py: add type hints, docstrings, and a main guard`
2. `Create a Python package with __init__.py, utils.py, and tests/test_utils.py`
3. `Review all Python files and fix any style issues`



```
s03 >> 我是windows系统。先检查scripts目录下有哪些文件，如果没有all.txt文件，则创建该文件，最后往该文件中写入“你好蔡启越”

todo: 
[>] #1: 检查scripts目录下有哪些文件
[ ] #2: 如果没有all.txt文件，则创建该文件
[ ] #3: 往all.txt文件中写入"你好蔡启越"

(0/3 completed)
> bash: 'ls' 不是内部或外部命令，也不是可运行的程序
或批处理文件。
> bash: 驱动器 E 中的卷没有标签。
 卷的序列号是 EA21-C92C

 E:\learn-claude-code\scripts 的目录

2026-02-27  10:57    <DIR>          .
2026-02-25  15:45    <DIR>          ..
2026-02-27  10:39               222 a.py
2026-02-25  1
> todo: [x] #1: 检查scripts目录下有哪些文件
[x] #2: 如果没有all.txt文件，则创建该文件
[>] #3: 往all.txt文件中写入"你好蔡启越"

(2/3 completed)
> write_file: Wrote 5 bytes
> todo: [x] #1: 检查scripts目录下有哪些文件
[x] #2: 如果没有all.txt文件，则创建该文件
[x] #3: 往all.txt文件中写入"你好蔡启越"

(3/3 completed)
```



# 问题一

## 1) 为什么需要 Nag：LLM 的“漂移”是结构性问题

LLM 做多步任务时常见失控方式：

- **忘记计划**：开始有计划，做两步后不再更新 todo，后面就自由发挥。
- **重复/跳步**：因为没看到进度状态，重复做已完成的事，或者直接跳过关键步骤。
- **上下文稀释**：对话越长，工具输出越多，“系统提示 + 早期计划”在上下文里占比越低，模型更容易偏离最初的约束。

TodoWrite 的核心思路是把“工作记忆”外化成 TodoManager；但还不够：**模型仍可能偷懒不写 todo**，或者忙着执行工具忘了更新状态。

Nag 机制就是为这个漏洞准备的：

> **你可以不自觉更新 todo，但系统会在你不更新时不断提醒你更新。**

------

## 2) Nag 注入机制到底是什么？

**Nag 注入机制 = 在特定条件满足时，系统自动向模型的输入消息里“注入一段提醒文本”。**

关键点：

- 这不是模型自己想起来的提醒；
- 是 agent runtime（外部循环 / orchestration layer）做的；
- 注入的内容通常很短、格式稳定、容易被模型识别（比如 `<reminder>...</reminder>`）。

它的作用是制造一种“不可忽视的信号”，让模型重新关注到：
 **“你应该更新 Todo/计划状态”**。

------

## 3) 注入发生在“哪里”？在 agent loop 的消息构建阶段

一个典型 agent 运行循环大概是：

1. 收集 messages（用户消息、历史工具结果等）
2. 交给模型生成下一步动作（tool call 或回答）
3. 执行工具，得到 tool_result
4. 把 tool_result 回写进 messages
5. 重复

Nag 注入通常发生在 **第 1 步 / 第 4 步附近**——也就是“给模型下一次推理前”的输入整理阶段。

你贴的伪码就是一种常见写法（概念上）：

- runtime 维护一个计数器 `rounds_since_todo`
- 每一轮如果模型没有调用 `todo` 工具，就 `+1`
- 一旦 `>= 3`，就在“下一次模型看到的输入”里插入 `<reminder>Update your todos</reminder>`

这就是“注入”。

------

## 4) 为什么它有效？因为它改变了模型的“注意力分配”

LLM 并没有真正的长期记忆，它在每一轮主要依赖：

- 最近输入（recency）
- 明确、结构化的指令（format + tags）
- 强烈的约束信号（比如系统指令、特殊标签）

Nag 注入能有效，是因为它：

1. **把提醒放到“最近输入”**（通常插到最后一条 user/tool content 的前面或很靠前的位置）
    → 触发模型注意力，降低“我没看到”的概率。
2. **用固定标签包装**（如 `<reminder>`）
    → 模型容易学会：看到这个就要做某个固定动作（更新 todo）。
3. **与工具状态绑定**
    → 一旦模型更新 todo，runtime 就把计数器清零，形成闭环：
    “不更新 → 被 nag → 更新 → nag 消失”。

它不是靠“模型更聪明”，而是靠“系统更会管”。

------

## 5) Nag 的触发条件怎么设计？

你看到的版本是最基础的：
 **连续 N 轮没有调用 todo → 注入提醒**

工程上常用的触发条件还会更细：

### A. 基于行为（最常见）

- `rounds_since_todo >= N`
- `rounds_since_plan_update >= N`
- `rounds_since_progress_change >= N`

### B. 基于任务阶段（更智能）

比如你要求“每个工具调用前必须把某条 todo 标为 in_progress”，那么可以做：

- 模型调用工具前没标 in_progress → 注入提醒
- 工具执行成功后没把当前 todo 标 completed → 注入提醒

### C. 基于风险信号（更高级）

- 对话很长、工具输出很多、模型开始输出与任务无关内容
   → 降低阈值、增加提醒强度

------

## 6) 注入到哪里最好？3 个常见策略

### 策略 1：注入到“下一条 user content”的开头（你贴的就是这个思路）

优点：模型最容易看到
 缺点：会“污染”用户消息（从纯粹性上讲）

### 策略 2：注入成一条 system / developer 级别的短消息

优点：更强约束
 缺点：有些实现里 system 太强，可能导致模型过度关注提醒、影响自然度

### 策略 3：注入到 tool_result（作为“工具反馈的一部分”）

优点：语义上合理：像“运行环境在提醒你要维护状态”
 缺点：如果 tool_result 很长，提醒可能被淹没（需要放在最前面）

实际工程里常选：

- **放在 tool_result 的最前面** 或
- **加一条独立的短消息**（role=system 或 role=tool 的提示）

------

## 7) Nag 的“强度”怎么控制？别把 agent nag 到发疯

Nag 提醒太频繁，会造成两类副作用：

1. **模型只顾更新 todo，不干活**
2. **用户体验变差**：每几轮都被提醒，看起来像“唠叨机器人”

所以一般会有“渐进式 nag”策略：

- 第一次：轻提醒
   `<reminder>Remember to update your todo status.</reminder>`
- 第二次：明确要求
   `<reminder>You have not updated todos in 3 rounds. Update now: set one task in_progress.</reminder>`
- 第三次：强制门禁（gating）
   “在更新 todo 之前不允许调用其他工具” 或 “拒绝继续执行”

这就从“提醒”升级成“流程守门员”。

------

## 8) Nag 和 TodoWrite 的关系：一个管“记”，一个管“别忘记记”

- **TodoWrite/TodoManager**：提供一个外部状态容器，让计划可见、可更新
- **Nag injection**：提供一个外部监督器，防止模型不更新状态导致计划失效

一句话：

> TodoManager 是“待办看板”，Nag 是“看板纪律检查员”。

------

## 9) 给你一个更贴近工程的“最小实现”伪逻辑

你可以用下面这个心智模型理解：

- runtime 维护：
  - `last_todo_hash`（上次 todo 内容）
  - `rounds_since_todo_update`
  - `current_in_progress_id`

每轮：

1. 模型输出 tool call
2. 如果 tool call 里没有 todo 更新 → `rounds_since_todo_update += 1`
3. 如果 `>= N`：
   - 注入提醒消息（短、固定、靠前）
4. 一旦检测到 todo 更新：
   - `rounds_since_todo_update = 0`

------

## 10) 你作为初学者，该怎么判断一个 nag 机制“做对了”？

看 3 个指标：

1. **模型是否在长任务里持续更新 todo**（持续性）
2. **是否减少重复/跳步**（正确性）
3. **提醒是否不过度打扰**（体验）

如果你看到 agent 在完成任务时：

- 每个阶段切换都会更新状态
- nag 很少出现（因为模型自觉更新）
   那就说明 nag 机制工作得很好：它“存在但不显眼”。

# 问题二

我会从一个 agent 架构师视角，把这三种东西讲清楚：

1. ✅ Todo 清单模式（TodoWrite / Task list）
2. ✅ Plan 模式（一次性规划）
3. ✅ spe-kit 这种“结构化规范驱动”模式
4. ✅ 它们的核心差异、本质区别、优缺点

------

## 一、先给你一个核心结论

**Todo 模式 = 带状态的执行控制系统**

**Plan 模式 = 一次性推理产物**

这句话是本质区别。

------

## 二、Plan 模式是什么？

Plan 模式通常是这样：

```
User: 重构这个项目
LLM:
1. 分析代码结构
2. 抽取公共函数
3. 添加测试
4. 更新 README
```

然后模型开始执行。

Plan 是：

- 静态文本
- 不强制更新
- 没有状态机
- 不受 runtime 监督

它只是：

> “模型脑子里的一次结构化输出”

------

### Plan 的优点

- 简单
- 成本低
- 推理能力强（一次性深度思考）
- 对短任务很有效

------

### Plan 的缺点

- 没有状态记忆
- 容易中途漂移
- 不会强制更新
- 无法防止跳步骤
- 长任务失败率高

------

## 三、Todo 模式是什么？

Todo 模式不是“列个清单”这么简单。

它是：

> 一个受 runtime 约束的、可变的、带状态的执行结构。

区别点在于：

| 属性           | Plan   | Todo                     |
| -------------- | ------ | ------------------------ |
| 是否有状态     | ❌      | ✅                        |
| 是否可更新     | ❌      | ✅                        |
| 是否有监督机制 | ❌      | ✅ (nag)                  |
| 是否有执行约束 | ❌      | ✅ (only one in_progress) |
| 是否可持久     | 通常否 | 可以                     |

Plan 是：

```
思考结果
```

Todo 是：

```
执行控制系统
```

这本质不同。

------

## 四、为什么 Plan 在长任务中会失败？

这是一个认知架构问题。

LLM 的注意力机制：

- 近端信息权重大
- 上下文越长，早期内容越弱
- 工具输出会淹没早期计划

当对话变长：

```
System prompt
Plan
Tool result
Tool result
Tool result
...
```

Plan 会被“稀释”。

Todo 不一样，因为：

- 每次更新都会刷新
- 状态是当前的
- 运行时强制模型关注

------

## 五、Todo 模式的优缺点

### 优点

1. 抗漂移
2. 可监督
3. 可恢复
4. 可持久化
5. 适合复杂多步骤任务

### 缺点

1. 约束过强会降低灵活性
2. 频繁更新增加 token 成本
3. 单 in_progress 会降低并行能力
4. 如果设计不好会变成“官僚主义”

------

## 六、Plan 模式什么时候更好？

- 短任务
- 创意任务
- 一次性分析
- 不需要严格顺序的工作

Plan 强在“认知深度”，
 Todo 强在“执行稳定性”。

------

## 七、spe-kit 是什么类型？

你记得是对的。

spe-kit 属于：

> 结构化规范驱动执行（Spec-driven agent）

它的核心思想是：

- 把需求写成结构化 spec
- 模型按照 spec 的 checklist 工作
- 通过“规范模板”减少自由度

它本质上：

介于 Plan 和 Todo 之间。

------

### spe-kit 的特点

- 类似 checklist
- 类似 TODO
- 但更偏“规范验证”
- 强调结构化输出
- 强调一致性

它不是单纯 todo，
 而是：

> 规范约束型执行系统

------

## 八、三种模式的对比

| 维度                | Plan | Todo | spe-kit            |
| ------------------- | ---- | ---- | ------------------ |
| 是否动态            | ❌    | ✅    | 部分               |
| 是否带状态          | ❌    | ✅    | 部分               |
| 是否有 runtime 监督 | ❌    | 可有 | 通常没有强 runtime |
| 是否强调规范        | ❌    | ❌    | ✅                  |
| 适合长任务          | 一般 | 强   | 强                 |
| 灵活性              | 高   | 中   | 低                 |

------

## 九、更高维度的理解

你可以把它们理解成三种“控制层级”：

### 第一层：纯认知（Plan）

> 模型自己想一套步骤

------

### 第二层：执行控制（Todo）

> 模型必须汇报进度

------

### 第三层：规范约束（spe-kit）

> 模型必须满足结构化规范

------

## 十、架构师角度的真正区别

Plan 是 cognitive pattern
 Todo 是 state machine
 spe-kit 是 schema contract

这是三种不同范式。

------

## 十一、在真实系统里怎么选？

一般生产级 agent 会：

1. 先生成 Plan（深度思考）
2. 再转成 Todo（可执行状态机）
3. 再用 Spec 校验（质量控制）

也就是三者融合。

------

## 十二、你现在可以理解的一个更深层概念

Plan 是“想清楚怎么做”
 Todo 是“保证按步骤做”
 Spec 是“保证做对”

这是三个不同维度。

# 问题三

## 第一部分：工具描述除了 JSON schema 和 docstring 还有哪些形式？

你给的这种：

```
TOOLS = [
  {
    "name": "write_file",
    "description": "...",
    "input_schema": {...}
  }
]
```

本质属于：

> 显式 JSON Schema 驱动的工具定义

这是当前最主流的方式（Anthropic / OpenAI function calling）。

但实际上工具描述有多种流派。

------

### 1️⃣ JSON Schema（结构化定义）

特点：

- 强类型
- 可枚举
- 有 required
- 有 enum
- 机器可校验

典型结构：

```
{
  "type": "object",
  "properties": {
    "path": {"type": "string"},
    "content": {"type": "string"}
  },
  "required": ["path", "content"]
}
```

优点：

- 模型容易学
- runtime 可做严格验证
- 自动生成 UI / SDK
- 强约束

缺点：

- 表达能力有限（不能写复杂逻辑）
- schema 太大时模型会忽略细节

------

### 2️⃣ Python docstring 作为工具描述

比如：

```
def write_file(path: str, content: str):
    """
    Write content to file.
    Args:
        path: File path.
        content: Text content to write.
    """
```

框架自动提取：

- 函数名
- 参数名
- 类型注解
- docstring

这在 LangChain / LlamaIndex 里常见。

优点：

- 开发者体验好
- 自动从代码反射生成工具

缺点：

- 模型解析自然语言
- 精度不如 JSON schema
- 不强类型

------

### 3️⃣ OpenAPI / REST 规范作为工具描述

一些高级 agent 会直接用：

- OpenAPI spec
- Swagger
- gRPC proto

模型通过 API 规范调用真实后端。

优点：

- 工业级 API 描述
- 可自动对接真实服务

缺点：

- 描述过大
- 模型容易迷失
- 需要压缩

------

### 4️⃣ DSL（领域专用语言）

有些 agent 系统用：

```
tools:
  - name: write_file
    args:
      path: str
      content: str
    rules:
      - must use absolute path
      - content must be utf-8
```

这是一种“半结构化 DSL”。

优点：

- 可扩展
- 可加规则
- 更灵活

缺点：

- 模型学习成本高

------

### 5️⃣ 纯自然语言工具列表

最早的 ReAct agent 就是：

```
You can use the following tools:
Search(query)
Lookup(term)
```

完全自然语言。

优点：

- 简单
- 灵活

缺点：

- 错误率高
- 参数不稳定

------

### 工具描述格式总结

| 类型        | 强约束 | 机器可校验 | 模型准确率 | 复杂度 |
| ----------- | ------ | ---------- | ---------- | ------ |
| JSON Schema | 强     | 强         | 高         | 中     |
| Docstring   | 中     | 弱         | 中         | 低     |
| OpenAPI     | 强     | 强         | 中         | 高     |
| DSL         | 中     | 可定制     | 中         | 中     |
| 纯自然语言  | 弱     | 无         | 低         | 低     |

生产系统几乎都会用 JSON schema 或 OpenAPI。

------

## 第二部分：模型真的能靠工具描述精准生成参数吗？

这个问题问得非常关键。

答案是：

> 不完全可靠，但在良好设计下可以做到“非常高成功率”。

我拆开讲。

------

### 1️⃣ 模型是怎么理解工具参数的？

当模型看到：

```
{
  "name": "write_file",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {"type": "string"},
      "content": {"type": "string"}
    },
    "required": ["path", "content"]
  }
}
```

模型在内部会：

- 学到参数名
- 学到 required
- 学到 enum
- 学到类型

大模型在预训练时已经见过大量 JSON schema。
 它们对：

- required
- enum
- object
- array

非常熟悉。

这不是推理，是模式匹配。

------

### 2️⃣ 什么时候会出错？

#### ❌ 情况 1：参数歧义

```
{
  "old_text": "string",
  "new_text": "string"
}
```

模型有时会：

- 搞反
- 少填
- 多填

因为语义太接近。

------

#### ❌ 情况 2：schema 太复杂

嵌套三层数组 + 多个 enum + 可选字段：

模型会忽略部分字段。

------

#### ❌ 情况 3：描述不清

如果 description 写得模糊：

> Replace text

模型不知道是否是 exact match 还是 fuzzy。

------

### 3️⃣ 工程上如何保证“几乎不出错”？

真正成熟的 agent 系统不会“只靠模型”。

他们会做三层防护：

------

#### 🛡 第一层：JSON schema 强校验

runtime 做：

```
jsonschema.validate(arguments, schema)
```

如果失败：

- 返回错误
- 要求模型重试

------

#### 🛡 第二层：工具错误回馈给模型

如果参数错：

```
Error: missing required field "path"
```

模型通常第二次会修正。

------

#### 🛡 第三层：参数重写 / 自动补全

有些系统会：

- 自动补默认值
- 自动路径规范化
- 自动修复小错误

------

### 4️⃣ 实际成功率如何？

在结构良好的 schema 下：

- GPT-4 / Claude 级别模型
- 简单工具（<5 参数）
- 清晰 description

成功率可以 95% 以上。

复杂嵌套结构会降到 80% 左右。

------

### 一个非常重要的架构观点

工具调用不是“模型自由发挥”。

它是：

> 结构化受约束生成（constrained generation）

现代 function calling 实际上使用：

- JSON token bias
- 强约束 decoding
- 部分语法引导

这大幅提高正确率。

------

### 更深层回答你的问题

你问：

> 大模型真的可以通过工具描述就能精准整理输入吗？

正确答案是：

它可以“学会格式”，
 但不能保证“业务语义完全正确”。

举例：

模型可以保证：

```
{"path": "a.txt", "content": "hello"}
```

但不能保证：

- path 是对的目录
- content 逻辑正确
- old_text 真存在于文件中

格式正确 ≠ 语义正确。

------

## 最终总结

### 工具描述方法

- JSON Schema（主流）
- Docstring
- OpenAPI
- DSL
- 自然语言

### 模型是否可靠？

- 格式层面：高可靠
- 语义层面：中等可靠
- 工程上必须加验证层



# 问题四

## 一、先理解一个基本事实

LLM 本质是：

> 逐 token 预测下一个 token 的概率模型。

如果你不限制它，它可以输出：

```
Sure! Here's what I think...
```

但如果你希望它输出：

```
{"path": "a.txt", "content": "hello"}
```

你必须控制它的“可选 token 空间”。

这就是 constrained generation。

------

## 二、JSON Token Bias 是什么？

### 通俗理解：给某些“词”加权重

想象模型在生成：

```
{
```

此时它可能预测：

- `"path"`
- `"Sure"`
- `"Let"`
- `"content"`

我们可以人为提高 `"path"` 这个 token 的概率。

这就是 token bias。

------

### 举个直观例子

假设当前生成到：

```
{
```

模型下一步本来概率是：

| token     | 概率 |
| --------- | ---- |
| "path"    | 0.25 |
| "content" | 0.20 |
| "Sure"    | 0.15 |
| "Let"     | 0.10 |

我们人为对合法 JSON key 做 bias：

```
logit["path"] += 2.0
logit["content"] += 2.0
```

结果概率变成：

| token     | 概率 |
| --------- | ---- |
| "path"    | 0.45 |
| "content" | 0.35 |
| 其他      | 很低 |

模型更容易生成合法 key。

------

### 类比

像考试时：

老师说：

> 选择题只能选 A B C D

并且：

> 选 A 或 B 会给加分

模型自然不会选 E。

------

### 作用

- 提高结构正确率
- 降低乱输出概率
- 但不能 100% 保证

因为模型还是“自由生成”，只是被轻推了一下。

------

## 三、强约束 decoding 是什么？

这就更硬核了。

### 通俗理解：不合法的 token 直接不让选

这不是“加权”，而是：

> 不合法的 token 概率直接设为 0。

例如你当前生成：

```
{"path":
```

合法的下一个 token只能是：

- 空格
- 字符串开始 `"`

如果模型想输出：

```
Sure
```

系统直接禁止。

------

### 举例

当前状态机在：

```
{
```

允许 token：

- `"path"`
- `"content"`

不允许：

- `Sure`
- `Hello`
- 任何普通文本

如果模型预测非法 token：

```
Sure
```

系统直接：

```
prob = 0
```

模型只能选合法 token。

------

### 类比

像一个自动售货机：

你只能按存在的按钮。

按不存在的按钮根本不会响应。

------

### 这是怎么实现的？

工程上会：

- 把 JSON schema 编译成状态机
- 每生成一个 token 更新状态
- 根据状态决定“下一个合法 token 集合”

这叫：

> grammar-constrained decoding

------

### 效果

- 结构 100% 正确
- 格式 100% 合法
- 但语义仍然可能错

------

## 四、部分语法引导是什么？

这是介于两者之间的技术。

它不像强约束那样完全禁止，
 也不像 token bias 那样只是轻推。

它是：

> 用一个语法模板引导生成方向。

------

### 举例

系统提示模型：

```
You MUST respond in JSON:
{
  "path": string,
  "content": string
}
```

并且在内部 prompt 加：

```
Only output valid JSON.
```

模型会倾向按模板输出。

------

### 更高级版本

有些系统在生成前，会插入：

```
<json>
```

然后在生成结束强制检测：

- 是否合法 JSON
- 是否匹配 schema

如果不合法 → 让模型重试。

------

### 类比

像给模型一个填空题：

```
{
  "path": "_____",
  "content": "_____"
}
```

它只是在空格里填东西。

------

## 五、三者对比

| 技术            | 限制强度 | 是否保证合法结构 | 实现复杂度 |
| --------------- | -------- | ---------------- | ---------- |
| Token bias      | 弱       | 否               | 低         |
| 部分语法引导    | 中       | 大概率           | 中         |
| 强约束 decoding | 强       | 是               | 高         |

------

## 六、一个非常直观的比喻

假设你让一个孩子画一个正方形。

### Token bias

你说：

> 尽量画四条边。

他可能画五条。

------

### 语法引导

你给他画一个虚线框：

> 沿着虚线画。

他大概率画对。

------

### 强约束 decoding

你给他一个刻板模具：

> 只能沿着模具描。

他一定画出正方形。

------

## 七、为什么现代 function calling 成功率高？

因为它们通常：

1. 用语法引导
2. 再用强约束 decoding
3. 再做 schema 校验
4. 再做自动重试

这是多层保险。

------

## 八、一个关键理解

你要知道：

> LLM 本质是自由语言模型
>  工具调用是人为构造的“受控生成通道”

工具调用成功率高，不是模型变聪明了。

而是：

我们在控制“生成空间”。

------

## 九、一个架构级结论

如果你以后设计 agent 系统：

- 不要完全信任模型
- 把结构交给解码器控制
- 把语义交给模型负责

结构 = 系统保证
 语义 = 模型负责

这是现代 agent 架构的核心思想。
