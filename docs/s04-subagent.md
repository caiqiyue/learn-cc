# s04: Subagent (子智能体)

> 子智能体使用全新的消息列表运行, 与父智能体共享文件系统, 仅返回摘要 -- 保持父上下文的整洁。

## 问题

随着智能体工作, 它的消息数组不断增长。每次工具调用、每次文件读取、每次 bash 输出都在累积。20-30 次工具调用后, 上下文窗口充满了无关的历史。为了回答一个简单问题而读取的 500 行文件, 会永久占据上下文中的 500 行空间。

这对探索性任务尤其糟糕。"这个项目用了什么测试框架?" 可能需要读取 5 个文件, 但父智能体的历史中并不需要这 5 个文件的全部内容 -- 它只需要答案: "pytest, 使用 conftest.py 配置。"

在本课程里, 一个实用解法是 fresh `messages[]` 隔离: 以 `messages=[]` 启动一个子智能体。子智能体进行探索、读取文件、运行命令。完成后, 只有最终的文本响应返回给父智能体。子智能体的全部消息历史被丢弃。

## 解决方案

```
Parent agent                     Subagent
+------------------+             +------------------+
| messages=[...]   |             | messages=[]      | <-- fresh
|                  |  dispatch   |                  |
| tool: task       | ---------->| while tool_use:  |
|   prompt="..."   |            |   call tools     |
|                  |  summary   |   append results |
|   result = "..." | <--------- | return last text |
+------------------+             +------------------+
          |
Parent context stays clean.
Subagent context is discarded.
```

## 工作原理

1. 父智能体拥有一个 `task` 工具用于触发子智能体的生成。子智能体获得除 `task` 外的所有基础工具 (不允许递归生成)。

```python
PARENT_TOOLS = CHILD_TOOLS + [
    {"name": "task",
     "description": "Spawn a subagent with fresh context.",
     "input_schema": {
         "type": "object",
         "properties": {
             "prompt": {"type": "string"},
             "description": {"type": "string"},
         },
         "required": ["prompt"],
     }},
]
```

2. 子智能体以全新的消息列表启动, 仅包含委派的 prompt。它共享相同的文件系统。

```python
def run_subagent(prompt: str) -> str:
    sub_messages = [{"role": "user", "content": prompt}]
    for _ in range(30):  # safety limit
        response = client.messages.create(
            model=MODEL, system=SUBAGENT_SYSTEM,
            messages=sub_messages,
            tools=CHILD_TOOLS, max_tokens=8000,
        )
        sub_messages.append({
            "role": "assistant", "content": response.content
        })
        if response.stop_reason != "tool_use":
            break
        # execute tools, append results...
```

3. 只有最终文本返回给父智能体。子智能体 30+ 次工具调用的历史被丢弃。

```python
    return "".join(
        b.text for b in response.content if hasattr(b, "text")
    ) or "(no summary)"
```

4. 父智能体将此摘要作为普通的 tool_result 接收。

```python
if block.name == "task":
    output = run_subagent(block.input["prompt"])
results.append({
    "type": "tool_result",
    "tool_use_id": block.id,
    "content": str(output),
})
```

## 核心代码

子智能体函数 (来自 `agents/s04_subagent.py`, 第 110-128 行):

```python
def run_subagent(prompt: str) -> str:
    sub_messages = [{"role": "user", "content": prompt}]
    for _ in range(30):
        response = client.messages.create(
            model=MODEL, system=SUBAGENT_SYSTEM,
            messages=sub_messages,
            tools=CHILD_TOOLS, max_tokens=8000,
        )
        sub_messages.append({"role": "assistant",
                             "content": response.content})
        if response.stop_reason != "tool_use":
            break
        results = []
        for block in response.content:
            if block.type == "tool_use":
                handler = TOOL_HANDLERS.get(block.name)
                output = handler(**block.input)
                results.append({"type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output)[:50000]})
        sub_messages.append({"role": "user", "content": results})
    return "".join(
        b.text for b in response.content if hasattr(b, "text")
    ) or "(no summary)"
```

## 相对 s03 的变更

| 组件           | 之前 (s03)       | 之后 (s04)                    |
|----------------|------------------|---------------------------|
| Tools          | 5                | 5 (基础) + task (仅父端)  |
| 上下文         | 单一共享         | 父 + 子隔离               |
| Subagent       | 无               | `run_subagent()` 函数     |
| 返回值         | 不适用           | 仅摘要文本                |

## 设计原理

在本节中, fresh `messages[]` 隔离是一个近似实现上下文隔离的实用办法。全新的 `messages[]` 意味着子智能体从不携带父级历史开始。代价是通信开销 -- 结果必须压缩回父级, 丢失细节。这是消息历史隔离策略, 不是操作系统进程隔离本身。限制子智能体深度 (不允许递归生成) 防止无限资源消耗, 最大迭代次数确保失控的子任务能终止。

## 试一试

```sh
cd learn-claude-code
python agents/s04_subagent.py
```

可以尝试的提示:

1. `Use a subtask to find what testing framework this project uses`
2. `Delegate: read all .py files and summarize what each one does`
3. `Use a task to create a new module, then verify it from here`



```
response
Message(id='05f9bd4733623ac738db7c28e124eca2', container=None, content=[ThinkingBlock(signature='8a4df1976eeedc3efba8616f8949ac6721ab0c1427af17fc4fa781ab71cf43fb', thinking='The user wants me to find what testing framework this project uses. I should use the task tool to spawn a subagent that can explore the project and find the testing framework.', type='thinking'), ToolUseBlock(id='call_function_8kf1lmgmjytl_1', caller=None, input={'description': 'Find testing framework', 'prompt': 'Explore this project to find what testing framework it uses. Look for:\n1. package.json (if Node.js) - check dependencies and devDependencies for test-related packages\n2. Any test configuration files (like jest.config.js, vitest.config.ts, .mocharc, etc.)\n3. Test directories or files (like __tests__, test/, *.test.js, *.spec.js)\n4. Any CI configuration that might mention test frameworks\n5. Any documentation (README.md) that mentions testing\n\nReport back what testing framework(s) are being used in this project.'}, name='task', type='tool_use')], model='MiniMax-M2.5', role='assistant', stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=476, output_tokens=187, server_tool_use=None, service_tier=None), base_resp={'status_code': 0, 'status_msg': ''})




```





# 分析

如果用一句话解释: **子代理就是父代理临时雇来的“短工专家”**。  
它去做脏活累活 (大量读文件、跑命令、试错), 最后只把结论回报给父代理, 不把全过程塞进父代理的上下文。

可以把它想成两层角色:

1. 父代理: 负责总体目标、对话连续性、最终交付。
2. 子代理: 负责某个子任务的执行和探索, 干完就“下线”。

这份文档里的实现关键在于: 子代理启动时使用全新的 `messages=[]`。这意味着它没有父代理之前的历史包袱, 相当于开了一个干净工作台。  
但它和父代理共享同一个文件系统和工具能力 (除了不能再递归创建子代理), 所以它仍然能访问项目代码、运行命令并完成调查。

为什么要这么做?  
核心原因是**控制上下文污染**。

- 不用子代理时: 父代理亲自读 5 个大文件, 这些内容会一直留在主上下文里, 后续每轮都要“背着走”, 成本越来越高。
- 用子代理时: 父代理只收到“摘要结果”, 例如“项目使用 pytest + conftest.py”, 主上下文保持轻量。

这其实是在做一种“信息压缩分层”:

1. 子代理层: 保留细节, 允许高噪声探索。
2. 父代理层: 只保留高价值结论, 保持决策清晰。

从工程角度看, 这是一种很实用的架构模式, 特别适合:

1. 代码库摸底: 先让子代理扫描目录、定位关键模块, 父代理只接收结构化总结。
2. 大量检索任务: 日志排查、配置比对、批量读文件。
3. 可失败探索: 允许子代理试多条路径, 最后回传可用答案。

但它也有明确代价和边界:

1. 细节丢失: 父代理拿到的是摘要, 不是全量过程。
2. 摘要质量依赖提示词: 子代理总结得差, 父代理就会“失真”。
3. 不是系统级隔离: 它隔离的是消息历史, 不是操作系统进程或权限沙箱。
4. 必须限流: 文档里用“最大迭代次数 + 禁止递归子代理”来防止失控。

所以,“什么是子代理”可以更准确地说成:

**子代理不是一个更强的模型, 而是一种任务拆分与上下文管理机制。**  
它通过“独立短上下文执行 + 回传摘要”来提升主代理的稳定性、可扩展性和长期对话质量。

如果你要判断一个任务是否该交给子代理, 一个简单标准是:  
**这件事是否“过程很长但结论很短”**。  
如果是, 就很适合子代理。



# 问题一

常用，而且比“全靠子代理”更稳的工程手段主要有这些：

1. `滑动窗口 + 截断策略`  
只保留最近 `N` 轮对话和必要系统指令，旧消息按规则丢弃。

2. `分层摘要（rolling summary）`  
把历史对话压成“事实摘要 + 决策摘要 + 待办摘要”，后续只带摘要，不带原文。

3. `外置记忆（Memory Store）`  
把长期信息存到数据库（KV/向量库/图数据库），上下文里只放检索到的少量相关片段。

4. `RAG 按需召回`  
不是“全量塞进 prompt”，而是“先检索再注入”，每次只注入和当前问题最相关内容。

5. `结构化状态替代自然语言`  
把关键状态放在 JSON/Schema 里（如 `goal`, `constraints`, `done_items`），减少冗长描述和歧义。

6. `工具输出限流与清洗`  
对日志、搜索结果、命令输出做截断、去噪、字段提取，只保留必要字段。

7. `产物外置（Artifact 化）`  
长代码、长报告写入文件或对象存储，上下文只放路径/ID + 简短摘要。

8. `规划器/执行器分离`  
一个模块负责计划，一个模块负责执行；计划上下文和执行上下文分开，互相不污染。

9. `上下文预算治理`  
给不同信息类型设 token 配额（系统指令/历史/检索/工具结果），超预算就压缩或丢弃低优先级内容。

10. `TTL 与失效机制`  
给“临时事实”加过期时间，避免过时信息长期滞留在上下文里。

实战里最常见的组合是：`滑动窗口 + 分层摘要 + RAG + 工具输出限流`。  
这套通常就能显著降低上下文污染，同时保持回答质量。



# 问题二

**关系**
1. 父代理-子代理是一个具体模式：父代理负责总体目标，子代理负责子任务，完成后回传结果。
2. Multi-agent 是更大的概念：系统里有多个代理协作完成任务。
3. 所以“父子代理”通常是 multi-agent 的一种层级化实现，不是另一个概念。

**什么是 Multi-agent**
1. Multi-agent 指多个“可感知-可决策-可执行”的代理，通过消息、任务、共享状态协作。
2. 这些代理可以用同一个模型，也可以用不同模型；关键在“角色分工 + 协作机制”，不在模型数量。
3. 工程目标通常是：提效、降上下文污染、提升可靠性、支持并行。

**常见架构**
1. 层级式（Supervisor-Worker）：一个总控代理拆任务，多个子代理执行。
2. 路由式（Router-Specialist）：入口代理先分类，再转给领域专家代理。
3. 流水线式（Pipeline/DAG）：代理按固定阶段串联，如“检索-分析-写作-审校”。
4. 评审式（Planner-Executor-Critic）：计划代理出方案，执行代理落地，审查代理打分/纠错。
5. 黑板式（Blackboard）：多个代理读写同一共享工作区，谁有能力谁处理。
6. 对等协商式（Peer-to-Peer）：代理之间直接协商分工，无单一总控。

**工程实现方式**
1. 单进程多上下文：在一个服务内维护多个 `messages[]` 会话（最轻量，常见于原型）。
2. 工具化子代理：把“启动子代理”封装成 `task` 工具，由父代理调用（你现在看的就是这种）。
3. 事件驱动/消息队列：每个代理是独立服务，通过 Kafka/RabbitMQ/SQS 协作（适合生产）。
4. 工作流编排：用状态机或 DAG 引擎（如自建状态机、Temporal/LangGraph 思路）管理步骤和重试。
5. Actor 模型：每个代理是 actor，异步收发消息，天然支持并发和隔离。

**落地时最关键的工程点**
1. 状态管理：共享什么、隔离什么、谁有写权限。
2. 协议设计：统一任务输入输出 schema，避免“自由文本失真”。
3. 预算控制：token、时间、重试次数、并发上限。
4. 质量闭环：评审代理/规则校验/人工兜底。
5. 可观测性：每个代理的日志、轨迹、成本、失败原因可追踪。

一句话总结：  
**父子代理是 multi-agent 的一种“层级协作”形态；multi-agent 是一整套多角色协同的系统设计方法。**
