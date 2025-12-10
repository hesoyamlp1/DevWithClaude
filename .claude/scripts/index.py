#!/usr/bin/env python3
"""
项目任务管理脚本

Task 管理命令:
    task list                     列出活跃任务
    task next                     显示下一个任务（含依赖产出）
    task show <id>                显示任务详情
    task add '<json>'             添加任务（JSON格式）
    task start <id>               开始任务
    task done <id> '<json>'       完成任务（JSON格式的output）
    task history                  查看归档历史
    task history --search <keyword>  搜索归档

JSON 格式示例:

task add:
{
  "name": "任务名称",
  "what": "要做什么",
  "boundary": ["不做什么"],
  "constraints": ["约束"],
  "done_when": ["完成标准"],
  "depends_on": ["T001"]
}

task done:
{
  "summary": "一句话总结",
  "models": ["数据结构"],
  "apis": ["接口"],
  "utils": ["工具方法"]
}

示例:
    python3 index.py task add '{"name": "Actor CRUD", "what": "实现基础CRUD"}'
    python3 index.py task done T001 '{"summary": "完成了Actor表和API"}'
"""

import io
import json
import sys
from datetime import datetime
from pathlib import Path

# 修复 Windows 终端中文乱码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 路径配置
SCRIPT_DIR = Path(__file__).parent
CLAUDE_DIR = SCRIPT_DIR.parent
TASKS_FILE = CLAUDE_DIR / "tasks.json"


def load_tasks():
    """加载任务文件"""
    if not TASKS_FILE.exists():
        return {"active": [], "archived": []}
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tasks(data):
    """保存任务文件"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_task_id(data):
    """生成下一个任务 ID"""
    all_ids = []
    for task in data.get('active', []):
        all_ids.append(task['id'])
    for task in data.get('archived', []):
        all_ids.append(task['id'])

    if not all_ids:
        return "T001"

    max_num = 0
    for tid in all_ids:
        if tid.startswith('T') and tid[1:].isdigit():
            max_num = max(max_num, int(tid[1:]))
    return f"T{max_num + 1:03d}"


def find_task_in_active(data, task_id):
    """在活跃区查找任务"""
    for task in data.get('active', []):
        if task['id'] == task_id:
            return task
    return None


def find_task_in_archived(data, task_id):
    """在归档区查找任务"""
    for task in data.get('archived', []):
        if task['id'] == task_id:
            return task
    return None


def get_dependency_outputs(data, depends_on):
    """获取依赖任务的产出"""
    outputs = []
    for dep_id in depends_on or []:
        task = find_task_in_archived(data, dep_id)
        if task and task.get('output'):
            outputs.append({
                'id': task['id'],
                'name': task['name'],
                'output': task['output']
            })
        else:
            task = find_task_in_active(data, dep_id)
            if task and task.get('status') == 'completed' and task.get('output'):
                outputs.append({
                    'id': task['id'],
                    'name': task['name'],
                    'output': task['output']
                })
    return outputs


def format_task_detail(task, dep_outputs=None):
    """格式化任务详情"""
    lines = []
    lines.append(f"=== {task['id']}: {task['name']} ===")
    lines.append("")

    if task.get('status'):
        lines.append(f"状态: {task['status']}")
        lines.append("")

    if task.get('what'):
        lines.append(f"## What")
        lines.append(task['what'])
        lines.append("")

    if task.get('boundary'):
        lines.append(f"## Boundary")
        for item in task['boundary']:
            lines.append(f"  - {item}")
        lines.append("")

    if task.get('constraints'):
        lines.append(f"## Constraints")
        for item in task['constraints']:
            lines.append(f"  - {item}")
        lines.append("")

    if task.get('done_when'):
        lines.append(f"## Done When")
        for item in task['done_when']:
            lines.append(f"  - {item}")
        lines.append("")

    if task.get('depends_on'):
        lines.append(f"## 依赖: {', '.join(task['depends_on'])}")
        lines.append("")

    if dep_outputs:
        lines.append("=" * 40)
        lines.append("## 依赖任务产出")
        lines.append("")
        for dep in dep_outputs:
            lines.append(f"### [{dep['id']}] {dep['name']}")
            output = dep['output']
            if isinstance(output, dict):
                if output.get('summary'):
                    lines.append(f"  {output['summary']}")
                if output.get('models'):
                    lines.append(f"  Models: {', '.join(output['models'])}")
                if output.get('apis'):
                    lines.append(f"  APIs: {', '.join(output['apis'])}")
                if output.get('utils'):
                    lines.append(f"  Utils: {', '.join(output['utils'])}")
            else:
                lines.append(f"  {output}")
            lines.append("")

    return '\n'.join(lines)


def format_archived_task(task):
    """格式化归档任务"""
    lines = []
    lines.append(f"=== [{task['id']}] {task['name']} ===")
    lines.append(f"完成时间: {task.get('completed_at', 'N/A')}")
    lines.append("")

    output = task.get('output', {})
    if isinstance(output, dict):
        if output.get('summary'):
            lines.append(f"Summary: {output['summary']}")
        if output.get('models'):
            lines.append(f"Models:")
            for m in output['models']:
                lines.append(f"  - {m}")
        if output.get('apis'):
            lines.append(f"APIs:")
            for a in output['apis']:
                lines.append(f"  - {a}")
        if output.get('utils'):
            lines.append(f"Utils:")
            for u in output['utils']:
                lines.append(f"  - {u}")
    else:
        lines.append(f"Output: {output}")

    return '\n'.join(lines)


# ============ 命令实现 ============

def cmd_task_list():
    """列出活跃任务"""
    data = load_tasks()
    active = data.get('active', [])

    if not active:
        print("没有活跃任务")
        return

    print("=== 活跃任务 ===\n")

    in_progress = [t for t in active if t.get('status') == 'in_progress']
    pending = [t for t in active if t.get('status') == 'pending']

    if in_progress:
        print("进行中:")
        for t in in_progress:
            print(f"  🔄 [{t['id']}] {t['name']}")
        print("")

    if pending:
        print("待处理:")
        for t in pending:
            deps = t.get('depends_on', [])
            dep_str = f" (依赖: {', '.join(deps)})" if deps else ""
            print(f"  ⏳ [{t['id']}] {t['name']}{dep_str}")
        print("")

    print(f"共 {len(active)} 个活跃任务")


def cmd_task_next():
    """显示下一个任务"""
    data = load_tasks()
    active = data.get('active', [])

    in_progress = [t for t in active if t.get('status') == 'in_progress']
    if in_progress:
        task = in_progress[0]
        dep_outputs = get_dependency_outputs(data, task.get('depends_on'))
        print(format_task_detail(task, dep_outputs))
        print("\n💡 当前有进行中的任务")
        return

    archived_ids = {t['id'] for t in data.get('archived', [])}
    completed_active_ids = {t['id'] for t in active if t.get('status') == 'completed'}
    all_completed = archived_ids | completed_active_ids

    for task in active:
        if task.get('status') != 'pending':
            continue
        deps = task.get('depends_on', [])
        if all(dep in all_completed for dep in deps):
            dep_outputs = get_dependency_outputs(data, deps)
            print(format_task_detail(task, dep_outputs))
            return

    print("没有可执行的待处理任务")


def cmd_task_show(task_id):
    """显示任务详情"""
    data = load_tasks()

    task = find_task_in_active(data, task_id)
    if task:
        dep_outputs = get_dependency_outputs(data, task.get('depends_on'))
        print(format_task_detail(task, dep_outputs))
        return

    task = find_task_in_archived(data, task_id)
    if task:
        print(format_archived_task(task))
        return

    print(f"任务 {task_id} 不存在")


def cmd_task_add(json_str):
    """添加任务（JSON格式）"""
    try:
        task_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败 - {e}")
        return None

    if 'name' not in task_data:
        print("错误: 缺少必填字段 'name'")
        return None

    data = load_tasks()
    task_id = get_next_task_id(data)

    task = {
        "id": task_id,
        "name": task_data['name'],
        "status": "pending"
    }

    # 可选字段
    if task_data.get('what'):
        task['what'] = task_data['what']
    if task_data.get('boundary'):
        task['boundary'] = task_data['boundary']
    if task_data.get('constraints'):
        task['constraints'] = task_data['constraints']
    if task_data.get('done_when'):
        task['done_when'] = task_data['done_when']
    if task_data.get('depends_on'):
        task['depends_on'] = task_data['depends_on']

    if 'active' not in data:
        data['active'] = []
    data['active'].append(task)
    save_tasks(data)

    print(f"✅ 任务 {task_id} 已添加: {task['name']}")
    return task_id


def cmd_task_start(task_id):
    """开始任务"""
    data = load_tasks()
    task = find_task_in_active(data, task_id)

    if not task:
        print(f"错误: 任务 {task_id} 不存在或已归档")
        return

    if task.get('status') == 'in_progress':
        print(f"任务 {task_id} 已经在进行中")
        dep_outputs = get_dependency_outputs(data, task.get('depends_on'))
        print(format_task_detail(task, dep_outputs))
        return

    if task.get('status') == 'completed':
        print(f"任务 {task_id} 已完成")
        return

    task['status'] = 'in_progress'
    task['started_at'] = datetime.now().isoformat()
    save_tasks(data)

    print(f"✅ 任务 {task_id} 已开始\n")
    dep_outputs = get_dependency_outputs(data, task.get('depends_on'))
    print(format_task_detail(task, dep_outputs))


def cmd_task_done(task_id, json_str=None):
    """完成任务（JSON格式的output）"""
    data = load_tasks()
    task = find_task_in_active(data, task_id)

    if not task:
        print(f"错误: 任务 {task_id} 不存在或已归档")
        return

    output = {}
    if json_str:
        try:
            output = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"错误: JSON 解析失败 - {e}")
            return

    # 创建归档记录
    archived_task = {
        "id": task['id'],
        "name": task['name'],
        "completed_at": datetime.now().strftime('%Y-%m-%d')
    }
    if output:
        archived_task["output"] = output

    # 从活跃区移除
    data['active'] = [t for t in data['active'] if t['id'] != task_id]

    # 添加到归档区
    if 'archived' not in data:
        data['archived'] = []
    data['archived'].append(archived_task)

    save_tasks(data)

    print(f"✅ 任务 {task_id} 已完成并归档")
    if output.get('summary'):
        print(f"   Summary: {output['summary']}")


def cmd_task_history(task_id=None, search=None, last=None):
    """查看归档历史"""
    data = load_tasks()
    archived = data.get('archived', [])

    if not archived:
        print("没有归档任务")
        return

    if task_id:
        task = find_task_in_archived(data, task_id)
        if task:
            print(format_archived_task(task))
        else:
            print(f"归档中没有任务 {task_id}")
        return

    if search:
        results = []
        search_lower = search.lower()
        for task in archived:
            if search_lower in task['name'].lower():
                results.append(task)
                continue
            output = task.get('output', {})
            if isinstance(output, dict):
                for value in output.values():
                    if isinstance(value, list):
                        if any(search_lower in str(v).lower() for v in value):
                            results.append(task)
                            break
                    elif search_lower in str(value).lower():
                        results.append(task)
                        break
        archived = results

    if last:
        archived = archived[-last:]

    if not archived:
        print(f"没有找到匹配的归档任务")
        return

    print(f"=== 归档任务 ({len(archived)} 条) ===\n")
    for task in archived:
        output = task.get('output', {})
        summary = output.get('summary', '') if isinstance(output, dict) else ''
        print(f"[{task['id']}] {task['name']}")
        print(f"    完成: {task.get('completed_at', 'N/A')} | {summary}")
        print("")


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    cmd = args[0]

    if cmd == 'task':
        if len(args) < 2:
            print("用法: index.py task <list|next|show|add|start|done|history>")
            return

        subcmd = args[1]

        if subcmd == 'list':
            cmd_task_list()

        elif subcmd == 'next':
            cmd_task_next()

        elif subcmd == 'show':
            if len(args) < 3:
                print("用法: index.py task show <task_id>")
                return
            cmd_task_show(args[2])

        elif subcmd == 'add':
            if len(args) < 3:
                print("用法: index.py task add '<json>'")
                print('示例: index.py task add \'{"name": "任务名", "what": "要做什么"}\'')
                return
            cmd_task_add(args[2])

        elif subcmd == 'start':
            if len(args) < 3:
                print("用法: index.py task start <task_id>")
                return
            cmd_task_start(args[2])

        elif subcmd == 'done':
            if len(args) < 3:
                print("用法: index.py task done <task_id> '<json>'")
                print('示例: index.py task done T001 \'{"summary": "完成了xxx"}\'')
                return
            task_id = args[2]
            json_str = args[3] if len(args) > 3 else None
            cmd_task_done(task_id, json_str)

        elif subcmd == 'history':
            task_id = None
            search = None
            last = None

            if '--id' in args:
                idx = args.index('--id') + 1
                task_id = args[idx] if idx < len(args) else None

            if '--search' in args:
                idx = args.index('--search') + 1
                search = args[idx] if idx < len(args) else None

            if '--last' in args:
                idx = args.index('--last') + 1
                last = int(args[idx]) if idx < len(args) else None

            cmd_task_history(task_id=task_id, search=search, last=last)

        else:
            print(f"未知子命令: {subcmd}")

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
