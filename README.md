# AI 小说自动生成系统

基于 [PocketFlow](https://github.com/the-pocket/PocketFlow) 框架实现的 AI 小说自动生成系统，使用 Google Gemini API 自动生成符合特定格式的小说内容。

## ✨ 功能特性

- 🤖 **AI 驱动生成**: 使用 Google Gemini 2.5 Pro 模型生成高质量小说内容
- 📝 **结构化输出**: 自动提取标题、标签、简介和正文
- ✅ **质量验证**: 多重验证确保内容符合平台要求
- 🔄 **自动重试**: 内置重试机制处理 API 失败
- 📊 **批量生成**: 支持循环生成多本小说
- 🎯 **高度可配置**: 通过配置文件自定义标签、模板和事件

## 🏗️ 项目结构

```
PocketFlow-Template-Python-1/
├── main.py                 # 主入口
├── flow.py                 # 流程定义
├── nodes.py                # 节点实现
├── utils/                  # 工具函数
│   ├── call_gemini.py     # Gemini API 调用
│   ├── prompt_builder.py  # 提示词构建
│   ├── novel_parser.py    # 小说解析
│   └── validator.py       # 内容验证
├── config/                 # 配置文件
│   ├── tags.json          # 标签配置
│   ├── command/           # 命令模板
│   └── events.txt         # 事件库
├── output/                 # 输出目录
│   ├── *.txt              # 小说正文（HTML 格式）
│   ├── intro/             # 标签和简介
│   ├── novel/             # 完整 JSON 数据
│   └── errors/            # 失败的响应
├── docs/                   # 设计文档
│   └── design.md          # 详细设计文档
└── requirements.txt        # Python 依赖
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

设置 Gemini API Key：

```bash
export GEMINI_API_KEY="your-api-key-here"
```

或在 Windows 上：

```cmd
set GEMINI_API_KEY=your-api-key-here
```

### 3. 运行程序

```bash
python main.py
```

## 📋 工作流程

系统使用 PocketFlow 的 Workflow 设计模式，流程如下：

```mermaid
flowchart TD
    start[Start] --> build[BuildPromptNode]
    build --> generate[GenerateNovelNode]
    generate --> parse[ParseNovelNode]
    parse --> validate[ValidateNovelNode]
    validate -->|pass| save[SaveNovelNode]
    validate -->|fail| error[Error Handling]
    save --> end[End]
    error --> end
```

### 节点说明

1. **BuildPromptNode**: 从配置文件随机构建 AI 提示词
2. **GenerateNovelNode**: 调用 Gemini API 生成小说（支持重试）
3. **ParseNovelNode**: 解析 AI 返回的结构化内容
4. **ValidateNovelNode**: 验证小说质量（字数、格式等）
5. **SaveNovelNode**: 保存小说到本地文件

## ⚙️ 配置说明

### 标签配置 (`config/tags.json`)

```json
[
  {
    "label": "主题",
    "name": "科幻末世"
  },
  {
    "label": "情节",
    "name": "穿越"
  }
]
```

### 命令模板 (`config/command/*.txt`)

命令模板支持 `{{event}}` 占位符：

```
写一个关于{{event}}的精彩故事，要有创意和想象力。
```

### 事件库 (`config/events.txt`)

```
末日求生
时空穿越
重生复仇
```

## 📝 小说格式要求

AI 生成的小说必须遵循以下格式：

```
TITLE{小说标题}TITLE
TAG{主题-科幻末世,情节-穿越}TAG
INTRO{小说简介...}INTRO
CONTENT{
## 第1章 章节标题
正文内容...
--END--
}CONTENT
```

### 验证规则

- ✅ 必须包含 `--END--` 结束标记
- ✅ 字数 ≥ 8000
- ✅ 无超长英文序列（>20个字母）
- ✅ 每行长度 ≤ 350 字符

## 📚 技术栈

- **框架**: PocketFlow
- **AI 模型**: Google Gemini 2.5 Pro
- **Python**: 3.8+

## 📄 输出文件

- `output/{标题}.txt` - 正文（HTML 格式）
- `output/intro/{标题}.txt` - 标签和简介
- `output/novel/{标题}.json` - 完整数据
- `output/errors/` - 失败响应
