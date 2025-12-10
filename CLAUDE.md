# 项目开发指南

## 开发流程

```
/init-project → /plan → /run → /test
     ↓            ↓        ↓       ↓
  填充skills   拆分任务  执行开发  运行测试
  +project.json
```

## 命令

| 命令 | 用途 |
|-----|------|
| `/init-project` | 检测技术栈，填充 skills，初始化 project.json |
| `/plan` | 聊完需求后，生成 design.md + 拆分任务 |
| `/run` | 自动执行所有 active 任务 |
| `/test` | 运行单元测试 |

## 管理脚本

```bash
# 路径
python3 .claude/scripts/index.py <command>
```

### Task 命令

```bash
# 查看任务
task list                    # 列出活跃任务
task next                    # 下一个任务（含依赖产出）
task show <id>               # 查看详情

# 管理任务（JSON格式）
task add '<json>'            # 添加任务
task start <id>              # 开始任务
task done <id> '<json>'      # 完成任务（自动同步到 project.json）

# 查看历史
task history                 # 归档任务
task history --search <keyword>
```

### Project 命令

```bash
# 查询
project info                       # 项目概览
project list [type]                # 列出资产 (models|apis|utils|components|all)
project show <type> <name>         # 查看详情
project search <keyword>           # 全局搜索
project search --type <t> <kw>     # 按类型搜索
project search --source <task_id>  # 按来源搜索

# 管理
project add <type> '<json>'        # 添加资产
project update <type> '<json>'     # 更新资产
project remove <type> <name>       # 删除资产
project init '<json>'              # 初始化项目信息
```

### JSON 格式

**Task 添加:**
```json
{
  "name": "任务名称",
  "what": "要做什么",
  "boundary": ["不做什么"],
  "constraints": ["约束"],
  "done_when": ["完成标准"],
  "depends_on": ["T001"]
}
```

**Task 完成:** (自动同步到 project.json)
```json
{
  "summary": "一句话总结",
  "models": ["ModelName: 字段说明"],
  "apis": ["/api/path: 描述"],
  "utils": ["MethodName: 描述"],
  "components": ["ComponentName: 描述"]
}
```

**Project 资产:**
```json
// model
{"name": "Actor", "table": "actor", "fields": ["id", "name"]}

// api
{"path": "/api/actors", "methods": ["GET", "POST"], "desc": "说明"}

// util
{"name": "copyActor", "layer": "backend", "desc": "说明"}

// component
{"name": "ActorCard", "desc": "说明"}

// init
{"name": "MyApp", "type": "web-app", "stack": {"backend": "java/spring-boot"}}
```

## Task 四要素

每个任务必须明确：

| 字段 | 说明 |
|-----|------|
| **what** | 要做什么 |
| **boundary** | 不做什么 |
| **constraints** | 约束条件 |
| **done_when** | 完成标准 |

## Output 四要素

完成时必须记录（自动同步到 project.json）：

| 字段 | 说明 |
|-----|------|
| **summary** | 一句话总结 |
| **models** | 数据结构变更 |
| **apis** | 接口变更 |
| **utils** | 可复用方法 |
| **components** | 前端组件 |

## 文件结构

```
.claude/
├── project.json       # 项目资产汇总（models/apis/utils/components）
├── tasks.json         # 任务队列（active + archived）
├── design.md          # 当前设计文档
├── designs/           # 历史设计归档
├── scripts/
│   └── index.py       # 管理脚本
├── skills/            # 领域知识
├── commands/          # 斜杠命令
└── agents/            # subagent 定义
```

## Skills 使用

按需调用：

| Skill | 何时使用 |
|-------|---------|
| `backend-dev` | 后端开发 |
| `frontend-dev` | 前端开发 |
| `database-migration` | 数据库变更 |
| `prompt-template` | 提示词模板 |
