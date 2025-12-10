# 执行任务

自动执行所有 active 任务。

**使用时机**: `/plan` 完成后，开始开发。

## 执行步骤

### 1. 读取设计文档

```bash
# 读取当前设计
cat .claude/design.md
```

理解整体设计，为后续任务提供背景。

### 2. 获取下一个任务

```bash
python3 .claude/scripts/index.py task next
```

这会显示：
- 任务详情（what, boundary, constraints, done_when）
- 依赖任务的 output（如有）

### 3. 开始任务

```bash
python3 .claude/scripts/index.py task start <task_id>
```

### 4. 执行开发

根据任务的四要素进行开发：
- **what**: 做什么
- **boundary**: 不做什么（避免过度设计）
- **constraints**: 遵守什么
- **done_when**: 完成标准

**开发时**：
- 按需调用 Skills（backend-dev, frontend-dev 等）
- 参考 design.md 了解详细设计
- 参考依赖任务的 output 了解已完成的内容

### 5. 完成任务

```bash
python3 .claude/scripts/index.py task done <task_id>
```

**必须填写 output**：
- summary: 做了什么
- models: 数据结构变更（如有）
- apis: 接口变更（如有）
- utils: 可复用方法（如有）

### 6. 询问是否继续

使用 AskUserQuestion 询问：

```
任务 <task_id> 已完成。

是否继续执行下一个任务？
- 继续: 执行下一个任务
- 暂停: 保存进度，稍后继续
```

### 7. 循环执行

如果选择继续，重复步骤 2-6，直到所有任务完成。

### 8. 全部完成

当没有更多 active 任务时：

```
## 所有任务已完成

### 完成统计
- 总任务数: N
- 已完成: N

### 产出摘要
[显示所有任务的 output.summary]

### 下一步
- 使用 `/test` 运行测试
- 手动验证功能
```

## 任务执行示例

```
=== T001: Actor 数据库表和实体 ===

What: 创建 actor 表，实现 Entity 和 Mapper
Boundary: 不包含业务逻辑
Constraints: 无
Done when: 表创建成功，Entity 可以 CRUD

[执行开发...]

任务完成，填写 output:
- summary: 创建了 actor 表和 ActorEntity
- models: actor(id, name, description, created_at)
- apis: (无)
- utils: (无)

✓ T001 已完成并归档

---

=== T002: Actor CRUD API ===

依赖任务产出:
[T001] 创建了 actor 表和 ActorEntity
       models: actor(id, name, description, created_at)

What: 实现 Controller 和 Service
...
```

## 注意事项

- 每完成一个任务必须填写 output，这是上下文传递的关键
- 遇到问题可以暂停，修复后继续
- 如果需要调整设计，先更新 design.md
- 如果需要新增任务，使用 `task add` 添加
