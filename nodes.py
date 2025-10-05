from pocketflow import Node
from utils.call_gemini import call_gemini
from utils.prompt_builder import build_random_prompt
from utils.novel_parser import parse_novel
from utils.validator import validate_content, clean_content
import json
from pathlib import Path


class BuildPromptNode(Node):
    """构建 AI 提示词节点"""

    def prep(self, shared):
        # 读取配置数据
        return shared["config"]

    def exec(self, config):
        # 调用提示词构建工具
        prompt = build_random_prompt(
            tags=config["tags"],
            commands=config["commands"],
            events=config["events"]
        )
        return prompt

    def post(self, shared, prep_res, exec_res):
        # 保存提示词
        shared["prompt"] = exec_res
        print(f"✓ 提示词构建完成，长度: {len(exec_res)} 字符")
        return "default"


class GenerateNovelNode(Node):
    """调用 Gemini API 生成小说节点"""

    def __init__(self, max_retries=3, wait=5):
        super().__init__(max_retries=max_retries, wait=wait)

    def prep(self, shared):
        return shared["prompt"]

    def exec(self, prompt):
        print("调用 Gemini API...开始生成")
        # 调用 Gemini API（启用流式输出）
        response = call_gemini(
            prompt=prompt,
            temperature=1.2,
            model="gemini-2.5-pro",
            stream=True  # 启用流式输出，避免超时
        )
        return response

    def exec_fallback(self, prep_res, exc):
        # 失败时的降级处理
        print(f"✗ Gemini API 调用失败: {exc}")
        raise exc  # 重新抛出异常，让上层处理

    def post(self, shared, prep_res, exec_res):
        shared["raw_response"] = exec_res
        print(f"✓ 小说生成完成，响应长度: {len(exec_res)} 字符")
        return "default"


class ParseNovelNode(Node):
    """解析小说内容节点"""

    def prep(self, shared):
        return shared["raw_response"]

    def exec(self, raw_response):
        # 解析小说
        novel = parse_novel(raw_response)
        return novel

    def post(self, shared, prep_res, exec_res):
        shared["novel"] = exec_res
        print(f"✓ 小说解析成功: {exec_res['title']}")
        # 修复 f-string 语法错误：先构建标签列表，再插入
        tags_str = [f"{t['label']}-{t['name']}" for t in exec_res['tags']]
        print(f"  - 标签: {tags_str}")
        print(f"  - 章节数: {len(exec_res['chapters'])}")
        return "default"


class ValidateNovelNode(Node):
    """验证小说质量节点"""

    def prep(self, shared):
        return shared["novel"]["content"]

    def exec(self, content):
        # 验证内容
        passed, errors = validate_content(content)
        return {"passed": passed, "errors": errors}

    def post(self, shared, prep_res, exec_res):
        shared["validation"] = exec_res

        if exec_res["passed"]:
            print("✓ 小说验证通过")
            return "pass"
        else:
            print("✗ 小说验证失败:")
            for error in exec_res["errors"]:
                print(f"  - {error}")

            # 保存失败的响应到错误目录
            error_file = Path("output/errors") / f"error_{shared['novel']['title'][:20]}.txt"
            error_file.parent.mkdir(parents=True, exist_ok=True)
            error_file.write_text(shared["raw_response"], encoding="utf-8")
            print(f"  已保存错误响应到: {error_file}")

            return "fail"


class SaveNovelNode(Node):
    """保存小说到本地文件节点"""

    def prep(self, shared):
        return shared["novel"]

    def exec(self, novel):
        # 清理并格式化内容
        cleaned_content = clean_content(novel["content"])

        # 准备保存的数据
        title = novel["title"]

        # 1. 正文内容（HTML 格式）
        html_content = cleaned_content.replace('\n', '<p>')

        # 2. 标签和简介
        tag_str = "".join([f"[{t['label']}:{t['name']}]" for t in novel["tags"]])
        intro_content = tag_str + novel["intro"]

        # 3. 完整 JSON 数据
        json_data = {
            **novel,
            "content": cleaned_content  # 使用清理后的内容
        }

        return {
            "title": title,
            "html_content": html_content,
            "intro_content": intro_content,
            "json_data": json_data
        }

    def post(self, shared, prep_res, exec_res):
        title = exec_res["title"]

        # 确保输出目录存在
        Path("output").mkdir(exist_ok=True)
        Path("output/intro").mkdir(exist_ok=True)
        Path("output/novel").mkdir(exist_ok=True)

        # 保存文件
        content_file = Path("output") / f"{title}.txt"
        intro_file = Path("output/intro") / f"{title}.txt"
        json_file = Path("output/novel") / f"{title}.json"

        content_file.write_text(exec_res["html_content"], encoding="utf-8")
        intro_file.write_text(exec_res["intro_content"], encoding="utf-8")
        json_file.write_text(json.dumps(exec_res["json_data"], ensure_ascii=False, indent=2), encoding="utf-8")

        # 保存文件路径到 shared
        shared["output_files"] = {
            "content": str(content_file),
            "intro": str(intro_file),
            "json": str(json_file)
        }

        print(f"✓ 小说已保存:")
        print(f"  - 内容: {content_file}")
        print(f"  - 简介: {intro_file}")
        print(f"  - JSON: {json_file}")

        return "default"