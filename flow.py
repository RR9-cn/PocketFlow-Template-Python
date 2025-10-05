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

    # 验证通过后保存
    validate_novel - "pass" >> save_novel

    # 验证失败则结束（可以在这里添加重试逻辑）
    # validate_novel - "fail" >> error_handler (如果需要)

    # 创建流程
    return Flow(start=build_prompt)


# 导出流程
novel_flow = create_novel_flow()