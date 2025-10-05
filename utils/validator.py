"""
内容验证工具
验证小说内容的质量和格式
"""
import re


def validate_content(content: str) -> tuple[bool, list[str]]:
    """
    验证小说内容质量

    Args:
        content: 小说正文内容

    Returns:
        (是否通过验证, 错误信息列表)
    """
    errors = []

    # 1. 检查是否包含过长的英文序列（>20个字母）
    if has_long_english_sequence(content):
        errors.append("包含过长的英文字母序列（超过20个字母）")

    # 2. 检查字数是否少于8000
    if len(content) < 8000:
        errors.append(f"小说内容少于8000字，当前字数: {len(content)}")

    # 3. 检查每行长度
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if len(line) > 350:
            errors.append(f"第{i}行超长（超过350字符），长度: {len(line)}")
            break  # 只报告第一个超长行

    # 4. 标点符号中文化验证（可选，仅警告）
    # 这里不强制要求，只是检查

    passed = len(errors) == 0
    return passed, errors


def has_long_english_sequence(text: str) -> bool:
    """
    检查是否包含超过20个连续的英文字母

    Args:
        text: 待检查文本

    Returns:
        是否包含过长英文序列
    """
    count = 0
    for char in text:
        code = ord(char)
        # 判断是否为英文字母（A-Z 或 a-z）
        if (65 <= code <= 90) or (97 <= code <= 122):
            count += 1
            if count > 20:
                return True
        # 如果遇到非字母且非空格/标点，重置计数
        # 使用 Python 支持的正则：空格、标点符号（包括中英文标点）
        elif not re.match(r'[\s\.,;!?:，。；！？：、"""''（）\(\)\[\]【】]', char):
            count = 0

    return False


def clean_content(content: str) -> str:
    """
    清理和格式化内容（标点符号中文化等）

    Args:
        content: 原始内容

    Returns:
        清理后的内容
    """
    # 标点符号中文化
    content = content.replace(':', '：')
    content = content.replace(',', '，')
    content = content.replace('?', '？')
    content = content.replace('!', '！')
    content = content.replace('*', '')
    content = content.replace('"', '')
    content = content.replace("'", '')

    # 移除中文字符之间的特定英文字母
    for char in ['T', 'M', 'D', 'G', 'e', 'E']:
        pattern = re.compile(f'([\u4e00-\u9fa5]){char}([\u4e00-\u9fa5])')
        while pattern.search(content):
            content = pattern.sub(r'\1\2', content)

    # 处理段落格式：给非标题段落添加缩进
    lines = content.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            if line.startswith('##'):
                # 章节标题，保持原样
                formatted_lines.append(line)
            else:
                # 普通段落，添加缩进
                formatted_lines.append(f'　　{line}')

    return '\n'.join(formatted_lines)


if __name__ == "__main__":
    # 测试代码
    test_content = """## 第1章 开始

这是第一章的内容，包含一些中文文字。

This is a very long English sequence that should be detected as invalid content because it exceeds twenty letters.

这里是第二段内容。
"""

    passed, errors = validate_content(test_content)
    print(f"验证结果: {'通过' if passed else '失败'}")
    if errors:
        print("错误信息:")
        for error in errors:
            print(f"  - {error}")

    print("\n清理后的内容:")
    cleaned = clean_content(test_content)
    print(cleaned)
