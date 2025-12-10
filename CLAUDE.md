# 项目开发指南

## 开发流程

```
/init-project → /plan → /run → /test
     ↓            ↓        ↓       ↓
  填充skills   拆分任务  执行开发  运行测试
```

## 命令

| 命令 | 用途 |
|-----|------|
| `/init-project` | 检测技术栈，填充 skills |
| `/plan` | 聊完需求后，生成 design.md + 拆分任务 |
| `/run` | 自动执行所有 active 任务 |
| `/test` | 运行单元测试 |

## 任务管理脚本

```bash
# 路径
python3 .claude/scripts/index.py <command>

# 查看任务
task list                    # 列出活跃任务
task next                    # 下一个任务（含依赖产出）
task show <id>               # 查看详情

# 管理任务（JSON格式）
task add '<json>'            # 添加任务
task start <id>              # 开始任务
task done <id> '<json>'      # 完成任务

# 查看历史
task history                 # 归档任务
task history --search <keyword>
```

### JSON 格式

**添加任务:**
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

**完成任务:**
```json
{
  "summary": "一句话总结",
  "models": ["数据结构"],
  "apis": ["接口"],
  "utils": ["工具方法"]
}
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

完成时必须记录：

| 字段 | 说明 |
|-----|------|
| **summary** | 一句话总结 |
| **models** | 数据结构变更 |
| **apis** | 接口变更 |
| **utils** | 可复用方法 |

## 文件结构

```
.claude/
├── design.md          # 当前设计文档
├── designs/           # 历史设计归档
├── tasks.json         # 任务队列（active + archived）
├── scripts/
│   └── index.py       # 任务管理脚本
├── skills/            # 领域知识
│   ├── backend-dev/
│   ├── frontend-dev/
│   └── database-migration/
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
