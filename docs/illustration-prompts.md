# 插图再生手册 —— 26 份手绘插图的双语生图提示词

本书 26 份插图（章徽、篇题刻、老驿卒、扉页车图）以开源项目
[yang0/handraw-style](https://github.com/yang0/handraw-style) 的画风体系绘制：
基准配方为 `FD-001 · Yuko Shimizu | Dynamic East-Asian Ink Editorial` 画风，
`C-32 炭黑（Charcoal Black）` 统领、`C-15 朱砂红（Cinnabar Red）` 点缀
（朱砂仅用于章印与书级点缀，不在画面内）。本手册按该项目的输出规范给出
每份插图的中英双语再生提示词：把它们整段粘贴进任意生图模型（gpt-image、
Midjourney、Flux 等），即可在别的媒介重制同一幅图，或为未来新增章节
以同一支笔续画。

> 规范要点（沿上游 skill）：提示词内不出现任何编号；只写正向特征；
> 参考作者/风格名称是索引标签而非模仿指令；默认不出图，由生图模型决定成败。

垫图（可选）：仅当生图模型对风格名不敏感时，垫入上游完整安装的 `images/individual/FD/FD-001.webp`（yang0/handraw-style 仓库），并附隔离指令：只提取画风，不沿用画面内容。

## 基准配方

- 风格：`FD-001 · Dynamic East-Asian Ink Editorial`（流动墨线、东方笔意、明显手绘笔压、
  停顿与轻微不齐整感、书写性与留白意识）
- 主题色：C-32 炭黑统领 + C-15 朱砂点缀（章印/首字）
- 画幅习惯：章徽 64×64、篇题刻 200×140、扉页 1000×470、章末驿卒 64×64

## 逐图提示词

### 前言 · `front.svg`

**隐喻**：折叠舆图上一条虚线驿路

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一幅对折再对折的古舆图摊开，纸面四道折痕，一条虚线驿路自左下蜿蜒至右上，尽头一枚实心墨点与一圈细环。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
An old folded atlas map spreads open with four crease lines; a dotted post road winds from lower left to upper right, ending in a solid ink dot inside a fine ring.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 1 章 · `ch01.svg`

**隐喻**：罗盘——重新瞄准的编程范式

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一只手绘罗盘：外环留缺口，内环虚线，四正四隅细辐，盘心一枚墨点套细环，像刚被指尖拨过。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A hand-drawn compass: the outer ring left open, a dotted inner ring, eight fine spokes, an ink dot at the center inside a thin ring, as if just flicked by a fingertip.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 2 章 · `ch02.svg`

**隐喻**：对话循环——心跳回路

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两段弧线首尾相逐成环，各带一枚小箭头，中心一枚实心墨点，像心跳的两个半拍。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Two arcs chase each other into a circle, each carrying a small arrowhead; a solid ink dot at the center marks the beat between beats.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 3 章 · `ch03.svg`

**隐喻**：工具系统——六角螺母

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一枚六角螺母，轮廓留笔势缺口，内孔一只圆环，盘心墨点，右上角一抹排线灰面。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A hexagonal nut with open corners, a round bore, an ink dot at the center, and a small patch of hatched shading at the upper right.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 4 章 · `ch04.svg`

**隐喻**：权限管线——护栏勾选

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两道护栏立柱之间一道有力的勾选线，像验讫的封印，立柱上各一枚铆点。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A bold checkmark drawn between two guardrail posts like an approval seal, a rivet dot on each post.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 5 章 · `ch05.svg`

**隐喻**：设置与配置——层叠菱面

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
三层菱面自上而下叠落，顶层实、下两层渐淡，像配置在层层沉降。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Three diamond planes stack downward, the top one solid and the lower two fading, like configuration settling layer by layer.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 6 章 · `ch06.svg`

**隐喻**：记忆系统——折角册页

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一页折角文档，三行墨迹行文，右下一笔小注与一枚墨点，像刚写完的记忆。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A document with a folded corner, three lines of ink writing, a small note and an ink dot at the lower right—a memory just written down.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 7 章 · `ch07.svg`

**隐喻**：上下文管理——量器

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一只半圆量器，三枚刻度，指针斜指右上方，像工作记忆正被度量。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A semicircular gauge with three ticks, its needle swept toward the upper right, measuring working memory.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 8 章 · `ch08.svg`

**隐喻**：钩子系统——生命周期挂钩

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一条基线上三枚节点，上方一道挂钩折线带垂弧，下方一行渐淡的回声，一枚箭头指向前方。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A baseline with three nodes; above it a bracketed hook line with a hanging swag; below, a fading echo; an arrow points ahead.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 9 章 · `ch09.svg`

**隐喻**：子智能体——一源三枝

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一个源环向右上、右下各分出一枝，各落一枚歪圆环，分叉处一枚小墨点。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
One source ring forks to the upper and lower right, each branch ending in its own lopsided ring; a tiny ink dot marks the fork.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 10 章 · `ch10.svg`

**隐喻**：协调器——枢纽列站

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
中心一枚墨环向四角各引一条细线，尽头四枚虚线小环，像列站的驿站。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A central ink ring sends four fine lines to the corners, each ending in a small dashed ring like way stations.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 11 章 · `ch11.svg`

**隐喻**：技能系统——侧挂面板

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一页文档右侧挂一块面板，两根引线各连一枚墨点，面板下两笔排线灰面。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A document with a side panel attached; two leads each end in an ink dot; two hatch lines shade the panel's foot.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 12 章 · `ch12.svg`

**隐喻**：MCP 集成——双杆一线

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两根立杆顶端各一枚绝缘墨点，一条垂弧双线跨接其间，两侧斜拉线落地，地面三段短划。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Two poles topped with insulator dots; a sagging double wire spans between them; guy lines brace to the ground of three dashes.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 13 章 · `ch13.svg`

**隐喻**：流式架构——漏斗汇流

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
三股墨流自左汇入一只漏斗，颈口一滴悬而未落，右侧罐体已积半管墨，双箭头向外流去。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Three ink streams pour into a funnel from the left; a drop hangs at the neck; the tank at right has filled halfway, two arrows flowing out.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 14 章 · `ch14.svg`

**隐喻**：Plan 模式——虚线远路

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一条虚线远路自一枚墨点起伏而去，尽头旗杆上一面燕尾旗，路线越远越细。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A dotted road rises and falls away from an ink dot, ending at a swallow-tailed flag on its pole.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 15 章 · `ch15.svg`

**隐喻**：构建 Harness——辘轳绕绳

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一架辘轳：人字架、轴上绕绳鼓、摇柄斜出，垂绳吊着一只小斗。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A well-windlass: an A-frame, a rope drum on its axle, a crank handle out to the side, a rope lowering a small bucket.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 A · `apxa.svg`

**隐喻**：源码导航——格上定位

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一张淡格舆图，中央一只歪圆定位环，四向短刻度伸出格外，环心一枚墨点。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A faint gridded map with a lopsided locator ring at the center, four short ticks reaching past the grid, an ink dot inside.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 B · `apxb.svg`

**隐喻**：工具清单——逐项核对

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
三行勾选清单，勾线一笔写成、粗细不匀，行线渐短，像逐项核对的工具清单。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A three-row checklist, each check drawn in one uneven stroke, the ruled lines shortening, as if ticking off tools one by one.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 C · `apxc.svg`

**隐喻**：功能标志——拨杆开关

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一枚手绘拨杆开关，胶囊外壳歪圆，旋钮拨向右侧并带一圈虚线残影，像刚被拨动。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A hand-drawn toggle switch: a lopsided capsule, the knob thrown to the right with a dashed halo, as if just flipped.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 D · `apxd.svg`

**隐喻**：术语表——侧订册页

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一册侧订小书，右侧两枚书签耳，三行词条墨迹，书脊一道淡影。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A side-stitched booklet with two bookmark tabs, three lines of entry writing, a soft shadow along the spine.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 章末按语·老驿卒 · `keeper.svg`

**隐喻**：老驿卒——章末按语伴立

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一位戴斗笠的老驿卒侧身而立，衣摆两笔，背一只行囊，手提一盏圆灯笼，灯笼里一线火苗。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
An old courier in a bamboo hat stands in profile: two strokes for the robe, a satchel on his back, a round lantern in hand with a line of flame inside.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 一 篇题刻 · `part-p1.svg`

**隐喻**：基础篇——大罗盘

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一面大罗盘铺满纸面，十六根长短不齐的辐条，双层环圈，盘心一枚墨点，地平线一笔拖过。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A great compass rose fills the sheet: sixteen uneven spokes, double rings, an ink dot at its heart, a single horizon stroke beneath.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 二 篇题刻 · `part-p2.svg`

**隐喻**：核心系统篇——箱匣

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一只圆盖箱匣正面而立，两道革带勒紧，锁孔居中，右旁一面小罗盘相照。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A round-lidded chest stands front on, two straps cinched tight, a keyhole at center, a small compass rose beside it.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 三 篇题刻 · `part-p3.svg`

**隐喻**：高级模式篇——山径

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两道山坡线夹出垭口，一条虚线山径串起三枚大小渐小的环，如驿站相望。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Two slope lines pinch a mountain pass; a dotted path strings three rings, each smaller than the last, like stations in sight of one another.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 四 篇题刻 · `part-p4.svg`

**隐喻**：工程实践篇——牌坊驿道

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一座两柱横梁的小牌坊，檐口一道弧线，右旁一道直角驿道伸向远处。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A small two-post gateway with a curved lintel; beside it a right-angled post road runs toward the distance.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 扉页·四马古车 · `cover.svg`

**隐喻**：扉页——四马古车

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一乘四马单辕古车：圆盖三十辐如伞张开，车厢内立戈，御者拱手执辔，车轮十八辐落地，两道云气自后掠过。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A four-horse chariot of antiquity: a round canopy of thirty ribs opens like an umbrella; a dagger-axe stands in the box; the driver holds the reins; an eighteen-spoke wheel meets the ground; two wisps of cloud sweep past behind.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

## 为新增章节续画（模板）

1. 从章节标题提炼一个可入画的隐喻（一个物件，不画界面截图）；
2. 按实时研判从 [yang0/handraw-style](https://github.com/yang0/handraw-style)
   的 367 风格与 36 主题色中重新推荐组合（不写死映射），并附一句具象美学理由；
3. 把上面的基准配方换成新组合，场景句套用本模板；
4. 成图后转为手写 SVG 时遵守 `yuyu-book/yuyu_book/art.py` 硬契约：
   单 svg + viewBox、至少一处 `currentColor`、禁 id/href/url/script/style、
   单元图 ≤ 6000 字节（封面 ≤ 20000）、质感只能来自几何笔触。

---

画风体系来源：[yang0/handraw-style](https://github.com/yang0/handraw-style)
（MIT with Attribution，原作者 yang0）。本手册的提示词规范沿其 skill 输出约定。