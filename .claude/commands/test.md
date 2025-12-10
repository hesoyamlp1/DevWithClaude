# 运行单元测试

运行后端单元测试，自动编写测试（如需要）并生成测试报告。

**使用时机**: 开发完成后，验证代码质量。

## 执行步骤

### 1. 检查设计文档

```bash
# 确认有设计文档
ls .claude/design.md
```

如果没有设计文档，提示用户先使用 `/plan` 创建。

### 2. 调用 Tester Agent

使用 Task 工具调用 tester agent：

```
Task(subagent_type="tester", prompt="
为当前项目编写和运行单元测试。

工作流程：
1. 读取 .claude/design.md 了解测试范围
2. 读取 .claude/tasks.json 的 archived 任务，了解已完成的功能
3. 检查 .claude/test/test_list.md 是否存在：
   - 不存在：分析源代码，编写单元测试，生成 test_list.md
   - 已存在：跳过编写步骤
4. 运行所有相关单元测试
5. 生成测试报告 .claude/test/test_report_{n}.md

注意：
- 只编写后端单元测试
- 不要修改任何源代码
- 使用 Mock 进行单元测试，不要连接真实数据库
")
```

### 3. 汇报结果

```
## 测试完成

### 测试状态
- **总测试数**: X
- **通过**: X
- **失败**: X

### 测试报告
路径: .claude/test/test_report_{n}.md

### 下一步
- 如果全部通过：功能验证完成
- 如果有失败：添加修复任务，使用 `/run` 执行
```

## 注意事项

- tester agent 只写测试，不修改源代码
- 如果测试失败，通过添加新任务来修复，不要直接改代码
