---
name: backend-dev
description: 后端 Java 开发技能。在进行 Spring Boot、MyBatis、LLM SDK、工具定义等后端开发时自动调用。遵循 SOLID 原则、分层架构和项目约定。
allowed-tools: Read, Grep, Glob, Edit, Write
---

# 后端开发技能

## 开发前必读

**在进行任何后端开发前，必须先阅读 common 包开发指南:**
- 文件路径: `/Users/linsuki/Passion/WebRPGWithLLM/common/DEVELOPMENT_GUIDE.md`

## 模块上下文（重要！）

**工作前根据任务自动发现需要的上下文：**

1. 查看 `.claude/specs/modules/` 目录，每个子目录代表一个模块
2. 根据任务涉及的模块，读取对应的 `GUIDE.md`
3. 如果 GUIDE.md 的"依赖"列了其他模块，也要读那些模块的 GUIDE.md

### 模块协作规则

当你在模块 A 工作，需要调用模块 B：
1. **先读模块 B 的 GUIDE.md** - 了解接口和调用方式
2. **使用 B 模块提供的接口** - 不要自己重新实现
3. **遵循分层架构** - 能力层不依赖业务层

**示例**：任务涉及 NPC 对话
```
→ 读 modules/npc/GUIDE.md
→ 发现依赖 LLM 模块
→ 读 modules/llm/GUIDE.md
```

### GUIDE.md 约定格式

每个模块的 GUIDE.md 包含：
- **模块信息**: 状态、代码位置
- **依赖/被依赖**: 与其他模块的关系
- **核心接口**: 主要方法签名
- **调用示例**: 实际代码示例
- **注意事项**: 使用时的注意点

## 核心原则

### SOLID 原则
1. **单一职责(SRP)**: 一个类只做一件事
2. **开闭原则(OCP)**: 对扩展开放，对修改关闭，使用抽象而非 if-else
3. **里氏替换(LSP)**: 子类可替换父类
4. **接口隔离(ISP)**: 接口职责单一，不强迫实现不需要的方法
5. **依赖倒置(DIP)**: 依赖抽象，使用依赖注入，不要硬编码具体实现

### 分层架构
```
API (Controller) → Service → Repository → Database
```
- 上层依赖下层抽象
- 高内聚低耦合

### Service 层规范
- **查询单个对象必须返回 `Optional<T>`**，避免 NPE
- 使用工厂模式创建对象
- 使用策略模式封装算法变化

## LLM SDK 使用

### 创建 LLM 客户端
```java
// 使用工厂方法 (正确)
LLMClient client = LLMClientFactory.create(config);

// 不要直接 new 具体实现 (错误)
```

### 定义工具 (Tool Call)
```java
@LLMTool(
    name = "tool_name",
    description = "工具描述",
    category = "game"
)
public String myTool(
    @LLMParam(description = "参数描述", required = true)
    String param
) {
    return "结果";
}
```

### 提示词模板
```java
PromptTemplate template = PromptTemplate.simple("name", """
    [SYSTEM]
    系统提示

    [USER]
    用户输入: {{user_input}}
    """);

List<Message> messages = engine.renderToMessages(template, vars);
```

## 数据库规范

- **不要在 Java 代码中硬编码 SQL**
- 使用 MyBatis Wrapper 进行数据库操作
- 复杂查询放在 `src/main/resources/sql/` 目录
- 数据库地址: `data/webrpg.db` (SQLite)

## 日志规范

- **日志使用中文打印**
```java
log.info("玩家 {} 进入游戏", playerId);
log.error("工具执行失败: {}", e.getMessage());
```

## 辅助脚本

脚本位置：`.claude/skills/backend-dev/scripts/backend_helper.py`

```bash
# 检查 Service 类规范 (Optional 返回、依赖注入等)
python3 .claude/skills/backend-dev/scripts/backend_helper.py check-service PlayerService.java

# 查找硬编码 SQL
python3 .claude/skills/backend-dev/scripts/backend_helper.py find-hardcoded-sql

# 查找硬编码提示词
python3 .claude/skills/backend-dev/scripts/backend_helper.py find-hardcoded-prompt

# 列出所有 Service 类
python3 .claude/skills/backend-dev/scripts/backend_helper.py list-services

# 列出所有 Controller 类
python3 .claude/skills/backend-dev/scripts/backend_helper.py list-controllers

# 显示后端目录结构
python3 .claude/skills/backend-dev/scripts/backend_helper.py show-structure
```

## 禁止事项

- 不要硬编码提示词 - 使用提示词模板管理
- 不要主动编写文档 - 除非用户明确要求
- **不要主动编写或运行单元测试** - 测试由用户手动调用 `/test` 命令触发
