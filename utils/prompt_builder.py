"""
随机提示词构建工具
从配置文件中随机选择标签、命令模板和事件，构建 AI 提示词
"""
import random
import json
from pathlib import Path


def build_random_prompt(tags: list, commands: list, events: list) -> str:
    """
    构建随机的小说生成提示词

    Args:
        tags: 标签列表 [{"label": "主题", "name": "科幻末世"}, ...]
        commands: 命令模板列表 ["命令模板1", "命令模板2", ...]
        events: 事件列表 ["事件1", "事件2", ...]

    Returns:
        格式化的提示词字符串
    """
    # 随机选择一个命令模板
    command = random.choice(commands)

    # 随机选择一个事件
    event = random.choice(events)

    # 替换事件占位符
    command = command.replace('{{event}}', event)

    # 按 label 对标签分组
    grouped_tags = {}
    for tag in tags:
        label = tag["label"]
        if label not in grouped_tags:
            grouped_tags[label] = []
        grouped_tags[label].append(tag["name"])

    # 构建标签指令字符串
    tag_instructions = "\n".join([
        f"{label}：{', '.join(names)}"
        for label, names in grouped_tags.items()
    ])

    # 构建最终提示词
    prompt = f"""{command}
需要总字数18000字，每章约1700字，共计11章

---
请从以下标签列表中，为你的小说选择合适的标签。规则如下：
1. 最多选择5个标签。
2. "主题"分类为必选项，必须并且只能选择一个。
3. "情节"一定包含沙雕搞笑。
4. 其他分类为可选项。

标签列表：
{tag_instructions}
---

MARK:
- TITLE: 小说标题，根据你的写作内容拟定一个合适的标题，在二十五个字之内
- TAG: 小说标签，根据你的写作内容从上述的标签列表中选择标签，以"[分类名]-[标签名]"的形式填写，多个标签使用","分隔
- INTRO: 是你对于小说内容的简介，几百字就好，需要做好分行处理，再开始输出语句。
- CONTENT: 正文内容，每个章节前需要一个小标题，和小说标题相似的命名原则，格式为"## 第[数字]章 [章节标题]"，注意：小说写完后需要在最后输出一行"--END--"

输出格式:
[MARK 例如"TITLE"]{{[信息]}}[MARK]

输出格式的参考：
TITLE{{东皇今天又发癫了}}TITLE
TAG{{主题-搞笑轻松,情节-穿越}}TAG
INTRO{{
...此处省略...
}}INTRO
CONTENT{{
## 第1章 第一章日子没法过了

我在昆仑山顶睡得正香。

...此处省略很多正文，但是你的输出不能省略...
--END--
}}CONTENT

---
参考上述输出格式，输出你的小说，在输出格式外部的内容将会被忽略，只有用户才能看见
"""

    return prompt


if __name__ == "__main__":
    # 测试代码
    test_tags = [
        {"label": "主题", "name": "科幻末世"},
        {"label": "主题", "name": "现代言情"},
        {"label": "情节", "name": "穿越"},
        {"label": "情节", "name": "重生"},
    ]

    test_commands = [
        "写一个{{event}}的故事",
        "创作一个关于{{event}}的小说"
    ]

    test_events = [
        "末日求生",
        "时空穿越",
        "重生复仇"
    ]

    prompt = build_random_prompt(test_tags, test_commands, test_events)
    print(prompt)
