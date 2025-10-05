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
    # 使用正则表达式提取 MARK 区块
    title_match = re.search(r'TITLE\{(.*?)\}TITLE', response, re.DOTALL)
    tag_match = re.search(r'TAG\{(.*?)\}TAG', response, re.DOTALL)
    intro_match = re.search(r'INTRO\{(.*?)\}INTRO', response, re.DOTALL)
    content_match = re.search(r'CONTENT\{(.*?)\}CONTENT', response, re.DOTALL)

    # 验证所有区块是否存在
    missing = []
    if not title_match:
        missing.append('TITLE')
    if not tag_match:
        missing.append('TAG')
    if not intro_match:
        missing.append('INTRO')
    if not content_match:
        missing.append('CONTENT')

    if missing:
        raise ValueError(f"小说生成不完整：缺少 {', '.join(missing)} 标记区块")

    # 提取并清理各部分内容
    title = title_match.group(1).strip()
    tag_string = tag_match.group(1).strip()
    intro = intro_match.group(1).strip()
    content = content_match.group(1).strip()

    # 解析标签（格式：主题-科幻末世,情节-穿越）
    tags = []
    for pair in tag_string.split(','):
        parts = pair.split('-')
        if len(parts) == 2:
            label, name = parts
            tags.append({"label": label.strip(), "name": name.strip()})

    # 验证生成是否完整（检查结束标记）
    if not content.endswith('--END--'):
        raise ValueError('小说生成不完整：正文内容缺少 "--END--" 标记')

    # 移除结束标记
    content = content.replace('--END--', '').strip()

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
    # 测试代码
    test_response = """
这是一些额外的文本

TITLE{测试小说标题}TITLE
TAG{主题-科幻末世,情节-穿越}TAG
INTRO{
这是一个关于末日穿越的故事。
主角在末日中求生。
}INTRO
CONTENT{
## 第1章 开始

这是第一章的内容。

## 第2章 冒险

这是第二章的内容。

--END--
}CONTENT

这是更多额外文本
"""

    try:
        novel = parse_novel(test_response)
        print("解析成功:")
        print(f"标题: {novel['title']}")
        print(f"标签: {novel['tags']}")
        print(f"章节数: {len(novel['chapters'])}")
    except ValueError as e:
        print(f"解析失败: {e}")
