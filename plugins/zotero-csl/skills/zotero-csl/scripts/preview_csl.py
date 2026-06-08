#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
preview_csl.py — 用 citeproc-py 加载 .csl 文件和测试数据，渲染 citation 和 bibliography 输出。

用法:
    python preview_csl.py <file.csl>                     # 使用默认 test_data.json
    python preview_csl.py <file.csl> --data custom.json   # 使用自定义数据
"""

import argparse
import json
import os
import sys

# Windows 下强制 UTF-8 输出，避免中文乱码
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 依赖检查
# ---------------------------------------------------------------------------
try:
    from citeproc import (
        Citation,
        CitationItem,
        CitationStylesBibliography,
        CitationStylesStyle,
        formatter,
    )
    from citeproc.source.json import CiteProcJSON
except ImportError:
    print("错误: 缺少 citeproc-py 库。请先安装：")
    print("  pip install citeproc-py")
    sys.exit(1)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def load_test_data(data_path: str) -> list[dict]:
    """加载 CSL-JSON 格式的测试数据。"""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or len(data) == 0:
        print(f"错误: {data_path} 应为非空 JSON 数组")
        sys.exit(1)
    return data


def warn_callback(citation_warning):
    """citeproc 回调，用于捕获警告（这里静默忽略）。"""
    pass


def render_citation_text(bib: CitationStylesBibliography, item_ids: list[str]) -> str:
    """注册并渲染一个 citation，返回字符串。"""
    citation = Citation([CitationItem(item_id) for item_id in item_ids])
    bib.register(citation)
    return str(bib.cite(citation, warn_callback))


def preview_csl(csl_path: str, data_path: str) -> None:
    """主流程：加载 CSL 和数据，输出 citation + bibliography。"""

    # --- 加载数据 ---
    test_data = load_test_data(data_path)
    item_ids = [entry["id"] for entry in test_data]

    # --- 加载 CSL 样式 ---
    try:
        style = CitationStylesStyle(csl_path, validate=False)
    except Exception as exc:
        print(f"错误: 无法加载 CSL 文件 '{csl_path}': {exc}")
        sys.exit(1)

    # --- 构建 bibliography ---
    source = CiteProcJSON(test_data)
    bib = CitationStylesBibliography(style, source, formatter.plain)

    # === Citation (正文引用) ===
    print("=== Citation (正文引用) ===")

    # Single: 第 1 条
    single = render_citation_text(bib, [item_ids[0]])
    print(f"Single: {single}")

    # Multiple: 第 1 条 + 第 3 条（不连续）
    if len(item_ids) >= 3:
        multiple = render_citation_text(bib, [item_ids[0], item_ids[2]])
        print(f"Multiple: {multiple}")

    # Range: 前 3 条（连续）
    if len(item_ids) >= 3:
        range_cite = render_citation_text(bib, [item_ids[0], item_ids[1], item_ids[2]])
        print(f"Range: {range_cite}")

    # --- 为剩余未注册的条目也生成 citation，确保 bibliography 包含所有条目 ---
    registered = set()
    registered.update(item_ids[:3] if len(item_ids) >= 3 else item_ids[:1])
    remaining = [iid for iid in item_ids if iid not in registered]
    if remaining:
        rest_citation = Citation([CitationItem(iid) for iid in remaining])
        bib.register(rest_citation)
        bib.cite(rest_citation, warn_callback)

    # === Bibliography (参考文献列表) ===
    print()
    print("=== Bibliography (参考文献列表) ===")
    bibliography = bib.bibliography()
    if bibliography:
        for item in bibliography:
            text = str(item).strip()
            if text:
                print(text)
    else:
        print("(bibliography 为空，请检查 CSL 文件配置)")


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="用 citeproc-py 预览 CSL 样式的 citation 和 bibliography 输出"
    )
    parser.add_argument("csl_file", help="CSL 样式文件路径")
    parser.add_argument(
        "--data",
        default=None,
        help="CSL-JSON 测试数据文件路径 (默认使用同目录下的 test_data.json)",
    )
    args = parser.parse_args()

    # CSL 文件
    csl_path = os.path.abspath(args.csl_file)
    if not os.path.isfile(csl_path):
        print(f"错误: CSL 文件不存在: {csl_path}")
        sys.exit(1)

    # 数据文件
    if args.data:
        data_path = os.path.abspath(args.data)
    else:
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data.json")
    if not os.path.isfile(data_path):
        print(f"错误: 数据文件不存在: {data_path}")
        sys.exit(1)

    print(f"CSL:  {csl_path}")
    print(f"Data: {data_path}")
    print()

    preview_csl(csl_path, data_path)


if __name__ == "__main__":
    main()
