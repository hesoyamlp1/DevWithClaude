#!/usr/bin/env python3
"""
提示词模板管理脚本 - 供 LLM subagent 调用

命令:
    list                        列出所有提示词模板
    show <name>                 显示模板详情和内容
    variables <name>            显示模板变量
    validate <name>             验证模板语法
    find-hardcoded              查找代码中硬编码的提示词
    categories                  列出所有模板分类

示例:
    python3 prompt_helper.py list
    python3 prompt_helper.py show system.loop
    python3 prompt_helper.py variables tool.speak
"""

import json
import os
import re
import sys
import sqlite3
from pathlib import Path
# 修复 Windows 终端中文乱码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "data/webrpg.db"
CORE_SRC = PROJECT_ROOT / "core/src/main/java"
COMMON_SRC = PROJECT_ROOT / "common/src/main/java"


def get_db_connection():
    """获取数据库连接"""
    if not DB_PATH.exists():
        return None
    return sqlite3.connect(DB_PATH)


def cmd_list():
    """列出所有提示词模板"""
    conn = get_db_connection()
    if not conn:
        print("数据库不存在")
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, display_name, category, template_type, is_system, description
        FROM prompt_template
        ORDER BY category, name
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("没有模板")
        return

    print(f"提示词模板 ({len(rows)} 个):")
    print()

    current_category = None
    for name, display_name, category, template_type, is_system, description in rows:
        if category != current_category:
            current_category = category
            print(f"## {category}")

        system_tag = " [系统]" if is_system else ""
        type_tag = f" ({template_type})" if template_type != 'FULL' else ""
        desc = f" - {description[:50]}..." if description and len(description) > 50 else (f" - {description}" if description else "")
        print(f"  - {name}{system_tag}{type_tag}{desc}")

    print()


def cmd_show(name):
    """显示模板详情"""
    conn = get_db_connection()
    if not conn:
        print("数据库不存在")
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, display_name, category, template_type, content,
               variables_json, description, is_system, version
        FROM prompt_template
        WHERE name = ?
    """, (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"模板不存在: {name}")
        return

    name, display_name, category, template_type, content, variables_json, description, is_system, version = row

    print(f"# {name}")
    if display_name:
        print(f"显示名: {display_name}")
    print(f"分类: {category}")
    print(f"类型: {template_type}")
    print(f"版本: {version}")
    print(f"系统模板: {'是' if is_system else '否'}")

    if description:
        print(f"\n## 描述\n{description}")

    if variables_json:
        print(f"\n## 变量定义")
        try:
            variables = json.loads(variables_json)
            for var in variables:
                print(f"  - {var.get('name', '?')}: {var.get('description', '')}")
        except json.JSONDecodeError:
            print(f"  (JSON 解析失败)")

    print(f"\n## 内容\n```")
    print(content)
    print("```")


def cmd_variables(name):
    """显示模板变量"""
    conn = get_db_connection()
    if not conn:
        print("数据库不存在")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT content, variables_json FROM prompt_template WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"模板不存在: {name}")
        return

    content, variables_json = row

    # 从 variables_json 解析定义的变量
    defined_vars = {}
    if variables_json:
        try:
            for var in json.loads(variables_json):
                defined_vars[var.get('name', '')] = var.get('description', '')
        except json.JSONDecodeError:
            pass

    # 从内容中提取使用的变量
    simple_vars = set(re.findall(r'\{\{(\w+(?:\.\w+)*)\}\}', content))
    conditional_vars = set(re.findall(r'\{\{#if\s+(\w+(?:\.\w+)*)', content))
    list_vars = set(re.findall(r'\{\{#(?:each|formatList)\s+(\w+)', content))

    all_used_vars = simple_vars | conditional_vars | list_vars

    print(f"模板 {name} 的变量:")
    print()

    if defined_vars:
        print("## 定义的变量 (variables_json)")
        for var_name, desc in defined_vars.items():
            print(f"  - {var_name}: {desc}")
        print()

    print("## 内容中使用的变量")
    for v in sorted(all_used_vars):
        defined_desc = defined_vars.get(v, "")
        if defined_desc:
            print(f"  - {v}: {defined_desc}")
        else:
            print(f"  - {v} (未在 variables_json 中定义)")


def cmd_validate(name):
    """验证模板语法"""
    conn = get_db_connection()
    if not conn:
        print("数据库不存在")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT content FROM prompt_template WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"模板不存在: {name}")
        return

    content = row[0]
    errors = []
    warnings = []

    # 检查消息分隔符
    has_system = '[SYSTEM]' in content
    has_user = '[USER]' in content

    if not has_system and not has_user:
        warnings.append("模板中没有消息分隔符 ([SYSTEM], [USER], [ASSISTANT])")

    # 检查变量语法错误
    wrong_vars = re.findall(r'\{\s*\w+\s*\}(?!\})', content)
    if wrong_vars:
        errors.append(f"变量语法错误，应使用 {{{{name}}}} 而非 {{name}}: {wrong_vars}")

    # 检查未闭合的条件
    if_count = len(re.findall(r'\{\{#if\b', content))
    endif_count = len(re.findall(r'\{\{/if\}\}', content))
    if if_count != endif_count:
        errors.append(f"条件语句未闭合: {{{{#if}}}} 有 {if_count} 个, {{{{/if}}}} 有 {endif_count} 个")

    # 检查未闭合的循环
    each_count = len(re.findall(r'\{\{#each\b', content))
    endeach_count = len(re.findall(r'\{\{/each\}\}', content))
    if each_count != endeach_count:
        errors.append(f"循环语句未闭合: {{{{#each}}}} 有 {each_count} 个, {{{{/each}}}} 有 {endeach_count} 个")

    print(f"验证模板: {name}")

    if errors:
        print("\n错误:")
        for e in errors:
            print(f"  ❌ {e}")

    if warnings:
        print("\n警告:")
        for w in warnings:
            print(f"  ⚠️ {w}")

    if not errors and not warnings:
        print("✅ 模板语法检查通过")


def cmd_find_hardcoded():
    """查找代码中硬编码的提示词"""
    print("查找硬编码提示词...")

    indicators = [
        (r'"\s*你是一个', "角色设定"),
        (r'"\s*You are a', "角色设定 (英文)"),
        (r'"\s*\[SYSTEM\]', "系统消息"),
        (r'"\s*请根据', "指令"),
    ]

    found = []
    for src_dir in [CORE_SRC, COMMON_SRC]:
        if not src_dir.exists():
            continue
        for file_path in src_dir.rglob("*.java"):
            # 跳过模板相关文件
            if 'template' in file_path.name.lower():
                continue

            content = file_path.read_text(encoding='utf-8')
            rel_path = file_path.relative_to(PROJECT_ROOT)

            for pattern, desc in indicators:
                if re.search(pattern, content, re.IGNORECASE):
                    found.append((str(rel_path), desc))
                    break

    if found:
        print(f"发现 {len(found)} 个文件可能包含硬编码提示词:")
        for path, desc in found:
            print(f"  - {path} ({desc})")
    else:
        print("✅ 未发现明显的硬编码提示词")


def cmd_categories():
    """列出所有模板分类"""
    conn = get_db_connection()
    if not conn:
        print("数据库不存在")
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM prompt_template
        GROUP BY category
        ORDER BY category
    """)
    rows = cursor.fetchall()
    conn.close()

    print("模板分类:")
    for category, count in rows:
        print(f"  - {category} ({count} 个)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == 'list':
        cmd_list()
    elif cmd == 'show':
        if len(sys.argv) < 3:
            print("用法: prompt_helper.py show <name>")
            return
        cmd_show(sys.argv[2])
    elif cmd == 'variables':
        if len(sys.argv) < 3:
            print("用法: prompt_helper.py variables <name>")
            return
        cmd_variables(sys.argv[2])
    elif cmd == 'validate':
        if len(sys.argv) < 3:
            print("用法: prompt_helper.py validate <name>")
            return
        cmd_validate(sys.argv[2])
    elif cmd == 'find-hardcoded':
        cmd_find_hardcoded()
    elif cmd == 'categories':
        cmd_categories()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
