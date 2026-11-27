# 第3章：工具系统 -- Agent 的双手

> **开门一句话：**工具的名称、Schema、权限、执行与渲染构成共同契约，调度器据此安排调用。

> "If all you have is a hammer, everything looks like a nail."
> -- Abraham Maslow

**学习目标：** 读完这章，你能：

- 拿到 55 个已注册工具里的任何一个，认出五要素分别写在哪儿，说清少一条会在什么时候炸
- 用 `buildTool` 加一个自定义工具：schema、权限、执行、渲染各归各位，并跑通一次调用
- 给一串工具调用排出并发批次，说清哪些能同批、哪些必须排队，并讲出 StreamingToolExecutor 四个阶段各卡住什么

**难度定位：**主干章：3.1 是起步（五要素协议）；3.2、3.4 是主干；3.3 逐个拆核心工具，篇幅最长，标了进阶，初读可以只挑你常用的几个看，剩下的连同实战练习留给第二遍。

---

先看一次翻车：你让 Agent 读三个文件，再改其中一个。三次读取排成串行，你等了三倍时间；改文件和读文件挤进同一批，读回来的还是旧内容；你按中断，正在跑的工具停了，排在后面的照样启动。三个毛病都在同一层：工具怎么定义、怎么排队、怎么收场。

只有一个 Bash 工具时，读文件用 `cat`，搜索用 `grep`，编辑用 `sed`。能跑，但每一步都要绕开类型检查。Claude Code 注册了 55 个专门化工具（清单见附录 B），每个把输入约束、权限和执行语义写在自己的定义里。

## 3.1 工具定义协议

Claude Code 的每个工具都遵循一个统一的类型契约 -- `Tool<Input, Output, Progress>`。这个契约定义在工具类型核心模块中，每个工具都围绕名称、Schema、权限、执行和渲染五个维度定义自己。

这个协议的核心思路是“接口即架构”：严格的类型接口让编译器把权限检查、并发控制、进度报告、UI 渲染这些架构约束逐条卡住。开发者无法漏掉必需方法，漏写就会在编译阶段报错。

### 核心类型：Tool、Tools、ToolDef、buildTool

<!-- block: ch03.b-8c01f6c7 -->
`Tool` 类型是一个泛型接口，接受三个类型参数：

- `Input extends AnyObject`：使用 Zod schema 定义的工具输入类型，确保每个工具的输入都是一个结构化对象。
- `Output`：工具的输出类型，自由定义。
- `P extends ToolProgressData`：工具的进度数据类型，用于流式反馈。

<!-- block: ch03.tool-generics -->
三个泛型参数分开写，不是随手为之：如果输入和输出类型合并成一个，工具的签名会难读得多；如果省掉进度类型，工具就没法边执行边报进度。三者分开，每个关注点各占一块类型空间，编译器能分别检查。

<!-- block: ch03.b-4f610843 -->
每个工具必须实现的五要素如下：

```mermaid
flowchart TD
    subgraph protocol["Tool 五要素协议"]
        name["要素一：名称与别名<br/>唯一名称标识符 + 可选别名<br/>支持向后兼容"]
        schema["要素二：Zod Schema<br/>运行时验证 + API 通信<br/>类型安全屏障"]
        perm["要素三：权限模型<br/>validateInput → hasPermissions → checkPermissions<br/>三层分层检查"]
        exec["要素四：执行逻辑<br/>核心执行方法 + contextModifier<br/>上下文修改通道"]
        ui["要素五：UI 渲染<br/>六个渲染方法覆盖完整生命周期<br/>React 组件深度集成"]
    end

    name --> schema --> perm --> exec --> ui

    classDef element fill:#e8f4f8,stroke:#2196F3,stroke-width:2px,color:#1565C0
    class name,schema,perm,exec,ui element
```

**要素一：名称与别名**

每个工具拥有一个唯一的名称标识符，以及可选的别名用于向后兼容。当工具重命名时，旧名称可以通过别名继续匹配。工具查找函数同时检查主名称和别名。

别名机制的存在揭示了一个工程实践原则：**在公开 API 中，重命名是"只增不减"的操作。** 即使某个工具的名称不再准确（如从 `SearchTool` 重命名为 `GrepTool`），旧名称也必须通过别名保持可用，否则依赖旧名称的配置、脚本和用户习惯全得散架。

**要素二：Zod Schema**

每个工具使用 Zod 定义其输入参数的 schema。Zod schema 承担了双重职责：

<!-- block: ch03.b-fcffa808 -->
1. **运行时验证**：在工具执行之前，LLM 生成的参数经过 Zod 解析，确保类型和约束的正确性。按"不要信任外部输入"的原则，LLM 的输出不可控，工具必须自我保护。
2. **API 通信**：Zod schema 通过转换层生成 JSON Schema 发送给 API，让模型知道每个参数的含义和约束。参数描述就写在 Zod schema 的 `describe()` 调用里。

> **交叉引用：** Zod schema 的验证发生在第 4 章权限管线的第一阶段（validateInput），这是"安全边界内嵌"设计原则的具体体现。

**要素三：权限模型**

权限相关的三个方法构成了分层的权限检查管线：

1. **第一层：输入验证（validateInput）**：在权限检查之前运行，用于拒绝无效输入。这是"数据合法性"检查，与权限无关。
2. **第二层：权限检查（hasPermissionsToUseTool + checkPermissions）**：包含工具特定的权限逻辑。不同工具的权限检查粒度不同：Read 工具可能只检查路径是否在允许列表内，而 Bash 工具需要解析命令、评估风险等级。
3. **第三层：运行时属性判断**：影响工具的并发调度策略。例如 `isConcurrencySafe()` 标记工具是否可以并行执行。

<!-- block: ch03.b-00afc370 -->
三层分离的设计哲学是"关注点分离"：数据验证不关心权限策略，权限策略不关心并发调度。每层只做一件事，但三层串联起来提供了完整的防护。

**要素四：执行逻辑**

这是工具的核心执行方法。它接收解析后的输入参数、工具使用上下文、权限检查函数、父消息引用和一个可选的进度回调。返回的结果携带输出数据和可选的上下文修改器。

上下文修改器（contextModifier）让工具跑完再改上下文（如更新文件缓存），这是工具影响后续行为的关键通道。例如，FileWriteTool 在写入文件后会通过 contextModifier 更新文件状态缓存，后面的 FileReadTool 就能读到最新内容。

**要素五：UI 渲染**

工具拥有丰富的渲染方法集合，覆盖了完整的 UI 生命周期：

- `renderToolUseMessage`：工具调用开始时展示（如 "Reading src/foo.ts"）
- `renderToolUseProgressMessage`：工具执行中的进度展示
- `renderToolResultMessage`：工具结果展示
- `renderToolUseRejectedMessage`：权限遭拒时的展示
- `renderToolUseErrorMessage`：执行出错时的展示
- `renderGroupedToolUse`：多个并行工具的分组展示

每个渲染方法都返回 `React.ReactNode`，工具系统就此接进 React 的渲染管线。工具的 UI 表现能像 React 组件一样灵活，进度条、颜色高亮、折叠面板、表格布局都能写成组件。

六个渲染方法合起来，覆盖工具调用的"生老病死"：开始（renderToolUseMessage）、进行中（renderToolUseProgressMessage）、成功（renderToolResultMessage）、驳回（renderToolUseRejectedMessage）、出错（renderToolUseErrorMessage），以及并行执行时的分组展示（renderGroupedToolUse）。

<!-- block: ch03.b-e8a9e023 -->
### buildTool 工厂函数

`buildTool` 是创建工具的标准工厂函数。它接收一个部分工具定义，自动填充安全默认值。这些默认值遵循"fail-closed"原则：安全性相关的方法（如并发安全判断、只读判断）默认为 false，工具必须显式声明自己安全才能享受并发等优化。

机场安检就是这个原则的现场版：默认假设所有行李都要检查（fail-closed），只有经过特殊认证的旅客（如外交官）才能走快速通道。如果反过来——默认放行，只在发现问题时才拦截（fail-open）——那么任何一个漏检都可能造成安全事故。

类型系统通过类型计算，让开发者只需提供必要字段，而工厂函数的返回类型保证完整的工具接口。如果开发者在定义中提供了某个方法，类型系统会使用开发者提供的签名；如果省略了，则使用默认签名。工程实践中，简单工具只需几行代码，复杂工具可以完全自定义。

---

## 3.2 工具注册与动态发现

### getAllBaseTools() 完整工具清单

把内建工具想成一张工作台：每件家伙什只管一件事。

```ill
ch03-tool-bench
```

`getAllBaseTools()` 是所有内建工具的注册中心，返回一个扁平数组，装着 Claude Code 全部可用工具。按功能分类，核心工具清单如下：

<!-- block: ch03.b-86a622f2 -->
| 类别 | 工具 | 职责 | 并发安全 |
|------|------|------|---------|
| 执行 | BashTool | 运行 Shell 命令 | 否（副作用） |
| 文件 | FileReadTool, FileEditTool, FileWriteTool | 读取、编辑、写入文件 | Read 是，Edit/Write 否 |
| 搜索 | GlobTool, GrepTool | 文件名模式匹配、内容搜索 | 是 |
| 笔记本 | NotebookEditTool | Jupyter Notebook 编辑 | 否 |
| 网络 | WebFetchTool, WebSearchTool | 获取 URL 内容、网络搜索 | 是 |
| 智能 | AgentTool | 子智能体入口 | 否 |
| 任务 | TodoWriteTool, TaskCreateTool 等 | 任务管理 | 视具体工具而定 |
| 规划 | EnterPlanModeTool, ExitPlanModeV2Tool | 计划模式切换 | 否 |
| 交互 | AskUserQuestionTool | 向用户提问 | 否（需要用户响应） |
| 技能 | SkillTool | 调用 slash command 技能 | 否 |
| 配置 | ConfigTool | 修改配置 | 否 |
| MCP | ListMcpResourcesTool, ReadMcpResourceTool | MCP 资源访问 | 是 |
| 工作树 | EnterWorktreeTool, ExitWorktreeTool | Git worktree 管理 | 否 |
| 通知 | BriefTool | 消息发送 | 否 |
| 搜索发现 | ToolSearchTool | 延迟工具发现 | 是 |

> **设计洞察：** 注意"并发安全"列：超过一半的工具标记为并发不安全。这反映了一个工程现实：在 Agent 系统中，大多数操作都有副作用（修改文件、执行命令、更改状态），真正可以安全并行执行的操作（纯读取、纯搜索）是少数。并发分区算法（3.4 节）的核心挑战正是在这个约束下最大化并行度。

<!-- block: ch03.b-cd617d45 -->
### 死代码消除在工具注册中的应用

<!-- block: ch03.b-cfe9eded -->
Claude Code 的工具注册大量依赖条件导入，在编译期就消掉死代码。当特定条件不满足时，对应工具的整个模块就进不了最终构建。功能开关控制的工具也是如此。

<!-- block: ch03.b-b5c7ce30 -->
功能开关来自构建工具链，在编译时由 bundler 评估。开关一关，tree-shaking 就把对应工具的实现代码整段删掉。外部构建（面向第三方用户）里就没有内部工具的代码。

这个设计的意义首先落在安全上：把内部工具（如 REPL 工具、调试工具）放进外部构建，哪怕谁都调不到，也可能泄露内部架构信息。死代码消除从源头上消除了这种信息泄漏的风险。

在工具注册函数中，条件注册使用展开运算符，根据运行环境和功能开关决定是否加入特定工具。

### ToolSearchTool 延迟发现机制

<!-- block: ch03.b-70130a7e -->
当工具数量超过一定阈值时，Claude Code 启用延迟工具发现（deferred tool discovery）。核心思路是：不在初始系统提示中发送所有工具的完整 schema，而是只发送工具名称列表，让模型通过 ToolSearchTool 按需加载。

传统方式是把整本百科全书摊在模型面前，哪怕大部分内容在当前对话里用不到；延迟发现只给一本目录索引：模型知道有哪些工具可用，需要时再翻到对应页面看详细参数。

ToolSearchTool 的实现遵循标准的工厂函数模式。一个工具该不该延迟，判断逻辑是：显式标记为总是加载的工具不延迟、MCP 工具总是延迟、工具搜索工具自身不延迟。

<!-- block: ch03.b-62e9add3 -->
延迟发现可以节省初始 prompt 的空间：MCP 服务器注册了数十个工具时，不必一开始就向 API 发送全部完整 schema，模型需要某个工具时再加载。实际节省多少，取决于工具定义的长度和本次任务用到的工具。

工具 schema 本身也吃 token：名称、描述、参数定义都要随工具列表发出去，工具上到 50 个就可能占掉几千 token。延迟发现是省钱的那一手。

### 工具过滤管线

从 `getAllBaseTools()` 到最终发送给 API 的工具列表，经过多层过滤：

```mermaid
flowchart LR
    all["getAllBaseTools()<br/>所有内建工具"] --> mode["模式过滤<br/>简单/普通模式筛选"]
    mode --> deny["拒绝规则过滤<br/>移除 blanket deny 工具"]
    deny --> enabled["启用状态检查<br/>过滤未启用工具"]
    enabled --> pool["工具池组装<br/>合并内建 + MCP<br/>按名称排序去重"]
    pool --> api["发送给 API 的工具列表"]

    classDef filter fill:#e8f4f8,stroke:#2196F3,stroke-width:2px,color:#1565C0
    classDef result fill:#f0fdf4,stroke:#22c55e,stroke-width:2px,color:#166534
    class all,mode,deny,enabled,pool filter
    class api result
```

<!-- block: ch03.b-547be657 -->
1. **模式过滤**：根据模式过滤工具。简单模式只保留 Bash、Read、Edit；普通模式排除特殊工具。受限环境里，Agent 手上就只剩这套最基本的工具集。
2. **拒绝规则过滤**：去掉 blanket deny 规则点到的工具。
3. **启用状态检查**：过滤掉未启用的工具。
4. **工具池组装**：合并内建工具与 MCP 工具，按名称排序去重。排序是为了保住 prompt 缓存的稳定性。工具顺序一变，就会造成缓存失效。

> **交叉引用：** 模式过滤和拒绝规则过滤与第 4 章的权限管线紧密相关。工具过滤是权限系统的第一道防线（工具可见性过滤），确保模型甚至无法"看到"它不应该使用的工具。

---

## 3.3 核心工具深度解析

### BashTool：命令执行的瑞士军刀

BashTool 是 Claude Code 里最复杂的工具。它不是简单的 Shell 执行器，身上叠了多层安全防护。如果工具系统是 Agent 的双手，BashTool 就是其中最有力的那只手，也是最要管住的那只。

BashTool 的特别之处有四处。先看这张图，再逐条说：

```mermaid
flowchart LR
    bt["BashTool"] --> err["错误传播<br/>一条命令失败<br/>同批并行的 Bash 调用全部取消"]
    bt --> cut["中断行为<br/>由工具自己定义<br/>立即停止，或阻塞到结束"]
    bt --> sem["语义分析<br/>先判断命令是搜索还是读取<br/>再决定界面怎么折叠"]
    bt --> box["沙盒集成<br/>bypass 权限模式下<br/>仍能限制文件系统访问"]

    classDef core fill:#fef2f2,stroke:#ef4444,stroke-width:2px,color:#991b1b
    classDef leaf fill:#fff3cd,stroke:#f39c12,color:#664d03
    class bt core
    class err,cut,sem,box leaf
```

<!-- block: ch03.b-61c799a2 -->
- **错误传播**：当 BashTool 执行失败时，会取消所有并行的 Bash 工具调用。这是因为 Bash 命令之间往往存在隐式依赖链（如 `mkdir` 失败后后续命令无意义）。这一条按"快速失败"办：与其让后续命令在一个已损坏的环境里继续跑、生出更多错误，不如立即停掉整个批次。

- **中断行为**：BashTool 可以自定义用户中断时的行为。某些长时间运行的命令（如测试套件）可能选择阻塞而非取消。这个设计分得清两种打断：中断一个正在运行的 `npm install` 应该立即停止（用户改了主意），但中断一个测试套件可能只是用户想看当前进度（测试完成后结果仍然有价值）。

- **语义分析**：BashTool 会解析命令的 AST、再做语义分析，判断命令是否为搜索/读取操作（`isSearchOrReadCommand`），用于 UI 折叠展示。工具在这里不止是把命令转手交给 shell 的管道：它先读懂命令在做什么，再决定界面怎么收放。

- **沙盒集成**：通过 `--dangerouslyDisableSandbox` 参数和沙盒配置，控制命令执行的安全边界。沙盒是 BashTool 的"安全网"：即使在 bypass 权限模式下，沙盒仍然可以限制命令的文件系统访问范围。

### 文件三件套：FileReadTool、FileEditTool、FileWriteTool

这三个工具构成了 Claude Code 文件操作的完整能力集。它们的分工反映了经典数据库操作的 CRUD 模式（Create/Read/Update），只是缺少了 Delete。这是有意为之的安全决策："删除文件"是不可逆操作，通常走 BashTool 的 `rm` 命令，这会触发更严格的权限检查。

**FileReadTool** 负责读取文件内容。它维护了文件状态缓存，用于追踪哪些文件已经读过，避免重复注入内存附件。缓存是这里的关键：同一文件在多个轮次里反复读取时，只有第一次触发真实 I/O，之后都走缓存。

**FileEditTool** 负责精确编辑文件。它使用 `old_string -> new_string` 的精确替换模式，而非行号范围，确保编辑操作在文件变化时仍然正确。这个选择的影响如下：

<!-- block: ch03.b-b075e65d -->
- **为什么不用行号？** 行号是脆弱的：如果在读取和编辑之间，另一个工具（或用户）动了文件，行号可能已经偏移，编辑就落到错误的位置。
- **为什么用精确字符串匹配？** 字符串匹配是幂等的：只要目标片段还在文件里，编辑就能正确定位。即使文件改了一部分，只要目标片段没动，编辑就是安全的。

<!-- block: ch03.b-e503443c -->
FileEditTool 的 `isDestructive` 方法会根据编辑内容判断是否为破坏性操作（如删除大量代码）。这种上下文感知的破坏性判断比简单的"写入即破坏性"标签更加精确。

**FileWriteTool** 负责创建或完全覆写文件。这是最"重"的文件操作，权限检查最为严格。FileWriteTool 与 FileEditTool 的区别在于作用范围：Edit 只修改文件中的特定片段，Write 可以完全覆盖文件内容。因此，Write 的权限检查标准更高。

三个工具都带 `contextModifier`，在执行后更新文件状态缓存，后续的工具调用和内存附件注入就能看到最新的文件状态。

```mermaid
flowchart LR
    t0["文件三件套<br/>Create / Read / Update<br/>独缺 Delete"] --> rd["FileReadTool<br/>记住哪些文件读过<br/>重复读取直接命中缓存"]
    t0 --> ed["FileEditTool<br/>old_string → new_string<br/>按内容定位，不怕行号偏移"]
    t0 --> wr["FileWriteTool<br/>整文件覆写<br/>权限检查最严"]
    t0 -.-> rm["删除不在三件套里<br/>改走 BashTool 的 rm"]

    classDef trio fill:#e8f4f8,stroke:#2196F3,stroke-width:2px,color:#1565C0
    classDef light fill:#f0fdf4,stroke:#22c55e,color:#166534
    classDef heavy fill:#fef2f2,stroke:#ef4444,color:#991b1b
    class t0 trio
    class rd,ed light
    class wr,rm heavy
```

<!-- block: ch03.b-275ecc1e -->
工具设计按最小权限来：能用 Edit 就别用 Write，能用 Read 就别用 Bash。这一条安全和效率两头占——精确的 Edit 比 Write 整个文件快，也更不容易出错。

### 搜索双雄：GlobTool 与 GrepTool

**GlobTool** 使用文件名模式匹配查找文件，底层使用 `fast-glob` 库。它返回匹配的文件路径列表，支持 ignore 模式和最大结果数限制。

<!-- block: ch03.b-5893ad9f -->
**GrepTool** 使用正则表达式搜索文件内容，底层使用 `ripgrep`。它支持多种输出模式（文件名、内容行、计数），以及丰富的过滤选项（文件类型、glob 模式等）。

这两桩搜索没有交给 BashTool 代劳。BashTool 虽然也能用 `find` 和 `grep` 命令做出类似结果，但专门的搜索工具有几个优势：

1. **结构化输出**：搜索工具返回结构化的结果列表，而非 Shell 命令的文本输出。模型可以更准确地解析结构化数据。
2. **权限控制**：搜索工具默认是只读的，权限检查更宽松。如果每次搜索都需要通过 BashTool，用户将面临更多的权限确认提示。
3. **性能优化**：专门的搜索工具可以针对特定场景优化（如限制结果数量、并行搜索），而 Shell 命令的优化空间有限。

当 Ant 原生构建中嵌入了专用的快速搜索工具时，Claude Code 会关掉 GlobTool 和 GrepTool，因为 Shell 里的 `find` 和 `grep` 已经别名到这些快速工具，BashTool 可以直接使用它们。

### AgentTool：子智能体入口

<!-- block: ch03.b-609ffc7f -->
AgentTool 是 Claude Code 多智能体协作的核心工具。它允许主智能体生成子智能体来处理子任务。子智能体拥有独立的上下文窗口和工具集，执行完成后将结果返回给主智能体。

AgentTool 在工具系统中有几个特殊属性：
<!-- block: ch03.b-f7f89dc9 -->
- 它可能带有 `alwaysLoad` 标记，确保在 ToolSearch 启用时仍然在第一轮可见。这是因为子智能体是处理复杂任务的关键能力，不该让延迟发现机制把它藏起来。
- 子智能体通过 `createSubagentContext` 创建独立的 `ToolUseContext`，继承父上下文的部分状态（如权限规则）但拥有独立的消息列表。子智能体不会意外修改父智能体的状态。
- 子智能体的结果通过 `TaskOutputTool` 暴露给主智能体。

---

## 3.4 工具编排引擎

工具编排引擎是工具系统的"指挥中心"。它决定多个工具调用怎么排队、怎么跑、结果怎么收回来。编排引擎要同时顾住三个目标：**并行性**（尽可能并行执行以提高速度）、**安全性**（避免并发执行导致的数据竞争）和**顺序性**（保证结果的产出顺序与请求顺序一致）。

### runTools() 函数与并发分区

工具编排的核心逻辑在工具编排模块中。`runTools` 函数是一个异步生成器，负责调度一批工具调用的执行。

<!-- block: ch03.b-6ba1c508 -->
它按 **并发分区**（concurrency partitioning）来排工具：

1. 首先将所有工具调用按顺序划分为批次。
2. 每个批次要么是一组连续的并发安全工具，要么是一个单独的非安全工具。
3. 并发安全批次并行执行。
4. 非安全批次串行执行。

分区算法的核心逻辑：遍历所有工具调用，检查每个工具的并发安全属性。如果当前工具安全且前一个批次也安全，则合并到同一批次；否则开启新批次。

想象一条工厂流水线：有些工序独立（如同时检查多个零件），可以并行；有些必须按顺序（先组装再测试），不能跳跃。并发分区算法就是这条线的调度员，自动认出哪几道能并行、哪几道必须串行。下面的四格胶片把它跑了一遍：调用排成队、按安全性切成两批、安全的那批同时开工、结果按请求顺序报号。

```ill
ch03-tool-pipeline
```

举例来说，如果模型请求了四个工具调用：`[Read(a.ts), Read(b.ts), Bash(ls), Read(c.ts)]`，分区结果为：

```mermaid
flowchart LR
    subgraph input["输入序列"]
        direction LR
        t1["Read(a.ts)<br/>安全=是"] ~~~ t2["Read(b.ts)<br/>安全=是"] ~~~ t3["Bash(ls)<br/>安全=否"] ~~~ t4["Read(c.ts)<br/>安全=是"]
    end

    subgraph b1["Batch 1: 并发安全 = true — 并行执行"]
        direction LR
        b1a["Read(a.ts)"] ~~~ b1b["Read(b.ts)"]
    end

    subgraph b2["Batch 2: 并发安全 = false — 串行执行"]
        b2a["Bash(ls)"]
    end

    subgraph b3["Batch 3: 并发安全 = true — 并行执行"]
        b3a["Read(c.ts)"]
    end

    input --> b1 --> b2 --> b3

    classDef safe fill:#f0fdf4,stroke:#22c55e,stroke-width:2px,color:#166534
    classDef unsafe fill:#fef2f2,stroke:#ef4444,stroke-width:2px,color:#991b1b
    class t1,t2,t4,b1,b1a,b1b,b3,b3a safe
    class t3,b2,b2a unsafe
```

```mermaid
flowchart LR
    subgraph timeline["执行时间线"]
        direction LR
        batch1["Batch 1: Read(a.ts) ‖ Read(b.ts)"]
        batch2["Batch 2: Bash(ls)"]
        batch3["Batch 3: Read(c.ts)"]
    end

    batch1 --> batch2 --> batch3

    note["注意：Batch 3 必须等 Batch 2 完成<br/>因为 Bash 可能有副作用"]

    classDef batch fill:#f0f7ff,stroke:#3b82f6,stroke-width:2px,color:#1e3a5f
    class batch1,batch2,batch3 batch
```

并发执行的并发度上限由环境变量控制，默认为 10。

> **设计洞察：** 为什么 Read(c.ts) 不能和 Bash(ls) 放在同一个批次？因为 Bash 命令可能有副作用：它可能创建新文件、修改文件内容或改变目录结构。如果在 Bash 执行的同时读取文件，Read 可能读到执行前的旧数据或执行后的新数据，导致不可预测的行为。串行执行让 Read(c.ts) 看到的是 Bash(ls) 跑完之后的确定状态。

### StreamingToolExecutor 流式执行

<!-- block: ch03.b-0d31e19e -->
`StreamingToolExecutor` 是 `runTools` 的增强版本，它不等待模型响应完全结束就开始执行工具，而是在流式接收到工具调用块时就立即启动执行。

收益可以算出来。假设模型在一个响应中请求了五个工具调用，每个工具执行需要 1 秒。传统模式下，模型生成完整响应需要 2 秒（流式输出时间），然后批量执行工具需要 5 秒，总计 7 秒。流式执行模式下，第一个工具在模型输出开始后约 0.4 秒（生成第一个 tool_use 块的时间）就开始执行，后续工具陆续启动，总计约 3 秒——速度提升超过 50%。

每个进入追踪的工具拥有四阶段状态机：

```mermaid
stateDiagram-v2
    [*] --> queued : 工具入队
    queued --> executing : 执行条件满足
    executing --> completed : 执行完成
    completed --> yielded : 顺序轮到输出
    yielded --> [*] : 生命周期结束

    note_right of queued : 等待执行条件满足
    note_right of executing : 检查并发条件<br/>无工具在执行或全部并发安全时启动
    note_right of completed : 等待顺序轮到输出
    note_right of yielded : 结果已产出
```

- **queued**：工具已入队，等待执行条件满足。
- **executing**：正在执行。执行前会检查并发条件：只有当没有工具在执行，或所有执行中的工具都是并发安全时，才允许开始执行。
- **completed**：执行完成，结果已收集。但尚未 yield 给上层（需要维持顺序）。
- **yielded**：结果已产出，工具生命周期结束。

StreamingToolExecutor 的关键设计决策：

<!-- block: ch03.b-4e9dde41 -->
1. **顺序保证**：即使在流式执行中工具可以并行完成，结果的 yield 仍然保持与请求相同的顺序。结果收集函数在遍历工具列表时，遇到未完成的非安全工具就会停止，确保顺序约束始终成立。工具尽管并行跑，结果仍按请求顺序交出，上层处理逻辑因此简单。

2. **错误传播**：BashTool 执行失败会取消所有并行兄弟工具。非 Bash 工具的错误不会传播，因为读取和搜索操作通常彼此独立。这个区分很重要：Bash 命令的失败通常意味着环境出了问题（如磁盘满了、网络断了），此时继续执行其他命令很可能也会失败。而文件读取或搜索操作的失败通常是局部的（如文件不存在、模式不匹配），不影响其他操作。

3. **进度即时产出**：工具执行中的进度消息绕过顺序约束，立即 yield 给上层。UI 能实时显示工具执行进度，不必等前面的工具完成。顺序上的取舍按消息性质分开：进度消息是"提示性"的，不需要严格的顺序保证；结果消息是"事实性"的，必须保持顺序。

4. **丢弃机制**：当流式回退发生时（模型切换到 fallback 模型），标记所有待执行和执行中的工具为废弃，避免过时的结果泄漏。这相当于一个"紧急刹车"：当模型决定改变策略时，旧策略下发出的工具调用结果，全都该丢掉。

5. **信号传播**：每个工具执行使用独立的子取消控制器，形成层级化的取消信号链。兄弟工具的错误或用户的 Ctrl+C 都会通过信号传播到正确的工具。这种层级化的信号传播确保了取消操作的精确性——取消一个工具不会意外影响不相关的其他工具。

<!-- block: ch03.b-36dc869c -->
别用一个 AbortController 管所有工具的取消：工具 A 失败要取消 B 时，无关的 C 也会被一起掐掉。取消信号要分层，一层管一层。

工具这一层出错的位置很固定，就这几处。下面把常见写法和对应的改法列在一起，括号里标了出处。

| 常见翻车 | 正确做法 |
|:--------:|------|
| 工具函数里自己 `JSON.parse` 模型给的参数 | 执行前交给 Zod schema 校验（3.1 要素二） |
| 一把 Bash 打天下：`cat`、`grep`、`sed` 全包 | 按操作类型分工，Read、Glob、Grep、Edit 各管一段（3.3） |
| 改文件永远用 Write 整份覆盖 | 优先 Edit 做精确改动，Write 留给真要换整份的时候（3.3） |
| 所有工具一律塞进请求，工具一多 token 就涨 | 只带当前用得上的，其余走 ToolSearchTool 延迟发现（3.2） |
| 一个 AbortController 管所有工具的取消 | 取消信号分层，A 失败不牵连无关的 C（3.4） |

> **交叉引用：** 同一双手在另一套 harness 里干活的现场，参见 omp 分册第 8 章《读与找》。

### 工具状态机在对话主循环中的集成

回到对话主循环，工具执行的状态与对话循环的状态紧密集成：

1. **流式执行路径**：当流式工具执行功能启用时，创建 StreamingToolExecutor。在流式接收工具调用块时，立即将工具加入执行队列，同时检查是否有已完成的结果可以立即 yield。这就是"边接收边执行"的流水线。

2. **批量执行路径**：当流式执行不可用时，使用传统的批量执行函数在模型响应完全结束后批量执行所有工具。这是流式执行的后备方案，保证了在流式功能关掉或出问题时系统仍然可以正常工作。

3. **上下文传播**：工具执行后可能修改上下文（如文件缓存更新），这些修改传播回对话循环，影响后续工具的执行环境。上下文传播是"一致性"的关键：如果工具 A 写了文件而缓存没更新，后面的工具 B 就可能拿着旧缓存做决定。

> **交叉引用：** 流式执行路径与第 2 章的对话主循环阶段三和阶段四紧密集成。对流式执行的理解需要结合对话主循环的整体流程图来把握。

---

## 实战练习

**练习 1：实现一个自定义工具**

使用 `buildTool` 工厂函数创建一个简单的工具。要求：
- 定义 Zod schema，包含一个 `path` 字段（字符串类型）
- 实现 `call` 方法，返回指定路径的文件信息
- 正确标记 `isReadOnly` 和 `isConcurrencySafe`
- 实现 `renderToolUseMessage` 和 `renderToolResultMessage`

对比你的实现与 FileReadTool 的差异，理解 `buildTool` 默认值的作用。

**思考题：** 你的自定义工具的 `isConcurrencySafe` 应该标记为 true 还是 false？如果标记错误（只读工具标记为 false，或写入工具标记为 true），分别会导致什么问题？

**练习 2：分析并发分区策略**

给定以下工具调用序列：
```
[GlobTool(*.ts), GrepTool(pattern), BashTool(npm test), FileReadTool(a.ts), FileEditTool(a.ts), GlobTool(*.json)]
```

手动执行 `partitionToolCalls` 的逻辑，画出批次划分结果。然后思考：为什么 FileEditTool 和 GlobTool 不能放在同一个并发批次？

**详细分析：** 画出每个工具的安全标记，然后逐步模拟分区算法的决策过程。最终答案应该是：

```
Batch 1 (并发安全): [GlobTool(*.ts), GrepTool(pattern)]   -- 并行执行
Batch 2 (非安全):   [BashTool(npm test)]                    -- 串行执行
Batch 3 (并发安全): [FileReadTool(a.ts)]                    -- 串行执行（受 Batch 2 影响不能并入 Batch 1）
Batch 4 (非安全):   [FileEditTool(a.ts)]                    -- 串行执行
Batch 5 (并发安全): [GlobTool(*.json)]                      -- 可并行（但只有一个工具）
```

**练习 3：追踪 StreamingToolExecutor 的生命周期**

在 StreamingToolExecutor 的工具入队、工具执行和结果获取环节设置断点。发送一个触发多个并行工具调用的请求（如"搜索所有 TODO 注释并读取相关文件"），观察工具状态如何从 queued 到 executing 到 completed 再到 yielded，以及进度消息如何即时产出。

**扩展观察：** 在工具执行期间按 Ctrl+C，观察取消信号如何从用户传播到各个工具。注意层级化的取消控制器如何确保取消只落在正在执行的工具上，而已经 completed 的工具结果不受影响。

**练习 4：评估延迟发现的性能影响**

如果你的环境接入了 MCP 服务器，观察以下两种情况下的 API 调用 token 消耗差异：
- 禁用延迟发现（所有工具 schema 都在初始 prompt 中）
- 启用延迟发现（只有工具名称列表在初始 prompt 中）

记录两种情况下的 input token 数量差异，计算延迟发现为你节省了多少 token。

**最小可运行案例：** 用一张必需参数表复刻工具注册与分派（Python 3.12 标准库，无第三方依赖；这是教学简化模型，不是 Claude Code 源码）。把代码存成 `case.py` 后运行 `python case.py`。

**版本锁：** Python 3.12 标准库，无第三方依赖。
**预期结果：** 两行：`ok: Read` 与 `reject: Write missing content`
**前置：** 第 2 章的循环；**回链：** 第 2 章的 `tool_use` 事件

```python
# exercise: ch03
# expected:
# ok: Read
# reject: Write missing content
TOOLS = {"Read": ["path"], "Write": ["path", "content"]}
def dispatch(name, args):
    missing = [key for key in TOOLS[name] if key not in args]
    return f"reject: {name} missing {','.join(missing)}" if missing else f"ok: {name}"
print(dispatch("Read", {"path": "a.txt"}))
print(dispatch("Write", {"path": "a.txt"}))
```

---

## 关键要点

1. **五要素协议决定工具系统的主干**：名称、Schema、权限、执行、渲染。每个工具围绕这五个维度定义，而 `buildTool` 的默认值让简单工具只需写核心逻辑。协议遵循“显式声明，安全默认”：工具必须主动声明自身安全，否则按不安全处理。

2. **死代码消除保障构建安全**：环境变量和功能开关决定构建时导入哪些模块，内部工具就进不了外部构建。这是 Agent 系统在多租户环境下的重要工程实践。结合第 1 章的"渐进式能力扩展"原则，死代码消除让不同产品形态能共享同一份代码库。

<!-- block: ch03.b-86ccfc32 -->
3. **并发分区是性能的关键**：`isConcurrencySafe` 的判断决定了工具能否并行执行。正确标记只读工具为并发安全，可以让 Agent 在单轮中同时执行多个搜索/读取操作，大幅减少响应时间。但标错的代价是数据竞争和不可预测的行为，值得谨慎权衡。

<!-- block: ch03.b-8108b397 -->
4. **StreamingToolExecutor 是零等待的工具调度器**：在模型还在生成 tool_use 块时就开始执行工具，靠四阶段状态机和顺序保证，工具并行跑，顺序一点不乱。它是"异步流式优先"这条设计原则落到工具系统上的样子。

5. **工具系统的可扩展性来自类型契约**：`Tool<Input, Output, Progress>` 的泛型设计让每个工具有独立的类型空间，而 `ToolUseContext` 提供了统一的执行环境。添加新工具不需要修改编排引擎的代码——第 1 章讲的"渐进式能力扩展"原则，就在这里兑现了。

> ①新增工具时，写清名称、Schema、权限、执行和渲染五项契约。②根据读写副作用设置并发属性，检查同批调用会不会互相影响。③测试失败与中断路径，确认后续排队工具的处理方式。

下一章讲 Agent 的安全护栏——权限管线。工具系统让 Agent 能动手，权限管线决定哪些动作被允许执行。
