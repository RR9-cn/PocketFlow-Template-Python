from pocketflow import Flow
from nodes import (
    BuildPromptNode,
    GenerateNovelNode,
    ParseNovelNode,
    ValidateNovelNode,
    SaveNovelNode
)


def create_novel_flow():
    """创建小说生成流程"""
    # 创建节点
    build_prompt = BuildPromptNode()
    generate_novel = GenerateNovelNode(max_retries=3, wait=5)
    parse_novel = ParseNovelNode()
    validate_novel = ValidateNovelNode()
    save_novel = SaveNovelNode()

    # 连接节点
    build_prompt >> generate_novel >> parse_novel >> validate_novel

    # 解析失败则重新生成
    parse_novel - "retry" >> generate_novel

    # 验证通过后保存
    validate_novel - "pass" >> save_novel

    # 验证失败则重新生成（可选：也可以直接结束）
    validate_novel - "fail" >> generate_novel

    # 创建流程
    return Flow(start=build_prompt)


# 导出流程
novel_flow = create_novel_flow()