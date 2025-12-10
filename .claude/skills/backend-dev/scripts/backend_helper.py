#!/usr/bin/env python3
"""
后端代码检查脚本 - 供 LLM subagent 调用

命令:
    check-service <file>        检查 Service 类规范
    find-hardcoded-sql          查找硬编码 SQL
    find-hardcoded-prompt       查找硬编码提示词
    list-services               列出所有 Service 类
    list-controllers            列出所有 Controller 类
    show-structure              显示后端目录结构

示例:
    python3 backend_helper.py check-service PlayerService.java
    python3 backend_helper.py find-hardcoded-sql
"""

import os
import re
import sys
from pathlib import Path
# 修复 Windows 终端中文乱码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
CORE_SRC = PROJECT_ROOT / "core/src/main/java"
COMMON_SRC = PROJECT_ROOT / "common/src/main/java"


def find_java_files(base_path, pattern=None):
    """查找 Java 文件"""
    if not base_path.exists():
        return []
    files = list(base_path.rglob("*.java"))
    if pattern:
        files = [f for f in files if pattern in f.name]
    return files


def cmd_check_service(filename):
    """检查 Service 类规范"""
    # 查找文件
    files = find_java_files(CORE_SRC, filename)
    files.extend(find_java_files(COMMON_SRC, filename))

    if not files:
        print(f"未找到文件: {filename}")
        return

    for file_path in files:
        print(f"检查文件: {file_path}")
        content = file_path.read_text(encoding='utf-8')
        issues = []

        # 检查 Optional 返回
        # 查找返回单个对象的方法但没有用 Optional
        single_return_patterns = [
            r'public\s+(?!Optional)(\w+)\s+find\w*ById',
            r'public\s+(?!Optional)(\w+)\s+get\w*ById',
            r'public\s+(?!Optional)(\w+)\s+findOne',
        ]
        for pattern in single_return_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(f"查询单个对象的方法应返回 Optional<T>: {matches}")

        # 检查是否有 new 具体实现
        new_impl_pattern = r'new\s+(Jdbc|Mybatis|Http|RestTemplate)\w*\('
        if re.search(new_impl_pattern, content):
            issues.append("不应直接 new 具体实现，使用依赖注入")

        # 检查日志是否使用中文
        log_pattern = r'log\.(info|warn|error|debug)\s*\(\s*"([^"]+)"'
        log_matches = re.findall(log_pattern, content)
        for level, msg in log_matches:
            if msg.isascii() and len(msg) > 10:
                issues.append(f"日志应使用中文: {msg[:50]}...")

        if issues:
            print("发现问题:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("✅ 未发现明显问题")
        print()


def cmd_find_hardcoded_sql():
    """查找硬编码 SQL"""
    print("查找硬编码 SQL...")
    sql_patterns = [
        r'"SELECT\s+.*FROM',
        r'"INSERT\s+INTO',
        r'"UPDATE\s+\w+\s+SET',
        r'"DELETE\s+FROM',
        r'"CREATE\s+TABLE',
    ]

    found = []
    for src_dir in [CORE_SRC, COMMON_SRC]:
        for file_path in find_java_files(src_dir):
            content = file_path.read_text(encoding='utf-8')
            for pattern in sql_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    found.append(str(rel_path))
                    break

    if found:
        print(f"发现 {len(found)} 个文件包含硬编码 SQL:")
        for f in found:
            print(f"  - {f}")
    else:
        print("✅ 未发现硬编码 SQL")


def cmd_find_hardcoded_prompt():
    """查找硬编码提示词"""
    print("查找硬编码提示词...")
    prompt_indicators = [
        r'""".*你是.*"""',
        r'""".*[SYSTEM].*"""',
        r'"你是一个.*"',
        r'"You are.*"',
    ]

    found = []
    for src_dir in [CORE_SRC, COMMON_SRC]:
        for file_path in find_java_files(src_dir):
            # 跳过模板相关文件
            if 'template' in file_path.name.lower():
                continue
            content = file_path.read_text(encoding='utf-8')
            for pattern in prompt_indicators:
                if re.search(pattern, content, re.DOTALL):
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    found.append(str(rel_path))
                    break

    if found:
        print(f"发现 {len(found)} 个文件可能包含硬编码提示词:")
        for f in found:
            print(f"  - {f}")
    else:
        print("✅ 未发现硬编码提示词")


def cmd_list_services():
    """列出所有 Service 类"""
    print("Service 类:")
    for src_dir in [CORE_SRC, COMMON_SRC]:
        files = find_java_files(src_dir, "Service")
        for f in sorted(files):
            rel_path = f.relative_to(PROJECT_ROOT)
            print(f"  - {rel_path}")


def cmd_list_controllers():
    """列出所有 Controller 类"""
    print("Controller 类:")
    for src_dir in [CORE_SRC, COMMON_SRC]:
        files = find_java_files(src_dir, "Controller")
        for f in sorted(files):
            rel_path = f.relative_to(PROJECT_ROOT)
            print(f"  - {rel_path}")


def cmd_show_structure():
    """显示后端目录结构"""
    print("后端模块结构:")
    print()

    for module_name, src_dir in [("core", CORE_SRC), ("common", COMMON_SRC)]:
        if not src_dir.exists():
            continue
        print(f"## {module_name}")

        # 统计各类文件
        controllers = len(find_java_files(src_dir, "Controller"))
        services = len(find_java_files(src_dir, "Service"))
        mappers = len(find_java_files(src_dir, "Mapper"))
        entities = len(find_java_files(src_dir, "Entity")) + len(find_java_files(src_dir, "Model"))

        print(f"  Controller: {controllers}")
        print(f"  Service: {services}")
        print(f"  Mapper: {mappers}")
        print(f"  Entity/Model: {entities}")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == 'check-service':
        if len(sys.argv) < 3:
            print("用法: backend_helper.py check-service <filename>")
            return
        cmd_check_service(sys.argv[2])
    elif cmd == 'find-hardcoded-sql':
        cmd_find_hardcoded_sql()
    elif cmd == 'find-hardcoded-prompt':
        cmd_find_hardcoded_prompt()
    elif cmd == 'list-services':
        cmd_list_services()
    elif cmd == 'list-controllers':
        cmd_list_controllers()
    elif cmd == 'show-structure':
        cmd_show_structure()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
