"""
小说解析工具
从 AI 响应中提取结构化的小说内容
"""
import re


def parse_novel(response: str) -> dict:
    """
    解析 AI 生成的小说内容

    Args:
        response: AI 原始响应文本

    Returns:
        解析后的小说数据字典，包含 title, tags, intro, content, chapters

    Raises:
        ValueError: 如果缺少必要的 MARK 标记
    """
    # 使用正则表达式提取 MARK 区块（使用 {...} 格式，单层大括号）
    title_match = re.search(r'TITLE\{(.*?)\}TITLE', response, re.DOTALL)
    tag_match = re.search(r'TAG\{(.*?)\}TAG', response, re.DOTALL)
    intro_match = re.search(r'INTRO\{(.*?)\}INTRO', response, re.DOTALL)

    # 验证前三个必要区块是否存在
    missing = []
    if not title_match:
        missing.append('TITLE')
    if not tag_match:
        missing.append('TAG')
    if not intro_match:
        missing.append('INTRO')

    if missing:
        raise ValueError(f"小说生成不完整：缺少 {', '.join(missing)} 标记区块")

    # 提取并清理各部分内容
    title = title_match.group(1).strip()
    tag_string = tag_match.group(1).strip()
    intro = intro_match.group(1).strip()

    # CONTENT: 优先使用正则匹配 CONTENT{...}CONTENT（单层大括号）
    # 如果匹配不上，则取 }INTRO 之后到 --END-- 之间的内容
    content_match = re.search(r'CONTENT\{(.*?)\}CONTENT', response, re.DOTALL)
    if content_match:
        content = content_match.group(1).strip()
    else:
        # 找到 }}INTRO 的位置，取之后的所有内容
        intro_end_pos = intro_match.end()
        remaining = response[intro_end_pos:]

        # 检查是否有 --END-- 标记
        if '--END--' in remaining:
            # 只取到 --END-- 之前的内容
            end_pos = remaining.find('--END--')
            content = remaining[:end_pos].strip()
        else:
            # 没有 --END-- 标记，抛出异常
            raise ValueError('小说生成不完整：正文内容缺少 "--END--" 标记')

    # 解析标签（格式：主题-科幻末世,情节-穿越）
    tags = []
    for pair in tag_string.split(','):
        parts = pair.split('-')
        if len(parts) == 2:
            label, name = parts
            tags.append({"label": label.strip(), "name": name.strip()})

    # 验证生成是否完整（content 不应该再包含 --END--）
    # 注意：已经在上面处理了，这里不需要再检查

    # 提取章节
    chapters = []
    lines = content.split('\n')
    current_chapter = None

    for line in lines:
        if line.strip().startswith('##'):
            # 新章节开始
            chapter_title = line.strip()[2:].strip()  # 移除 ##
            current_chapter = {
                "title": chapter_title,
                "content": ""
            }
            chapters.append(current_chapter)
        elif current_chapter:
            # 添加内容到当前章节
            current_chapter["content"] += line + "\n"

    # 清理章节内容
    for chapter in chapters:
        chapter["content"] = chapter["content"].strip()

    return {
        "title": title[:25],  # 限制标题长度
        "tags": tags,
        "intro": intro,
        "content": content,
        "chapters": chapters
    }


if __name__ == "__main__":
    # 测试代码 1: 标准格式（INTRO 后直接写正文）
    test_response_standard = """
这是一些额外的文本

TITLE{测试小说标题}TITLE
TAG{主题-科幻末世,情节-穿越}TAG
INTRO{
这是一个关于末日穿越的故事。
主角在末日中求生。
}INTRO

## 第1章 开始

这是第一章的内容。

## 第2章 冒险

这是第二章的内容。

--END--

这是更多额外文本
"""

    # 测试代码 2: 完整格式（带 CONTENT{...}CONTENT 包裹）
    test_response_full = """
TITLE{测试小说标题2}TITLE
TAG{主题-现代言情,情节-重生}TAG
INTRO{
这是简介
}INTRO
CONTENT{
## 第1章 开始

使用完整格式 CONTENT 标记。

## 第2章 继续

继续写。

--END--
}CONTENT
"""

    print("=" * 50)
    print("测试1: 标准格式（推荐）")
    print("=" * 50)
    try:
        novel = parse_novel(test_response_standard)
        print("[OK] 解析成功:")
        print(f"  标题: {novel['title']}")
        print(f"  标签: {novel['tags']}")
        print(f"  章节数: {len(novel['chapters'])}")
    except ValueError as e:
        print(f"[FAIL] 解析失败: {e}")

    print("\n" + "=" * 50)
    print("测试2: 完整格式")
    print("=" * 50)
    try:
        novel = parse_novel(test_response_full)
        print("[OK] 解析成功:")
        print(f"  标题: {novel['title']}")
        print(f"  标签: {novel['tags']}")
        print(f"  章节数: {len(novel['chapters'])}")
        print(f"  内容预览: {novel['content'][:100]}...")
    except ValueError as e:
        print(f"[FAIL] 解析失败: {e}")
