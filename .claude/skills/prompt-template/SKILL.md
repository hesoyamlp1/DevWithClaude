---
name: prompt-template
description: 提示词模板管理技能。在创建、修改、优化 LLM 提示词时自动调用。所有提示词必须通过模板管理，禁止硬编码。
allowed-tools: Read, Grep, Glob, Edit, Write
---

# 提示词模板管理技能

## 核心原则

**所有提示词必须通过模板管理，禁止硬编码在代码中！**

## 模板引擎使用

### 创建模板引擎

```java
// 使用默认配置
TemplateEngine engine = DefaultTemplateEngine.createDefault();

// 或注册自定义函数
TemplateFunctionRegistry registry = new TemplateFunctionRegistry();
registry.register("custom", new CustomFunction());
TemplateEngine engine = DefaultTemplateEngine.create(registry);
```

## 模板语法

### 1. 变量替换

```
你好, {{name}}!
玩家 HP: {{player.hp}}/{{player.maxHp}}
```

### 2. 条件判断

```
{{#if player.hp > 50}}
    玩家状态良好
{{else}}
    玩家需要治疗
{{/if}}
```

### 3. 列表渲染

```
物品列表:
{{#formatList items separator=", " prefix="- "}}
```

### 4. 消息分隔符

使用 `[SYSTEM]`、`[USER]`、`[ASSISTANT]` 标记消息角色:

```
[SYSTEM]
你是 {{npc.name}},{{npc.description}}

[USER]
玩家对你说: {{user_input}}
```

## 创建提示词模板

### 定义模板

```java
PromptTemplate template = PromptTemplate.simple("game_npc_chat", """
    [SYSTEM]
    你是 {{npc.name}}，一个 {{npc.role}}。

    ## 性格特点
    {{npc.personality}}

    ## 当前场景
    {{scene.description}}

    ## 对话规则
    - 保持角色一致性
    - 回复控制在 100 字以内
    - 使用符合角色身份的语气

    [USER]
    玩家说: {{user_input}}
    """);
```

### 渲染为消息列表

```java
Map<String, Object> vars = Map.of(
    "npc", npc,
    "scene", scene,
    "user_input", userInput
);

List<Message> messages = engine.renderToMessages(template, vars);
```

## 模板验证

```java
ValidationResult result = engine.validate(templateContent);

if (!result.valid()) {
    log.error("模板错误: {}", result.errors());
}

if (!result.warnings().isEmpty()) {
    log.warn("模板警告: {}", result.warnings());
}
```

## 模板存储位置

建议将模板存储在以下位置之一:

1. **数据库** - 支持动态修改
2. **配置文件** - `src/main/resources/prompts/`
3. **常量类** - 简单场景

## 模板设计最佳实践

### 1. 结构清晰

```
[SYSTEM]
## 角色设定
...

## 能力边界
...

## 输出格式
...

[USER]
用户输入
```

### 2. 使用变量而非硬编码

```
// 正确
你是 {{character.name}}

// 错误
你是 酒馆老板
```

### 3. 提供清晰的指令

```
## 回复规则
1. 回复长度不超过 {{max_length}} 字
2. 使用 {{language}} 回复
3. 保持 {{tone}} 语气
```

## 辅助脚本

脚本位置：`.claude/skills/prompt-template/scripts/prompt_helper.py`

**模板存储在数据库 `prompt_template` 表中**

```bash
# 列出所有提示词模板 (从数据库读取)
python3 .claude/skills/prompt-template/scripts/prompt_helper.py list

# 显示模板详情和内容
python3 .claude/skills/prompt-template/scripts/prompt_helper.py show system.loop

# 显示模板变量
python3 .claude/skills/prompt-template/scripts/prompt_helper.py variables tool.speak

# 验证模板语法 (检查变量、条件、循环是否正确)
python3 .claude/skills/prompt-template/scripts/prompt_helper.py validate system.loop

# 列出所有模板分类
python3 .claude/skills/prompt-template/scripts/prompt_helper.py categories

# 查找代码中硬编码的提示词
python3 .claude/skills/prompt-template/scripts/prompt_helper.py find-hardcoded
```

## 禁止事项

- **禁止在 Java 代码中硬编码提示词**
- 禁止直接拼接字符串构建提示词
- 禁止在模板中包含敏感信息

## 示例: 完整的 NPC 对话模板

```java
PromptTemplate npcChatTemplate = PromptTemplate.simple("npc_chat", """
    [SYSTEM]
    # 角色信息
    你是 {{npc.name}}，{{npc.description}}

    ## 性格特点
    {{npc.personality}}

    ## 知识范围
    {{#formatList npc.knowledge separator="\n" prefix="- "}}

    ## 当前状态
    - 位置: {{npc.location}}
    - 情绪: {{npc.mood}}
    - 对玩家的态度: {{npc.attitudeToPlayer}}

    ## 对话规则
    1. 始终保持角色一致性
    2. 只回答你知识范围内的问题
    3. 对于不知道的事情，用符合角色的方式表示不知道
    4. 回复控制在 {{maxResponseLength}} 字以内

    {{#if npc.hasSecret}}
    ## 秘密 (不要直接透露)
    {{npc.secret}}
    {{/if}}

    [USER]
    {{userInput}}
    """);
```
