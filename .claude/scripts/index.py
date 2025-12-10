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

Project 管理命令:
    project info                  项目概览
    project list [type]           列出资产 (models|apis|utils|components|all)
    project show <type> <name>    查看详情
    project search <keyword>      全局搜索
    project search --type <t> <kw>    按类型搜索
    project search --source <id>      按来源任务搜索
    project add <type> '<json>'   添加资产
    project update <type> '<json>'    更新资产
    project remove <type> <name>  删除资产
    project init '<json>'         初始化项目信息

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
  "models": ["Model名: 字段说明"],
  "apis": ["/api/path: 描述"],
  "utils": ["方法名: 描述"],
  "components": ["组件名: 描述"]
}

project add:
  model: {"name": "Actor", "table": "actor", "fields": ["id", "name"]}
  api:   {"path": "/api/actors", "methods": ["GET", "POST"], "desc": "说明"}
  util:  {"name": "copyActor", "layer": "backend", "desc": "说明"}
  component: {"name": "ActorCard", "desc": "说明"}

示例:
    python3 index.py task add '{"name": "Actor CRUD", "what": "实现基础CRUD"}'
    python3 index.py task done T001 '{"summary": "完成了Actor表和API"}'
    python3 index.py project search actor
    python3 index.py project add model '{"name": "Actor", "table": "actor", "fields": ["id"]}'
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
PROJECT_FILE = CLAUDE_DIR / "project.json"

# 资产类型
ASSET_TYPES = ['models', 'apis', 'utils', 'components']
ASSET_TYPE_ALIASES = {
    'model': 'models',
    'api': 'apis',
    'util': 'utils',
    'component': 'components'
}


def normalize_asset_type(t):
    """规范化资产类型名称"""
    if t in ASSET_TYPES:
        return t
    return ASSET_TYPE_ALIASES.get(t, t)


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


def load_project():
    """加载项目文件"""
    if not PROJECT_FILE.exists():
        return {
            "project": {"name": "", "type": ""},
            "stack": {"backend": "", "frontend": "", "database": ""},
            "conventions": {},
            "models": {},
            "apis": {},
            "utils": {},
            "components": {}
        }
    with open(PROJECT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_project(data):
    """保存项目文件"""
    with open(PROJECT_FILE, 'w', encoding='utf-8') as f:
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

    # 同步资产到 project.json
    if output:
        sync_output_to_project(task_id, output)


def sync_output_to_project(task_id, output):
    """将任务产出同步到 project.json"""
    synced = []

    # 同步 models (格式: "ModelName: 字段说明" 或 "ModelName")
    for item in output.get('models', []):
        name = item.split(':')[0].strip() if ':' in item else item.strip()
        if name:
            # 简单解析，创建基础记录
            project_data = load_project()
            if 'models' not in project_data:
                project_data['models'] = {}
            if name not in project_data['models']:
                project_data['models'][name] = {
                    'table': name.lower(),
                    'fields': [],
                    'source': task_id
                }
                save_project(project_data)
                synced.append(f"models.{name}")

    # 同步 apis (格式: "/api/path: 描述" 或 "GET /api/path")
    for item in output.get('apis', []):
        item = item.strip()
        if ':' in item:
            path = item.split(':')[0].strip()
            desc = item.split(':', 1)[1].strip() if ':' in item else ''
        else:
            parts = item.split()
            path = parts[-1] if parts else item
            desc = ''

        # 提取路径（去掉 HTTP 方法）
        if path.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            continue
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            if path.startswith(method + ' '):
                path = path[len(method):].strip()
                break

        if path and path.startswith('/'):
            project_data = load_project()
            if 'apis' not in project_data:
                project_data['apis'] = {}
            if path not in project_data['apis']:
                project_data['apis'][path] = {
                    'methods': ['GET'],
                    'desc': desc,
                    'source': task_id
                }
                save_project(project_data)
                synced.append(f"apis.{path}")

    # 同步 utils (格式: "MethodName: 描述" 或 "Class.method: 描述")
    for item in output.get('utils', []):
        name = item.split(':')[0].strip() if ':' in item else item.strip()
        desc = item.split(':', 1)[1].strip() if ':' in item else ''
        if name:
            project_data = load_project()
            if 'utils' not in project_data:
                project_data['utils'] = {}
            if name not in project_data['utils']:
                # 推断 layer
                layer = 'backend'
                if name.startswith('use') or name.endswith('Hook'):
                    layer = 'frontend'
                project_data['utils'][name] = {
                    'layer': layer,
                    'desc': desc,
                    'source': task_id
                }
                save_project(project_data)
                synced.append(f"utils.{name}")

    # 同步 components (格式: "ComponentName: 描述")
    for item in output.get('components', []):
        name = item.split(':')[0].strip() if ':' in item else item.strip()
        desc = item.split(':', 1)[1].strip() if ':' in item else ''
        if name:
            project_data = load_project()
            if 'components' not in project_data:
                project_data['components'] = {}
            if name not in project_data['components']:
                project_data['components'][name] = {
                    'desc': desc,
                    'source': task_id
                }
                save_project(project_data)
                synced.append(f"components.{name}")

    if synced:
        print(f"   📦 已同步到 project.json: {', '.join(synced)}")


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


# ============ Project 命令实现 ============

def cmd_project_info():
    """显示项目概览"""
    data = load_project()

    print("=== 项目概览 ===\n")

    proj = data.get('project', {})
    if proj.get('name'):
        print(f"名称: {proj['name']}")
    if proj.get('type'):
        print(f"类型: {proj['type']}")
    print("")

    stack = data.get('stack', {})
    if any(stack.values()):
        print("技术栈:")
        if stack.get('backend'):
            print(f"  Backend: {stack['backend']}")
        if stack.get('frontend'):
            print(f"  Frontend: {stack['frontend']}")
        if stack.get('database'):
            print(f"  Database: {stack['database']}")
        print("")

    conv = data.get('conventions', {})
    if conv:
        print("命名规范:")
        for key, val in conv.items():
            print(f"  {key}: {val}")
        print("")

    # 资产统计
    counts = []
    for asset_type in ASSET_TYPES:
        count = len(data.get(asset_type, {}))
        if count > 0:
            counts.append(f"{asset_type}: {count}")
    if counts:
        print(f"资产: {', '.join(counts)}")


def cmd_project_list(asset_type=None):
    """列出资产"""
    data = load_project()

    if asset_type and asset_type != 'all':
        asset_type = normalize_asset_type(asset_type)
        if asset_type not in ASSET_TYPES:
            print(f"错误: 未知类型 '{asset_type}'，可选: {', '.join(ASSET_TYPES)}")
            return
        types_to_show = [asset_type]
    else:
        types_to_show = ASSET_TYPES

    for t in types_to_show:
        assets = data.get(t, {})
        if not assets:
            continue

        print(f"=== {t.upper()} ({len(assets)}) ===\n")

        for name, info in assets.items():
            if t == 'models':
                fields = ', '.join(info.get('fields', [])[:5])
                if len(info.get('fields', [])) > 5:
                    fields += '...'
                print(f"  {name} ({info.get('table', '?')})")
                print(f"    fields: [{fields}]")
            elif t == 'apis':
                methods = ', '.join(info.get('methods', []))
                print(f"  {name}")
                print(f"    [{methods}] {info.get('desc', '')}")
            elif t == 'utils':
                layer = info.get('layer', 'unknown')
                print(f"  {name} [{layer}]")
                print(f"    {info.get('desc', '')}")
            elif t == 'components':
                print(f"  {name}")
                print(f"    {info.get('desc', '')}")

            if info.get('source'):
                print(f"    source: {info['source']}")
            print("")


def cmd_project_show(asset_type, name):
    """查看资产详情"""
    data = load_project()
    asset_type = normalize_asset_type(asset_type)

    if asset_type not in ASSET_TYPES:
        print(f"错误: 未知类型 '{asset_type}'，可选: {', '.join(ASSET_TYPES)}")
        return

    assets = data.get(asset_type, {})
    if name not in assets:
        print(f"错误: {asset_type} 中没有 '{name}'")
        return

    info = assets[name]
    print(f"=== {asset_type}.{name} ===\n")
    print(json.dumps(info, ensure_ascii=False, indent=2))


def cmd_project_search(keyword, asset_type=None, source=None):
    """搜索资产"""
    data = load_project()
    keyword_lower = keyword.lower() if keyword else None
    results = []

    if asset_type:
        asset_type = normalize_asset_type(asset_type)
    types_to_search = [asset_type] if asset_type else ASSET_TYPES

    for t in types_to_search:
        if t not in ASSET_TYPES:
            continue
        assets = data.get(t, {})

        for name, info in assets.items():
            # 按来源搜索
            if source:
                if info.get('source') == source:
                    results.append((t, name, info))
                continue

            # 按关键词搜索
            if keyword_lower:
                # 搜索名称
                if keyword_lower in name.lower():
                    results.append((t, name, info))
                    continue

                # 搜索描述
                if keyword_lower in str(info.get('desc', '')).lower():
                    results.append((t, name, info))
                    continue

                # 搜索表名
                if keyword_lower in str(info.get('table', '')).lower():
                    results.append((t, name, info))
                    continue

                # 搜索字段
                fields = info.get('fields', [])
                if any(keyword_lower in f.lower() for f in fields):
                    results.append((t, name, info))
                    continue

    if not results:
        if source:
            print(f"没有找到来源为 {source} 的资产")
        else:
            print(f"没有找到匹配 '{keyword}' 的资产")
        return

    print(f"=== 搜索结果 ({len(results)}) ===\n")
    for t, name, info in results:
        source_str = f" [{info.get('source')}]" if info.get('source') else ""
        desc = info.get('desc', '')
        if t == 'models':
            desc = f"table: {info.get('table', '?')}"
        print(f"  [{t}] {name}{source_str}")
        if desc:
            print(f"    {desc}")
        print("")


def cmd_project_add(asset_type, json_str, task_id=None):
    """添加资产"""
    asset_type = normalize_asset_type(asset_type)
    if asset_type not in ASSET_TYPES:
        print(f"错误: 未知类型 '{asset_type}'，可选: {', '.join(ASSET_TYPES)}")
        return False

    try:
        asset_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败 - {e}")
        return False

    # 获取名称
    if asset_type == 'apis':
        name = asset_data.get('path')
        if not name:
            print("错误: API 需要 'path' 字段")
            return False
    else:
        name = asset_data.get('name')
        if not name:
            print("错误: 缺少 'name' 字段")
            return False

    data = load_project()

    if asset_type not in data:
        data[asset_type] = {}

    # 构建资产信息
    info = {}
    if asset_type == 'models':
        info['table'] = asset_data.get('table', name.lower())
        info['fields'] = asset_data.get('fields', [])
    elif asset_type == 'apis':
        info['methods'] = asset_data.get('methods', ['GET'])
        info['desc'] = asset_data.get('desc', '')
    elif asset_type == 'utils':
        info['layer'] = asset_data.get('layer', 'unknown')
        info['desc'] = asset_data.get('desc', '')
    elif asset_type == 'components':
        info['desc'] = asset_data.get('desc', '')

    if task_id:
        info['source'] = task_id
    elif asset_data.get('source'):
        info['source'] = asset_data['source']

    data[asset_type][name] = info
    save_project(data)

    print(f"✅ 已添加 {asset_type}.{name}")
    return True


def cmd_project_update(asset_type, json_str):
    """更新资产（覆盖）"""
    return cmd_project_add(asset_type, json_str)


def cmd_project_remove(asset_type, name):
    """删除资产"""
    asset_type = normalize_asset_type(asset_type)
    if asset_type not in ASSET_TYPES:
        print(f"错误: 未知类型 '{asset_type}'，可选: {', '.join(ASSET_TYPES)}")
        return False

    data = load_project()

    if asset_type not in data or name not in data[asset_type]:
        print(f"错误: {asset_type} 中没有 '{name}'")
        return False

    del data[asset_type][name]
    save_project(data)

    print(f"✅ 已删除 {asset_type}.{name}")
    return True


def cmd_project_init(json_str):
    """初始化项目信息"""
    try:
        init_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败 - {e}")
        return

    data = load_project()

    # 更新项目信息
    if init_data.get('name'):
        data['project']['name'] = init_data['name']
    if init_data.get('type'):
        data['project']['type'] = init_data['type']

    # 更新技术栈
    if init_data.get('stack'):
        data['stack'].update(init_data['stack'])

    # 更新命名规范
    if init_data.get('conventions'):
        if 'conventions' not in data:
            data['conventions'] = {}
        data['conventions'].update(init_data['conventions'])

    save_project(data)
    print("✅ 项目信息已更新")
    cmd_project_info()


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

    elif cmd == 'project':
        if len(args) < 2:
            print("用法: index.py project <info|list|show|search|add|update|remove|init>")
            return

        subcmd = args[1]

        if subcmd == 'info':
            cmd_project_info()

        elif subcmd == 'list':
            asset_type = args[2] if len(args) > 2 else None
            cmd_project_list(asset_type)

        elif subcmd == 'show':
            if len(args) < 4:
                print("用法: index.py project show <type> <name>")
                print(f"  type: {', '.join(ASSET_TYPES)}")
                return
            cmd_project_show(args[2], args[3])

        elif subcmd == 'search':
            keyword = None
            asset_type = None
            source = None

            # 解析参数
            i = 2
            while i < len(args):
                if args[i] == '--type' and i + 1 < len(args):
                    asset_type = args[i + 1]
                    i += 2
                elif args[i] == '--source' and i + 1 < len(args):
                    source = args[i + 1]
                    i += 2
                elif not keyword and not args[i].startswith('--'):
                    keyword = args[i]
                    i += 1
                else:
                    i += 1

            if not keyword and not source:
                print("用法: index.py project search <keyword>")
                print("      index.py project search --type <type> <keyword>")
                print("      index.py project search --source <task_id>")
                return

            cmd_project_search(keyword, asset_type=asset_type, source=source)

        elif subcmd == 'add':
            if len(args) < 4:
                print("用法: index.py project add <type> '<json>'")
                print(f"  type: {', '.join(ASSET_TYPES)}")
                return
            cmd_project_add(args[2], args[3])

        elif subcmd == 'update':
            if len(args) < 4:
                print("用法: index.py project update <type> '<json>'")
                return
            cmd_project_update(args[2], args[3])

        elif subcmd == 'remove':
            if len(args) < 4:
                print("用法: index.py project remove <type> <name>")
                return
            cmd_project_remove(args[2], args[3])

        elif subcmd == 'init':
            if len(args) < 3:
                print("用法: index.py project init '<json>'")
                print('示例: index.py project init \'{"name": "MyApp", "type": "web-app"}\'')
                return
            cmd_project_init(args[2])

        else:
            print(f"未知子命令: {subcmd}")

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
