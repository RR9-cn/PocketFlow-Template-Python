from flow import novel_flow
import json
from pathlib import Path


def load_config():
    """加载配置文件"""
    # 读取标签配置
    tags_file = Path("config/tags.json")
    if tags_file.exists():
        with open(tags_file, encoding="utf-8") as f:
            tags = json.load(f)
    else:
        # 默认标签
        tags = [
            {"label": "主题", "name": "科幻末世"},
            {"label": "主题", "name": "现代言情"},
            {"label": "情节", "name": "穿越"},
            {"label": "情节", "name": "重生"},
        ]

    # 读取命令模板
    command_dir = Path("config/command")
    if command_dir.exists():
        commands = []
        for cmd_file in command_dir.glob("*.txt"):
            commands.append(cmd_file.read_text(encoding="utf-8"))
    else:
        # 默认命令模板
        commands = [
            "写一个关于{{event}}的故事，要有创意和想象力。",
        ]

    # 读取事件库
    events_file = Path("config/events.txt")
    if events_file.exists():
        events = [e.strip() for e in events_file.read_text(encoding="utf-8").split('\n') if e.strip()]
    else:
        # 默认事件
        events = ["末日求生", "时空穿越", "重生复仇"]

    return {
        "tags": tags,
        "commands": commands,
        "events": events
    }


def main():
    """主函数"""
    print("=" * 60)
    print("AI 小说自动生成系统 (基于 PocketFlow)")
    print("=" * 60)

    # 加载配置
    config = load_config()
    print(f"\n配置加载完成:")
    print(f"  - 标签数: {len(config['tags'])}")
    print(f"  - 命令模板数: {len(config['commands'])}")
    print(f"  - 事件数: {len(config['events'])}")

    # 初始化 shared store
    shared = {
        "config": config,
        "prompt": "",
        "raw_response": "",
        "novel": {},
        "validation": {},
        "output_files": {}
    }

    # 运行流程
    print("\n开始生成小说...\n")
    try:
        novel_flow.run(shared)
        print("\n" + "=" * 60)
        print("✓ 小说生成流程完成！")
        print("=" * 60)

        if shared.get("output_files"):
            print(f"\n生成的小说: {shared['novel']['title']}")
            print(f"文件位置:")
            for key, path in shared["output_files"].items():
                print(f"  - {key}: {path}")

    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
