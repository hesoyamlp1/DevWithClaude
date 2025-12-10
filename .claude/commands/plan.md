# 规划任务

聊完需求后，生成设计文档并拆分任务。

**使用时机**: 需求讨论结束，准备开始开发时。

## 执行步骤

### 1. 归档现有 design（如有）

```bash
# 检查是否存在 design.md
if [ -f .claude/design.md ]; then
    # 归档到 designs/ 目录，以时间戳命名
    mkdir -p .claude/designs
    mv .claude/design.md ".claude/designs/$(date +%Y%m%d-%H%M%S).md"
    echo "已归档现有 design.md"
fi
```

### 2. 回顾对话内容

从本次会话中提取：
- **需求**: 用户想要什么
- **设计决策**: 确定的方案
- **边界**: 不做什么
- **约束**: 必须遵守的规则

### 3. 生成 design.md

创建 `.claude/design.md`，包含：

```markdown
# [功能名称] 设计文档

## 需求概述
[一段话描述要做什么]

## 功能范围
### 包含
- 功能点 1
- 功能点 2

### 不包含
- 排除项 1
- 排除项 2

## 技术设计

### 数据模型
[表结构 / 实体设计]

### API 设计
[接口列表和说明]

### 前端设计
[页面和组件]

## 约束条件
- 约束 1
- 约束 2
```

### 4. 拆分任务

使用脚本添加任务（JSON格式）：

```bash
python3 .claude/scripts/index.py task add '{
  "name": "任务名称",
  "what": "要做什么",
  "boundary": ["不做什么"],
  "constraints": ["约束"],
  "done_when": ["完成标准"],
  "depends_on": []
}'
```

每个任务必须填写四要素：
- **what**: 精确描述要做什么
- **boundary**: 不做什么
- **constraints**: 约束条件
- **done_when**: 完成标准

**任务粒度**: 一个 task = 2-4 小时工作量

**任务顺序**: 考虑依赖关系，设置 depends_on

### 5. 确认任务列表

```bash
python3 .claude/scripts/index.py task list
```

### 6. 输出结果

```
## 规划完成

### 设计文档
- .claude/design.md

### 任务列表
[显示所有任务]

### 依赖关系
[显示任务依赖图]

### 下一步
使用 `/run` 开始自动执行任务
```

## 任务拆分示例

```
功能: Actor 管理

T001: Actor 数据库表和实体
  what: 创建 actor 表，实现 Entity 和 Mapper
  boundary: 不包含业务逻辑
  done_when: 表创建成功，Entity 可以 CRUD

T002: Actor CRUD API
  what: 实现 Controller 和 Service
  boundary: 只做基础 CRUD，不做复杂查询
  constraints: 返回格式遵循现有 API 规范
  done_when: API 可以正常调用
  depends_on: [T001]

T003: Actor 列表页面
  what: 前端列表页，展示所有 Actor
  boundary: 不做分页（后续任务）
  done_when: 页面能显示数据
  depends_on: [T002]
```

## 注意事项

- 任务描述要具体，不要模糊
- 每个任务的 done_when 必须可验证
- 合理设置依赖，避免循环依赖
- 不要把一个大功能塞进一个任务
