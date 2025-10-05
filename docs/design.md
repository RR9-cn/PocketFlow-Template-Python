# Design Doc: AI Novel Auto-Generation System

> Please DON'T remove notes for AI

## Requirements

> Notes for AI: Keep it simple and clear.
> If the requirements are abstract, write concrete user stories

基于 PocketFlow 框架实现一个 AI 小说自动生成与发布系统，主要功能包括：

1. **AI 小说生成**：使用 Google Gemini API 自动生成符合特定格式的小说内容
2. **内容验证**：对生成的小说进行多重质量检查（格式、字数、语法等）
3. **自动发布**：通过浏览器自动化将小说发布到番茄小说平台

用户故事：
- 作为内容创作者，我希望能批量生成符合平台要求的小说，减少手工写作时间
- 作为运营人员，我希望生成的内容质量可控，避免不合规内容
- 作为开发者，我希望整个流程自动化，无需人工干预

## Flow Design

> Notes for AI:
> 1. Consider the design patterns of agent, map-reduce, rag, and workflow. Apply them if they fit.
> 2. Present a concise, high-level description of the workflow.

### Applicable Design Pattern:

1. **Workflow（工作流）**: 小说生成是一个多步骤的线性流程
   - 提示词构建 → AI 生成 → 内容解析 → 质量验证 → 自动发布

2. **Batch（批处理）**: 支持循环生成多本小说
   - 使用 BatchFlow 控制生成数量

### Flow high-level Design:

1. **BuildPromptNode**: 从配置文件随机构建 AI 提示词
2. **GenerateNovelNode**: 调用 Gemini API 生成小说内容
3. **ParseNovelNode**: 解析 AI 返回的结构化内容（标题、标签、简介、正文）
4. **ValidateNovelNode**: 验证小说质量（字数、格式、语法等）
5. **SaveNovelNode**: 保存小说到本地文件
6. **PublishNovelNode**: 自动发布到番茄小说平台（可选）

```mermaid
flowchart TD
    start[Start] --> build[BuildPromptNode]
    build --> generate[GenerateNovelNode]
    generate --> parse[ParseNovelNode]
    parse -->|解析成功 default| validate[ValidateNovelNode]
    parse -->|解析失败 retry| generate
    validate -->|验证通过 pass| save[SaveNovelNode]
    validate -->|验证失败 fail| generate
    save --> end[End]
```

## Utility Functions

> Notes for AI:
> 1. Understand the utility function definition thoroughly by reviewing the doc.
> 2. Include only the necessary utility functions, based on nodes in the flow.

1. **Call Gemini API** (`utils/call_gemini.py`)
   - *Input*: prompt (str), temperature (float), model (str)
   - *Output*: response (str)
   - *Necessity*: GenerateNovelNode 用于调用 Gemini API 生成小说

2. **Random Prompt Builder** (`utils/prompt_builder.py`)
   - *Input*: config files (tags.json, command/*.txt, events.txt)
   - *Output*: formatted prompt (str)
   - *Necessity*: BuildPromptNode 用于构建随机提示词

3. **Novel Parser** (`utils/novel_parser.py`)
   - *Input*: raw response (str)
   - *Output*: structured novel data (dict)
   - *Necessity*: ParseNovelNode 用于提取结构化内容

4. **Content Validator** (`utils/validator.py`)
   - *Input*: novel content (str)
   - *Output*: validation result (bool) and error messages (list)
   - *Necessity*: ValidateNovelNode 用于质量检查

5. **Browser Automation** (`utils/browser.py`)
   - *Input*: page actions (dict)
   - *Output*: browser instance / page result
   - *Necessity*: PublishNovelNode 用于自动化发布流程（可选）

## Node Design

### Shared Store

> Notes for AI: Try to minimize data redundancy

The shared store structure is organized as follows:

```python
shared = {
    # 配置数据
    "config": {
        "tags": [],           # 标签列表
        "commands": [],       # 命令模板列表
        "events": []          # 事件库
    },

    # 生成数据
    "prompt": "",            # AI 提示词
    "raw_response": "",      # AI 原始响应

    # 解析后的小说数据
    "novel": {
        "title": "",         # 标题（≤25字）
        "tags": [],          # 标签列表 [{"label": "主题", "name": "科幻末世"}]
        "intro": "",         # 简介
        "content": "",       # 正文内容
        "chapters": []       # 章节列表 [{"title": "第1章 ...", "content": "..."}]
    },

    # 验证结果
    "validation": {
        "passed": False,
        "errors": []
    },

    # 文件路径
    "output_files": {
        "content": "",       # output/{title}.txt (平台粘贴格式)
        "full": "",          # output/full/{title}.txt (完整阅读格式)
        "intro": "",         # output/intro/{title}.txt
        "json": ""           # output/novel/{title}.json
    }
}
```

### Node Steps

> Notes for AI: Carefully decide whether to use Batch/Async Node/Flow.

1. **BuildPromptNode**
   - *Purpose*: 从配置文件随机构建 AI 提示词
   - *Type*: Regular
   - *Steps*:
     - *prep*: 读取 shared["config"] 中的 tags、commands、events
     - *exec*: 调用 random_prompt_builder() 工具函数，随机选择模板和事件，构建提示词
     - *post*: 将生成的提示词写入 shared["prompt"]

2. **GenerateNovelNode**
   - *Purpose*: 调用 Gemini API 生成小说
   - *Type*: Regular (max_retries=3)
   - *Steps*:
     - *prep*: 读取 shared["prompt"]
     - *exec*: 调用 call_gemini() 工具函数，temperature=1.2, model="gemini-2.5-pro"
     - *post*: 将 AI 响应写入 shared["raw_response"]

3. **ParseNovelNode**
   - *Purpose*: 解析 AI 返回的结构化内容
   - *Type*: Regular (带异常处理)
   - *Steps*:
     - *prep*: 读取 shared["raw_response"]
     - *exec*: 调用 novel_parser() 工具函数，使用正则提取 TITLE、TAG、INTRO、CONTENT
     - *exec_fallback*: 捕获解析异常，返回 None
     - *post*:
       - 如果 exec_res 为 None，返回 "retry" 重新生成
       - 否则将解析结果写入 shared["novel"]，返回 "default"

4. **ValidateNovelNode**
   - *Purpose*: 验证小说质量
   - *Type*: Regular
   - *Steps*:
     - *prep*: 读取 shared["novel"]["content"]
     - *exec*: 调用 content_validator() 工具函数，检查：
       - 是否包含 "--END--" 标记
       - 字数是否 ≥ 8000
       - 是否有超长英文序列（>20字母）
       - 每行长度是否 ≤ 350
     - *post*: 将验证结果写入 shared["validation"]，返回 "pass" 或 "fail"

5. **SaveNovelNode**
   - *Purpose*: 保存小说到本地文件
   - *Type*: Regular
   - *Steps*:
     - *prep*: 读取 shared["novel"]
     - *exec*: 将内容格式化并保存到 4 个文件：
       - output/{title}.txt - 平台粘贴格式（HTML <p>标签，去除章节标题）
       - output/full/{title}.txt - 完整阅读格式（保留章节标题）
       - output/intro/{title}.txt - 标签+简介
       - output/novel/{title}.json - 完整 JSON 数据
     - *post*: 将文件路径写入 shared["output_files"]

6. **PublishNovelNode**（可选功能）
   - *Purpose*: 自动发布到番茄小说平台
   - *Type*: Regular
   - *Steps*:
     - *prep*: 读取 shared["novel"] 和 shared["output_files"]
     - *exec*: 调用 browser_automation() 工具函数完成发布流程
     - *post*: 记录发布状态

