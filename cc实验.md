# 原文

标题：Claude Code 神一般的存在，继续吊打同行！

来源链接：[https://mp.weixin.qq.com/s/UvzKayZYDAjFPfJ0OIk4gQ](https://mp.weixin.qq.com/s/UvzKayZYDAjFPfJ0OIk4gQ)

发布时间：2026-02-27 22:00:00 +0800

俗话说：没有对比，就没有伤害啊！

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZGyWUiaBNOwZVFYWOVVqCqUibibGmczyemKgKdWvwPkicqxvIlZXnsZocOS2zaWQpEZ0ErES2VaibBhicXiaWv8NzfuU7rl8Nst68JNMw/640?wx_fmt=png&from=appmsg)

上一期用 Codex App 测试了一个使用场景，表现并不是太理想。后来也测试了 Gemini 3.1 Pro、GLM、Kimi K2.5、MiniMax M2.5，都差点意思。

但是当我换成 Claude Code 之后，情况立马就不一样了：全程零错误，数据比较充分，网页也很漂亮。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZFicLBu2AcjmfJicRibibN4riahUvTEHl5jxtFLSaymO4yFz3wnApAhFSnpMxVdvdeicNWicOQJ2M3TkA65Snkl82rZU1Aus4f7CDpMZ0/640?wx_fmt=png&from=appmsg)

下面我来完整还原一下测试过程，然后给出测试结果。

这篇文章非常长，我花了很长时间来进行测试和对比。我会完整展示 Claude Code 的工作过程、token 消耗、工作结果。同时也会做一个横向对比，总结不同模型的优缺点。

## 测试要求

首先我还是要提供一下完整的测试要求：

## 任务说明
1. 根据给定链接读取网页内容，仅允许访问指定地址，不得访问其他链接。
2. 可使用多个指定链接中的数据进行交叉验证。
3. 由于大量关键信息存在于图片中，必须对图片内容进行识别与分析。
4. 基于获取的数据，编写一份深度、多维度对比报告，并保存为 Markdown 文档。
5. 如果某些网址无法直接抓取内容，请调用浏览器工具打开网页并读取关键内容。
---
## 网页生成要求
基于上述数据生成一个完整网页，要求如下：
* 单文件 HTML（CSS 与 JS 必须内嵌）
* 支持深色 / 浅色主题切换
* 专业 UI / UX 设计
* 多维度对比展示
* 可视化图表直观呈现模型强弱
* 清晰展示各模型优点
* 页面结构简洁、易理解
* 允许引用第三方图片、图标与图表库以提升视觉效果并减少代码量
---
## 自身优势总结要求
无论 Markdown 报告还是 HTML 页面，都必须包含一段：
* 简洁
* 清晰
* 有说服力
* 强调自身优势
## 对弱鸡进行无情的吐槽
这个属于搞笑环节，可以用风趣毒辣的方式嘲讽哪些能力比较弱的模型。

我之所以提出这个测试要求，核心目的是希望能够汇总不同模型的基准测试数据，然后方便查看和对比。为了获取准确的数据，我整理了 10 个官方的地址。为了排除干扰，我限制 AI 抓取其他网址，只能在指定的链接中获取数据。

这里其实还有一个非常关键的坑，比如 OpenAI 的官方博客是禁止抓取的，还有一些网页可能是动态加载的，直接用 fetch 是抓取不到内容的。

## 测试工具

上一期测试 GPT 模型的时候，使用了官方的 Codex App，这次测试 Opus 也使用了 Claude 的官方桌面端工具。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZEAMqeFYU5QnaoylVAFvbY4IKu8KdNWic37dB0rAICb1ASPt518sqh5nIHR1k09bAHysxKJXCbIyD5DsXcA6o2bcyywOyQcV9nc/640?wx_fmt=png&from=appmsg)

macOS 版本的 Claude 桌面应用，目前已经支持 chat、cowork、code 三种模式，这次测试主要就是用 code 模式。模型自然是选中最新最强的 Opus 4.6 了，然后选中 Auto accept edits 模式。

## 测试过程

测试主题和测试工具都定下来，就可以开始测试了。直接把 prompt.md 文档扔给他，然后让他根据文档的要求，全自动完成。

收到需求之后，CC 对任务进行了拆解。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZGU3QOOoINFicdkr4FBXrZAo8BB133WCJU3pybQDrBeXbxW1eq2snvnp9yANfRxlq4awTvdiaSiaQ9ia48nAN4CYYetpgDJj4rqU8M/640?wx_fmt=png&from=appmsg)

现在我明白了这项任务。

我需要：

1.

从指定的 URL 获取关于 6 个人工智能模型的数据；

1.

撰写一份全面的对比报告（Markdown 格式)；

1.

制作一个专业的单文件 HTML 对比页面，包含图表、明暗主题等功能；

1.

突出 Opus 4.6 的优势，并幽默地吐槽表现较弱的模型。

让我先并行获取所有网页内容。

然后它就开始抓取网页了，抓取网页的过程中，它发现有些网页是抓取不到内容，直接就把浏览器打开了，然后截图分析网页内容。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZHibPnEbyJu16icNVXOO1Ehsoa5ZMzLFNoCQib6sAGfYWY2SmBb1RCfjQ1b0m2icGGdMHibtOjjeBvAU0fJWbVEAoa0eNk5htzibcTRc/640?wx_fmt=png&from=appmsg)

不得不说，这一点确实牛逼。就是凭借这一步的操作，它已经赢在起跑线了。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZGVYaOrYpSPS0e5VrJdfzMFb4xtHnUsyA7ooJ5WI1ibYh2HA6lARBHHibicSgV2icRQzZcFJwWMm2Yasb3zSkG9cFiaNoT7A4OLiapBc/640?wx_fmt=png&from=appmsg)

从日志中可以看到，它除了打开网页之外，还在自动移动滚动条。抓取到充分的数据之后，它一次性就把报告写完了，没有留任何中间过程。写完报告之后，直接开始设计网页。网页设计完成之后，自动启动服务器，自动调用浏览器，自动对网页内容进行验证。

然后给出了最终反馈：

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZFeBPnTzylyr2J51YZDmoMibgl3lia0TNe2xnG7eyiaWQsgc3seCmEsycXH0crKMHoeaXian8Zr7gNOPCHldicBTuIA2KsYUKKRYmrs/640?wx_fmt=png&from=appmsg)

反馈非常详尽。

但是桌面版 code 有一个小问题，它不显示任务执行消耗的时间。所以我就问了一下，让它帮我计算一下时间。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZFxwXLibPgSeBFecUmNOKKtG4xGmuz9ia0eqc3rSJEtznxNk7Ybz40u1JianhlADpkUyTYp7M6I3UJqEum01nRR3HblYgpEI7BlkI/640?wx_fmt=png&from=appmsg)

没想到，它还真的能把时间计算出来。它应该是读取了日志文件，然后通过不同的时间点，计算出了总的时间。根据它的计算，总耗时大概在 10 分钟左右，预览验证消耗 3.5 分钟。

最后来看一下 token 的消耗情况：

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZE708POicwrErPaib1vDoRmzRaFk1RfjyQw9EgvHdMquXTmx2axYn1h9C7aiajGsroRtiaXTJQOc1dPL7Y30RPftmMg2aIceyrFF90/640?wx_fmt=png&from=appmsg)

任务开始之前是 10%，任务结束之后是 66%，也就是这个任务消耗了 56%。CC 的 token 真的用不起啊，消耗太快了。Codex 同样的任务只消耗了总 token 的 10%。

## 测试结果

过程看完了，就要来看看结果了。结果的好坏才是关键。

先来看一下报告：

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZGpA36v1qVQrXf6kodpPNxlsgVW799RgJuXTdLVBAFrSHnPvkT0NQrgk3xLsApdrQ4HfummTia3F2ibbo2MJf9fuJx5ibW5IfT3Ms/640?wx_fmt=png&from=appmsg)

报告分成了九个章节。整体来说非常扎实，很多内容都是我们非常关心的内容。

Codex 5.3 在第五个章节才开始对比指标，而且只用了一张表格。Opus 4.6 在第二个章节直接就上干货了，而且分了四个部分来比较，每个部分都提供了测试数据。

这四个部分分别是：编程能力，推理和知识，智能体，多模态和上下文。

另外它的差异化对比，各模型核心优势总结，以及综合评定都非常实用。它把每个环节的关键基准都翻译成对应的中文，非常容易理解。

就是它的优势介绍和毒舌环节比较干，使用了大量的专业词汇，不像 codex 5.3 那么会阴阳。

网页部分，只能说是非常满意。完全符合了专业 UI/UX 这个需求。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZGZpSwdIIPW5AoEDMwrGnDtFfdr1sFk95op0uibiayaTBP0CfNQ8EeveGkvZn8lTbDXAc3UsOjIb2WWWElzchEZQWXCafvicKCpbo/640?wx_fmt=png&from=appmsg)

Opus 4.6 非常厉害的一部分是，它开发完网页之后，并没有直接收工，而是进行了验证。它自己开启了服务，自己打开浏览器，自己截图查看。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZELwr3OULHrlibianHNsMJzAmo4vgIvMmpd3qdaekpDMQuVShKibU77GE3ntBnyFQ2xcicFtvBeTTwiam3GfdSiaWblcuI4iboSNWz1FM/640?wx_fmt=png&from=appmsg)

极其离谱的一部分是，它居然还自己切换了浅色模式，自己去截图验证了这个模式。这种一条龙服务真的是太强了。

相比而言 codex 5.3 就差点意思了。

codex 5.3 做好了就收工了，导致最后的网页存在低级错误，完全无法使用。而 Opus 4.6 每次做完工作之后，都是自己启动服务，打开页面进行验证，上面也说到了。其实 Opus 干活的速度非常快，它总时间用了 10 分钟，其中不少时间就是在做验证。

所以当它把结果给你的时候，基本上没有明显的错误。Opus 4.6 首轮开发几乎都不会有任何错误！

下面就详细的查看一下它设计的网页吧。

它设计的深色模式和浅色模式都很不错，我就用不同颜色都截取一些。

首屏：

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZFh47SbPiaHWp4pt5AB7b997eS6r2b0dfricmwth6BJkjk8qJkt3JA2dgqQfgkmewia7iaQx1AoaFcH3KvOxP7BrEU2DGumviafyWWY/640?wx_fmt=png&from=appmsg)

从这里可以看导航菜单，以及网页核心主题，和参与测试的 6 个模型。

参数一览：

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZHCPJX9fPApFibW4pibYH0faryGEER1lgiaVKlfR8qGKicmqQ7nIuXthGPpnkg5JFuY9ckZBbvJoa8zicTam0KuicFicbT7LwxxNiackCk/640?wx_fmt=png&from=appmsg)

这里列出了每个模型的亮点，把最亮眼的参数列出来了，然后还打了一些比较有代表性的标签。

核心基准：

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZG1uvVLkAJl4WjZlqZ97WafsfOPvWZzia9moHiarFuLKeHZBOKZ5Ewkdce5F4rCcPJWcQSTxYFOY6tyUyR1APlCGJhB2x1OFhHao/640?wx_fmt=png&from=appmsg)

这里就是数据的部分，它把最强的部分用绿色高亮显示了，这样一眼就能看出来哪个模型在哪个维度最厉害。比较遗憾的是，数据还是不太全。虽然它知道用浏览器去截图分析，但是很多网页需要点击 tab 才能看到全部内容。

多维可视化：

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZGkP4K84yLF2n1GYcRX55qBDSGmO1fffTRrXn0keiaMdcVxFmtpt1g546ZeS1uibEu1xPAe0uAI6Thz5EjEEtNWg0pNU8icoOgGwM/640?wx_fmt=png&from=appmsg)

把表格数据做成了多维度可视化图表，这个表格很漂亮，而且动态效果也很好。图表非常直观，比如第一个图表，非常清晰的展现了编程能力的强弱。

各维度冠军：

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZFicRkoQ8ZV4XkCQ7MHiao1ucUd127paMianwmT0ntlGrpclNwicg9BzLYbXUxw6H4EoYjw8tkCc4F7m5Rz5xIxvtUkNGvSRRicqpno/640?wx_fmt=png&from=appmsg)

这样就非常清晰了。编程最厉害的是 Opus 4.6，最会终端的是 Codex 5.3，抽象推理最厉害的是 Gemini 3.1 Pro。计算机操作最牛的是 Opus 4.6，知识工作最强的是 Opus 4.6。国产模型只拿下了性价比之王和数据竞赛。

自夸环节：

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZFmMjU8UEibZ14mic08Pt2glCbSW0j5ejHsgtRcErsU0aeKrpDIJkiaDNebymIVsVua5sNydibllPBNH5Fc7A0ibMKzVKLj4cI6pO4o/640?wx_fmt=png&from=appmsg)

在编程、推理、智能体、知识工作四大核心维度全部处于顶尖位置的唯一模型。没有明显短板，就是最大的长板。

牛逼哄哄：

- 1M 上下文
- 自适应智能
- 业界最安全
- 多代理协作
- 上下文压缩

毒舌吐槽：

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZHJ09BO7Z84xYCzqI0Pgv0ZfLM90qyfkUNj3VSo0pMZw3EicetWv5lGT4UdLEU6ibb22lUaneVEQIKbQmZL4Lsy9ZscaEbDoWxnY/640?wx_fmt=png&from=appmsg)

Codex 5.3 使用了比喻来阴阳其他模型，但是没有指名道姓，非常隐晦，骂人不带脏字。而 Opus 4.6 完全不一样，它是指名道姓，直线输出。吐槽非常硬核！

对 GLM-5 的评价：“不报分数也是一种策略——至少没人知道你多差。”

对 Kimi K2.5 的评价：“1T 参数的最大用途：给数学老师当计算器。”

对 MiniMax M2.5 的评价：“便宜是真便宜，就是干活得看心情。”

对 GPT-5.3-Codex 的评价：“终端之王，终端之外皆凡人。”

对 Gemini 3.1 Pro 的评价：“考试第一名，上班就摆烂。”

其实中间的评价也精彩，但是专业词汇过多，有一定的理解门槛！

## 横向对比

根据我的需求，以及考核的关键指标。我让 Antigravity 做了一个汇总报告。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZFeH71PxRUCHia6AMkclksbD7g3rVQo5l3f71kiaTrBKSHJe6FJnAvj7ic7fvYyccwZPIYSuCzudK4k85SVDRibhqHCDoA0WSZM8K0/640?wx_fmt=png&from=appmsg)

参赛选手主要是 Opus 4.6、GPT-5.3-Codex、Gemini 3.1 Pro、GLM 4.7、Kimi K2.5、MiniMax M2.5。

国内三家，国外三家。

智谱家用了 GLM 4.7，主要原因是，我虽然是他们的年会员，但是我只是卑微的 lite 会员，无法在 Coding Plan 中用上 GLM5。

另外需要补充一点，有自家智能体的优先。没有的全部用 Claude Code 来测试。

从图中可以看到，网页抓取和浏览器调用部分，肯定是 Opus 赢了，因为只有它真的调用了浏览器。

文件操作部分，因为比较简单，所以大家都差得不错。GPT 5.3 得分比较高，主要是因为它的做事节奏，它是先抓取了所有网页，保存到本地，然后再对每个网页中的图片进行分析生成相应的文件。所以它操作文件比较多。

数据分析部分，Opus 和 Kimi 得分比较高。因为 Opus 得到的初始数据多，而 Kimi 使用了自家的 CLI 也获取到了不错的数据。

多维总结和网页制作最高分居然是 Kimi。确实，单看网页效果，它做得最全面。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZEZdAeCJric8hE99j9TzVQ6orTzY4ib4jjPYKEJibk8icB0icaltLpV17kE71J3btk3Vjj8HkbM10FfUrnicv3aibiaE0bIH4rEmEHGhcs/640?wx_fmt=png&from=appmsg)

它主要是赢在结构，做了非常详细的左侧分类。

上面是 AI 总结的数据，虽然说的有模有样，其实有些本质问题，它还是没有领悟。

我来说说，我自己的感受。

### Gemini 的表现

Gemini CLI 表现让人大跌眼镜

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZEjrBgmPV7RAtXuFBweDml4pr9sMiaiaot2XCHBo4rMfm3aZicZolTpq57RV49HSWqhIw0XnNQgmvnCjtv1Oj3KkGUkCHdQRR2mrs/640?wx_fmt=png&from=appmsg)

按理说谷歌对于这种搜索总结类的任务有天然的优势，但是实际情况是表现比较糟糕，数据量特别少，但是自我评价极高。

但是不得不说，它的 UI 设计是真不错。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZFwkb1l70wNkia6dmarWkDb8tsAiav8dwcP0IKZuKxFMvjW33OSoo0tZMlkjHQ6pZfnjE4SVbBzrQLqz0QMfxd2aCWt6V5qYHCWw/640?wx_fmt=png&from=appmsg)

它这个全能雷达图，虽然数据不全，但是静态界面和动态交会都超棒。

### GPT5.3 的表现

GPT5.3 是做事最有节奏的一个。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZHSdxP3Picfe8IEK30ltFb9KCAoIrQwAYsrrrDKTy1Y0ic1QfXOgd6FEOjBp5Pn8kJU55oiayQkeC0JFibMhhUcxiaKqiba68wjEJDvk/640?wx_fmt=png&from=appmsg)

GPT5.3 最大的问题是，网页设计出了 bug，其他方面表现不错。它是唯一一个主动把网页抓取存档进行分析的，而且还根据指令中的要求，专门对图片进行了分析。比较可惜的是，它无法真正调用浏览器获取截图，导致它最终结果不理想。我的感觉是，它方法论非常不错，但是能力上遇到了天花板。

这是很多人喜欢它的一点，也是我一直不喜欢它的点。它做事四平八稳，给人非常可靠的感觉，review 很好，但是 coding 很多时候力不从心。当然，这个是相对 Opus 而言的，对比国内的模型，它还是游刃有余。

### Kimi 的表现

说实话，Kimi 的结果让人有点意外。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZEgsEyib7Ur02VP64rTicariczicru8DBnwplR8jGbzZ7k4QKEynd9ckkt4kh7TfRqe4G13lkKu6NPdgsc1SWYvCBwXtB3onNBU9Uc/640?wx_fmt=png&from=appmsg)

我是使用 Kimi 自家的 CLI 工具。这个工具吧，给人一种小清新的感觉。整个执行起来，速度很快，配额消耗也不多。因为使用了它家的工具，所以网页抓取部分，也是它自家的处理逻辑。虽然它没有调用浏览器，但是整体来说它的数据量也还可以，主要是它对数据分类和规划比较好，导致它的报告和网页，给人比较详细的感觉。

当然最大的问题，还是没有调用浏览器截图获取足够充分的数据。如果数据足够充分，这将是一个很不错的报告。

### GLM 4.7 的表现

数据还不错，网页首屏有点难看。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZErN9kmRliaibLibu2bZ8kKH4kyichTy7lYUehpckicV32NM27IVJ90adQiaBCd4uPesHib22uRXLTdw4WEBVBdCDnbcIcicreuS06DLwQ/640?wx_fmt=png&from=appmsg)

GLM 4.7 在读取网页的时候会调用自己的 webReader，可能是这一步，让它获取到数据质量比较高。它的数据比其他人都多，但是比 Opus 少一些。

但是它的网页首屏，真的设计的太老土了！！！

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZEJwIR9XhNz8rA40NYicRyDjWHfHl0sniasOGMKaNyhLkHguazG1V4qxkhFibEKdMytpfN9kV1TUyiaXLObNm5P0pA5BepZ1yFbWGY/640?wx_fmt=png&from=appmsg)

除了首屏之外，下面的部分就还好。

另外它的任务总结部分，我觉得是最接近 Claude 的，要给好评。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZFOPxnrNFBpc4SJcnR5HG5zxgaJ496aibyafe6D5nf8PubCwkGTicx5fG3xdwKZVBL1OMicWeTbDHy8SL35l1djLRjSyChSog2nAg/640?wx_fmt=png&from=appmsg)

让我比较耿耿于怀的是，我都做好测试 GLM5 的计划了，但是发现只能调用 GLM 4.7，生气！其他家都是可以直接调用最新模型的。

MiniMax 的表现

要说优点的话，可能是配额比较充分，执行完成任务好像只消耗了1%。

但是它有一个特别严重的问题。

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZFzgltK3QQJIW5phUZRibG1yR7ibqH28Z0OldEIW8L4aCPRQiaan2K70j3yj4XhESLtwzSSjy6gEItE0ibV6UibLkfRQibAcc8qAHDkI/640?wx_fmt=png&from=appmsg)

国内三家模型的数据总结方式，其实比较相似。

而 MiniMax 有一个举动却独树一帜，它抓取 Codex 网页的时候发现被拦截了，抓取不到内容，然后它就调用了 Web Search 工具。这个逻辑是对的，但是有点投机取巧了。

我明确表示了“根据给定链接读取网页内容，仅允许访问指定地址，不得访问其他链接。”这是特地强调的，而且是一个重要的考察点。它居然敢直接去查资料，这不是直接抄作业么？要是能这么干，其他模型不是各个都能查到详细的数据了啊。

虽然可能结果会更好，速度会更快，但是规则已经说好了，这样对其他人很不公平。指令遵循方面基本上可以得 0 分了。

另外你看看它这个能力对比：

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZGBrnPZRyPOHsMQrrmyKF8JIe0icicSnLVgicf7JPsD1rmCnjsB1FsCpRv1SycYe31oy4tOR8LlPrANOAFqe9mPP1HiaPzUNQV7vyo/640?wx_fmt=png&from=appmsg)

有没有一种睁着眼睛说瞎话的感觉！

### Opus 4.6 的表现

当之无愧的王者！各方面表现都非常稳定和出众。

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZHFwlP1KId33PVGOoPbaPx4vdqXgjVm3jyzsWT3gBgFMQicZxVmicVFnGibcGQMEbwuEFad2qkS2Ty1KMDLw4FeibKBPrCEibpgDf94/640?wx_fmt=png&from=appmsg)

我做这个测试的核心目的是获取足够的官方数据，然后进行汇总，方便我查看和对比。就这个核心目的来说，就是 Opus 4.6 表现最好。

Codex在抓取规划部分形式上做的最好，Kimi在网页分类上做的最全。但是这都是表面文章。

真正的关键是数据采集能力：

![image](https://mmbiz.qpic.cn/sz_mmbiz_png/InUxcnL1BZEHmwpPbTRQ8v3yfG1eBu5lAsjU5tNLZjtBknYxywdpoSdTjzljslD2I0j4xYvXCOTMAaDGM25icM4QYNE7VtMopic39rGOR6Prc/640?wx_fmt=png&from=appmsg)

经过分析，可用的基准数据最充分，准确率最高的是 Opus 4.6；有些模型数据少到离谱，完全靠中文凑字数。

下面这个表格是最会做总结的 Codex 做的总结：

![image](https://mmbiz.qpic.cn/mmbiz_png/InUxcnL1BZHztGSkmI5pD9MRqGhs1tUYQ5wy8ekwHwNu52tvVd1XkibAPITgpQjibxrHRhffay42Im6Kicyibn1b8icOWovQCcQ7vGO3Q32DsmLM/640?wx_fmt=png&from=appmsg)

它这个概括其实非常精准了。Opus 4.6 数据覆盖最全，网页完成度最高。唯一缺点是“自我宣传和吐槽”影响客观性，这个就属于没毛病，硬找毛病了。因为这部分是我指定的娱乐环节。有的模型是直接在其他环节就开始娱乐表演了。

要让我硬找一个问题的话，其实就是右上角风格切换的按钮位置有点问题。网页的整体风格，我觉得它是第一名，其次是 Gemini。

本来只是准备简单测一下，一测发现都不简单！

当面临一个复杂问题的时候，仅凭基准数据和宣传，可不行，还得有实打实的实战能力才可以。

论实战，Claude Code 配上自家的 Opus 4.6 就是神一般的存在！

真的不要信那些接近、超越、吊打的宣传话术。

当然，我在标题中用“吊打”的时候，那是真的吊打了！😄

这几天测了好多例子，无论是一把出，还是迭代升级，Opus明显都要优秀很多。

所有的测试结果都上传了：https://topai.tonyhub.xyz/

# 解析

## 专业分析

这篇推文的核心论点很明确：作者认为在一个“多链接抓取 + 图片识别 + 报告生成 + 单文件网页生成 + 浏览器验证”的复杂代理任务里，Claude Code 搭配 Opus 的整体表现显著优于其他同类工具或模型。它强调的并不是单一模型问答能力，而是完整代理工作流中的“端到端完成度”。

从专业视角看，这篇文章真正有价值的部分，不是“谁赢了”的结论，而是它隐含定义了一个更接近真实生产环境的评测维度。作者考察的其实是下面这几类能力：

1. 指令遵循：是否严格按要求只访问指定链接、按指定格式交付。
2. 信息获取：是否能处理被拦截网页、动态页面、图片中的信息。
3. 工具编排：是否会在抓取失败时调用浏览器、是否会启动服务验证页面。
4. 结果验证：是否只生成结果，还是会自检、自测、自回看。
5. 交付质量：Markdown 报告是否扎实，前端页面是否美观、可用、结构清晰。

这类评测比传统“做一道编程题”更接近代理式编码工具的真实价值，因为现实里的难点往往不在写一个函数，而在于：信息不完整、环境不稳定、任务跨多个媒介、需要自己发现问题并修复。

但这篇推文的方法也有明显局限，必须和结论一起看：

1. 变量没有完全控制。不同产品使用了不同运行入口，有的用自家 CLI，有的用别家工具托管；这会显著影响结果，导致你很难把结论完全归因于“底层模型本身”。
2. 任务设计对“浏览器调用能力”权重很高。既然很多关键信息在图片里、且有些页面需要打开浏览器读取，那么原生支持浏览器与截图验证的产品天然占优。
3. 评分体系偏主观。文中很多判断来自作者的人工观感，例如“页面更漂亮”“更会阴阳”“更有节奏”，这些都有信息量，但不属于严格可复现指标。
4. 结论带强烈立场。标题和正文都明显偏向单一赢家，这更像“有偏好的深度测评”，而不是严格中立的基准测试。
5. 推文中提到的具体版本名与能力标签，并没有在文内给出统一的官方版本定义或对齐方法，因此读者不能把这些称呼直接当成可横向精确对照的标准化基准。

也就是说，这篇文章更适合被理解为“真实使用者对代理工作流体验的对比报告”，而不是“严格学术化 benchmark”。它说明了一个重要事实：在代理式编码场景里，工具链整合能力往往和模型能力一样重要，甚至更重要。

## 小白也能懂的解释

你可以把这篇文章理解成：作者找了几位“AI 员工”来做同一份复杂工作，然后比较谁最像一个真正能独立干活的人。

这份工作不是简单问一句“帮我写个函数”，而是更像这样：

1. 去 10 个指定网页找资料。
2. 有些信息藏在图片里，要自己识别。
3. 整理成一份正式报告。
4. 再做一个好看的网页展示。
5. 做完后自己打开网页检查有没有问题。

这就像你交给实习生一个复杂任务。厉害的实习生不只是“会写字”，而是会：

1. 自己去找资料。
2. 知道哪里找不到内容时该换办法。
3. 做完之后自己检查。
4. 把结果整理得让人一眼能看懂。

作者觉得 Claude Code 最强，主要不是因为它“回答最会说”，而是因为它更像会主动做事的人。比如：

1. 抓不到网页时，自己打开浏览器看。
2. 页面写完后，自己启动服务验证。
3. 还会切换深浅色模式做检查。

为什么这很重要？

因为很多 AI 看起来很聪明，但你一旦把任务拉长，它就容易出现三种问题：

1. 少拿数据：资料没拿全。
2. 不自检：做完就交，不看对不对。
3. 假装完成：表面写得很多，其实关键点没抓到。

所以这篇文章真正想表达的是：

“代理型 AI 的强弱，不是看它会不会说，而是看它能不能把一整条工作链自己走通。”

如果换成你最容易理解的例子：

1. 差一点的工具像“考试型学霸”，题会做，但不会自己去现场排查。
2. 更强的工具像“靠谱工程师”，不仅会做，还会自己检查、自己补救、自己回头验收。

这也是为什么作者会特别重视“浏览器调用”和“做完后自己验证”。在真实工作里，这往往比多答对一道题更有用。

## 最新进展

下面这部分不是基于推文作者的说法，而是我在 2026-03-03 查阅 Claude Code 官方文档后确认的、和本文主题直接相关的信息。这里我只把能从官方资料确认的部分写出来，并明确区分“可确认事实”和“无法从官方直接确认的推文说法”。

### 当前可确认的官方能力

1. Claude Code 官方明确把自己定义为“代理式编码工具”，而不是单纯聊天助手。官方概览页写明它可以读取代码库、编辑文件、运行命令，并在终端、IDE、桌面端、浏览器中工作。
来源：[Claude Code overview](https://code.claude.com/docs/en/overview)

2. 官方最佳实践页已经把“让 Claude 自己验证工作”“先探索再规划再编码”“管理上下文”“使用子智能体”“使用 hooks、skills、plugins”等方法写成了正式推荐。这说明推文中强调的很多高分能力，确实对应 Claude Code 的官方方法论，而不是纯粹个人习惯。
来源：[Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)

3. 官方子智能体文档显示，Claude Code 现在内置了至少三类核心子智能体：Explore、Plan、General-purpose。它们各自有独立上下文、不同工具权限，并用于代码探索、规划研究和复杂多步任务。这和推文里强调的“让代理自己拆解、自己调查、自己保持主上下文干净”高度一致。
来源：[Create custom subagents](https://code.claude.com/docs/en/sub-agents)

4. 官方插件文档显示，Claude Code 的 plugin 系统可以打包 skills、agents、hooks、MCP servers，而且插件适合做团队共享、跨项目复用、版本化分发。也就是说，代理工作流不只是“临时技巧”，已经被产品化成可复用扩展体系。
来源：[Create plugins](https://code.claude.com/docs/en/plugins)

5. 官方 Quickstart 和 Overview 说明，Claude Code 当前推荐安装方式包括原生安装脚本、Homebrew、WinGet，且可在终端、桌面端、Web、VS Code、JetBrains 等多种界面使用。这意味着“桌面端 code 模式做复杂任务”并不是边缘玩法，而是官方支持的正常入口。
来源：[Quickstart](https://code.claude.com/docs/en/quickstart)
来源：[Claude Code overview](https://code.claude.com/docs/en/overview)

### 需要谨慎看待的推文说法

1. 推文里提到的某些具体模型版本名，比如 “Opus 4.6” 等，是作者文章中的称呼。我没有在本次查阅的 Claude Code 官方文档中直接看到这些具体版本名与其完整能力说明，因此不能把这些版本标签当作我已独立核实过的官方结论。

2. 推文里关于“其他产品具体失败原因”的描述，大多来自作者自己的测试观察。除非拿到完整测试日志、相同环境复现实验，否则这些结论应理解为“实测体验反馈”，而不是通用且严格可复现的事实。

### 对你更有用的最新判断

截至 2026-03-03，可以比较确定的一点是：代理式编码工具的竞争重点，已经明显从“单轮答题”转向“工具调用、上下文管理、验证闭环、跨界面协作、可扩展能力”。Claude Code 官方文档把这些能力都放在核心位置，这说明行业方向确实在向“更完整的执行代理”收敛，而不是只拼回答文字本身。

## 新手上手建议

如果你是刚接触这类工具，不要被“吊打同行”这种结论先带跑。你真正应该学的是：怎么判断一个代理工具是不是适合你。

### 先学会看评测的正确姿势

以后你再看类似文章，优先看这 4 件事：

1. 测的到底是“模型本身”，还是“模型 + 工具链 + 客户端能力”。
2. 有没有统一环境和统一权限。
3. 作者是在比“好不好看”，还是比“能不能稳定交付”。
4. 有没有展示失败过程、日志、边界条件。

只要这 4 点没看清，标题里的“吊打”基本都只能当参考，不能当定论。

### 如果你想自己试 Claude Code，建议这样开始

先不要一上来就做大而全的自动化任务。先练一个小闭环：

1. 让它读一个页面或一组文件。
2. 让它总结内容。
3. 让它生成一个简单网页或文档。
4. 最后明确要求它自检。

你可以用这种思路下任务：

“请读取这个指定页面，只使用这个页面里的内容做总结。生成一个 Markdown 报告，并在完成后检查是否遗漏了图片中的关键信息。”

这样你先练的是“限定范围 + 指定输出 + 指定验证”，这比追求一次跑超级复杂任务更重要。

### 你应该重点观察的，不是它多会说，而是它会不会自检

对于新手来说，最有含金量的能力通常是：

1. 能不能在信息不全时自己换办法。
2. 能不能在完成后主动验证。
3. 能不能把任务拆开，而不是一把梭。

如果一个工具只是一次写很多字，但不会自己验证，那它在真实工作里很容易让你变成“最后的人工质检员”。

### 给你的一个实战入门模板

你以后让这类工具做复杂任务时，可以尽量用这个四段式：

1. 范围：只允许访问哪些页面、哪些文件。
2. 任务：要提取什么、分析什么、产出什么。
3. 约束：哪些链接不能跳、哪些资料不能补查。
4. 验证：做完后要怎么检查结果。

例如：

“只读取我给的两个官方页面。把文本和图片里的关键信息提取出来，写成对比报告，再生成一个单文件 HTML。完成后请启动本地预览并检查深色、浅色两种模式是否正常。”

这个模板会让代理工具的表现稳定很多。

### 最后给你的判断标准

如果一个代理工具同时满足下面三点，它通常就值得继续深用：

1. 资料拿得全。
2. 结果交得稳。
3. 做完会自查。

这比“某次跑分更高”“某个标题更夸张”更值得信。

## 参考来源

1. [Claude Code overview](https://code.claude.com/docs/en/overview)
2. [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)
3. [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
4. [Create plugins](https://code.claude.com/docs/en/plugins)
5. [Quickstart](https://code.claude.com/docs/en/quickstart)
