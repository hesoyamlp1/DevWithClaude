#!/usr/bin/env python3
"""
数据库迁移辅助脚本 - 供 LLM subagent 调用

命令:
    version                     显示当前 Flyway 版本
    next-name <description>     生成下一个迁移文件名
    list                        列出所有迁移文件
    schema <table>              显示表结构
    tables                      列出所有表
    check                       检查迁移文件规范

示例:
    python3 migration_helper.py version
    python3 migration_helper.py next-name add_user_table
    python3 migration_helper.py schema player
"""

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
MIGRATION_DIR = PROJECT_ROOT / "core/src/main/resources/db/migration"
DB_PATH = PROJECT_ROOT / "data/webrpg.db"


def cmd_version():
    """显示当前 Flyway 版本"""
    if not DB_PATH.exists():
        print("数据库不存在")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT version, description, installed_on, success
            FROM flyway_schema_history
            ORDER BY installed_rank DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()

        if rows:
            print("最近的迁移记录:")
            for row in rows:
                status = "✅" if row[3] else "❌"
                print(f"  {status} V{row[0]} - {row[1]} ({row[2]})")
        else:
            print("没有迁移记录")
    except sqlite3.OperationalError:
        print("flyway_schema_history 表不存在，数据库可能未初始化")
    finally:
        conn.close()


def cmd_next_name(description):
    """生成下一个迁移文件名"""
    if not MIGRATION_DIR.exists():
        print(f"迁移目录不存在: {MIGRATION_DIR}")
        return

    # 找到当前最大版本号
    max_version = 0
    for f in MIGRATION_DIR.glob("V*.sql"):
        match = re.match(r"V(\d+)__", f.name)
        if match:
            version = int(match.group(1))
            max_version = max(max_version, version)

    next_version = max_version + 1
    # 规范化描述: 转小写，空格换下划线
    clean_desc = description.lower().replace(" ", "_").replace("-", "_")
    filename = f"V{next_version}__{clean_desc}.sql"

    print(f"下一个版本号: V{next_version}")
    print(f"建议文件名: {filename}")
    print(f"完整路径: {MIGRATION_DIR / filename}")


def cmd_list():
    """列出所有迁移文件"""
    if not MIGRATION_DIR.exists():
        print(f"迁移目录不存在: {MIGRATION_DIR}")
        return

    files = sorted(MIGRATION_DIR.glob("V*.sql"))
    if not files:
        print("没有迁移文件")
        return

    print(f"迁移文件 ({len(files)} 个):")
    for f in files:
        print(f"  {f.name}")


def cmd_schema(table_name):
    """显示表结构"""
    if not DB_PATH.exists():
        print("数据库不存在")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        if not columns:
            print(f"表 {table_name} 不存在")
            return

        print(f"表 {table_name} 结构:")
        print("  列名 | 类型 | 非空 | 默认值 | 主键")
        print("  " + "-" * 50)
        for col in columns:
            pk = "✓" if col[5] else ""
            notnull = "✓" if col[3] else ""
            default = col[4] if col[4] else ""
            print(f"  {col[1]} | {col[2]} | {notnull} | {default} | {pk}")

        # 获取索引
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        if indexes:
            print(f"\n索引:")
            for idx in indexes:
                print(f"  {idx[1]}")

    finally:
        conn.close()


def cmd_tables():
    """列出所有表"""
    if not DB_PATH.exists():
        print("数据库不存在")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()

        if tables:
            print(f"数据库表 ({len(tables)} 个):")
            for t in tables:
                # 获取行数
                cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
                count = cursor.fetchone()[0]
                print(f"  {t[0]} ({count} 行)")
        else:
            print("没有表")
    finally:
        conn.close()


def cmd_check():
    """检查迁移文件规范"""
    if not MIGRATION_DIR.exists():
        print(f"迁移目录不存在: {MIGRATION_DIR}")
        return

    issues = []
    files = list(MIGRATION_DIR.glob("V*.sql"))

    for f in files:
        # 检查命名规范
        if not re.match(r"V\d+__[a-z0-9_]+\.sql", f.name):
            issues.append(f"命名不规范: {f.name} (应为 V<数字>__<小写描述>.sql)")

        # 检查文件内容
        content = f.read_text(encoding='utf-8')
        if not content.strip():
            issues.append(f"文件为空: {f.name}")

    if issues:
        print("发现问题:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print(f"✅ 所有 {len(files)} 个迁移文件检查通过")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == 'version':
        cmd_version()
    elif cmd == 'next-name':
        if len(sys.argv) < 3:
            print("用法: migration_helper.py next-name <description>")
            return
        cmd_next_name(' '.join(sys.argv[2:]))
    elif cmd == 'list':
        cmd_list()
    elif cmd == 'schema':
        if len(sys.argv) < 3:
            print("用法: migration_helper.py schema <table_name>")
            return
        cmd_schema(sys.argv[2])
    elif cmd == 'tables':
        cmd_tables()
    elif cmd == 'check':
        cmd_check()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
