#!/usr/bin/env python3
"""
前端代码检查脚本 - 供 LLM subagent 调用

命令:
    check-component <file>      检查组件规范
    find-inline-styles          查找内联样式
    find-css-imports            查找 CSS 文件导入
    list-pages                  列出所有页面组件
    list-components             列出所有可复用组件
    show-structure              显示前端目录结构
    check-store-usage           检查状态管理使用

示例:
    python3 frontend_helper.py check-component SessionChat.tsx
    python3 frontend_helper.py find-inline-styles
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
FRONTEND_SRC = PROJECT_ROOT / "rpg-frontend/src"


def find_tsx_files(base_path, pattern=None):
    """查找 TSX/TS 文件"""
    if not base_path.exists():
        return []
    files = list(base_path.rglob("*.tsx"))
    files.extend(base_path.rglob("*.ts"))
    if pattern:
        files = [f for f in files if pattern in f.name]
    return files


def cmd_check_component(filename):
    """检查组件规范"""
    files = find_tsx_files(FRONTEND_SRC, filename)

    if not files:
        print(f"未找到文件: {filename}")
        return

    for file_path in files:
        print(f"检查文件: {file_path}")
        content = file_path.read_text(encoding='utf-8')
        issues = []
        warnings = []

        # 检查内联样式
        if 'style={{' in content or 'style={' in content:
            issues.append("使用了内联样式，应使用 Mantine 组件属性")

        # 检查 CSS 导入
        if re.search(r"import\s+['\"].*\.css['\"]", content):
            issues.append("导入了 CSS 文件，应使用 Mantine 样式系统")

        # 检查是否在可复用组件中直接使用全局状态
        if '/components/' in str(file_path):
            if 'useAppStore' in content:
                warnings.append("可复用组件直接使用了全局状态，建议通过 props 传递")

        # 检查是否有加载状态
        if 'await' in content or '.then(' in content:
            if 'loading' not in content.lower() and 'isLoading' not in content:
                warnings.append("异步操作缺少加载状态处理")

        # 检查是否有错误处理
        if 'await' in content or '.then(' in content:
            if 'error' not in content.lower() and 'catch' not in content:
                warnings.append("异步操作缺少错误处理")

        # 检查直接使用 axios
        if 'import axios' in content or 'from \'axios\'' in content:
            if 'client' not in file_path.name.lower():
                warnings.append("直接导入 axios，应使用 client 实例")

        if issues:
            print("问题 (需要修复):")
            for issue in issues:
                print(f"  ❌ {issue}")

        if warnings:
            print("警告 (建议修复):")
            for warn in warnings:
                print(f"  ⚠️ {warn}")

        if not issues and not warnings:
            print("✅ 未发现明显问题")
        print()


def cmd_find_inline_styles():
    """查找内联样式"""
    print("查找内联样式...")
    found = []

    for file_path in find_tsx_files(FRONTEND_SRC):
        content = file_path.read_text(encoding='utf-8')
        if 'style={{' in content or re.search(r'style=\{[^{]', content):
            rel_path = file_path.relative_to(PROJECT_ROOT)
            # 统计数量
            count = content.count('style={{') + len(re.findall(r'style=\{[^{]', content))
            found.append((str(rel_path), count))

    if found:
        print(f"发现 {len(found)} 个文件使用内联样式:")
        for f, count in found:
            print(f"  - {f} ({count} 处)")
    else:
        print("✅ 未发现内联样式")


def cmd_find_css_imports():
    """查找 CSS 文件导入"""
    print("查找 CSS 文件导入...")
    found = []

    for file_path in find_tsx_files(FRONTEND_SRC):
        content = file_path.read_text(encoding='utf-8')
        if re.search(r"import\s+['\"].*\.css['\"]", content):
            rel_path = file_path.relative_to(PROJECT_ROOT)
            found.append(str(rel_path))

    # 也查找 CSS 文件
    css_files = list(FRONTEND_SRC.rglob("*.css"))

    if found:
        print(f"发现 {len(found)} 个文件导入 CSS:")
        for f in found:
            print(f"  - {f}")

    if css_files:
        print(f"\n发现 {len(css_files)} 个 CSS 文件:")
        for f in css_files:
            rel_path = f.relative_to(PROJECT_ROOT)
            print(f"  - {rel_path}")

    if not found and not css_files:
        print("✅ 未发现 CSS 文件使用")


def cmd_list_pages():
    """列出所有页面组件"""
    pages_dir = FRONTEND_SRC / "pages"
    if not pages_dir.exists():
        print("pages 目录不存在")
        return

    print("页面组件:")
    for f in sorted(pages_dir.rglob("*.tsx")):
        rel_path = f.relative_to(FRONTEND_SRC)
        print(f"  - {rel_path}")


def cmd_list_components():
    """列出所有可复用组件"""
    components_dir = FRONTEND_SRC / "components"
    if not components_dir.exists():
        print("components 目录不存在")
        return

    print("可复用组件:")
    for f in sorted(components_dir.rglob("*.tsx")):
        rel_path = f.relative_to(FRONTEND_SRC)
        print(f"  - {rel_path}")


def cmd_show_structure():
    """显示前端目录结构"""
    print("前端目录结构:")
    print()

    dirs_to_check = ['api', 'store', 'types', 'pages', 'components', 'hooks']

    for dir_name in dirs_to_check:
        dir_path = FRONTEND_SRC / dir_name
        if dir_path.exists():
            files = list(dir_path.rglob("*.ts")) + list(dir_path.rglob("*.tsx"))
            print(f"{dir_name}/ ({len(files)} 个文件)")
            for f in sorted(files)[:5]:  # 最多显示5个
                print(f"  - {f.name}")
            if len(files) > 5:
                print(f"  ... 还有 {len(files) - 5} 个文件")
            print()


def cmd_check_store_usage():
    """检查状态管理使用"""
    print("检查状态管理使用...")

    zustand_usage = []
    usestate_usage = []

    for file_path in find_tsx_files(FRONTEND_SRC):
        content = file_path.read_text(encoding='utf-8')
        rel_path = file_path.relative_to(PROJECT_ROOT)

        has_zustand = 'useAppStore' in content or 'useStore' in content
        has_usestate = 'useState' in content

        if has_zustand:
            zustand_usage.append(str(rel_path))
        if has_usestate:
            usestate_usage.append(str(rel_path))

    print(f"使用 Zustand (全局状态): {len(zustand_usage)} 个文件")
    for f in zustand_usage[:10]:
        print(f"  - {f}")
    if len(zustand_usage) > 10:
        print(f"  ... 还有 {len(zustand_usage) - 10} 个文件")

    print(f"\n使用 useState (组件状态): {len(usestate_usage)} 个文件")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == 'check-component':
        if len(sys.argv) < 3:
            print("用法: frontend_helper.py check-component <filename>")
            return
        cmd_check_component(sys.argv[2])
    elif cmd == 'find-inline-styles':
        cmd_find_inline_styles()
    elif cmd == 'find-css-imports':
        cmd_find_css_imports()
    elif cmd == 'list-pages':
        cmd_list_pages()
    elif cmd == 'list-components':
        cmd_list_components()
    elif cmd == 'show-structure':
        cmd_show_structure()
    elif cmd == 'check-store-usage':
        cmd_check_store_usage()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
