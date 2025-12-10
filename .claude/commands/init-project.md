# 初始化项目

检测技术栈，填充 project.json 和 skills。

**使用时机**: 新项目首次使用此脚手架时。

## 执行流程

```
1. 并行探索 → 2. 汇总结果 → 3. 用户确认 → 4. 填充文件
```

---

## 阶段 1：并行探索

启动 3 个 Explore subagent 并行探索：

### 探索后端

```
Task(subagent_type="Explore", prompt="探索项目的后端结构，找出：
1. 编程语言和版本（查看 pom.xml/build.gradle/package.json/go.mod 等）
2. 框架（Spring Boot/Express/FastAPI 等）
3. 构建工具（Maven/Gradle/npm 等）
4. 目录结构（Controller/Service/Repository 在哪里）
5. DTO 模式（如何定义请求/响应对象，找一个例子）
6. 异常处理（自定义异常类，全局异常处理）
7. 日志方式（用什么库，日志风格）

返回格式：
- stack: 语言/框架/构建工具
- paths.backend_root: 后端代码根目录
- patterns.dto_style: DTO 风格描述
- patterns.exception_class: 异常类名
- patterns.log_style: 日志方式
- structure: 目录结构描述")
```

### 探索前端

```
Task(subagent_type="Explore", prompt="探索项目的前端结构，找出：
1. 框架（React/Vue/Angular 等）
2. 语言（TypeScript/JavaScript）
3. 构建工具（Vite/Webpack/CRA 等）
4. 目录结构（pages/components/hooks 在哪里）
5. 组件库（Mantine/Ant Design/MUI 等）
6. 状态管理（Zustand/Redux/Pinia 等）
7. 样式方案（CSS Modules/Tailwind/Styled Components 等）
8. API 调用方式（axios/fetch，是否有封装）

返回格式：
- stack: 语言/框架/构建工具
- paths.frontend_root: 前端代码根目录
- patterns.component_library: 组件库
- patterns.state_management: 状态管理
- patterns.style_solution: 样式方案
- patterns.api_client: API 调用方式
- structure: 目录结构描述")
```

### 探索数据库

```
Task(subagent_type="Explore", prompt="探索项目的数据库结构，找出：
1. 数据库类型（SQLite/MySQL/PostgreSQL/MongoDB 等）
2. 数据库位置/连接配置
3. 迁移工具（Flyway/Liquibase/Prisma/无）
4. 迁移脚本位置
5. 迁移脚本命名规则（看现有脚本）
6. 现有的表结构（列出主要表名）

返回格式：
- stack: 数据库类型/迁移工具
- paths.database: 数据库文件位置（如果是文件数据库）
- paths.migration_dir: 迁移脚本目录
- migration_naming: 命名规则描述
- existing_tables: 现有表列表")
```

---

## 阶段 2：汇总结果

将三个探索结果汇总为 project.json 格式：

```json
{
  "project": { "name": "项目名", "type": "web-app" },
  "stack": {
    "backend": "探索结果",
    "frontend": "探索结果",
    "database": "探索结果"
  },
  "paths": {
    "backend_root": "探索结果",
    "frontend_root": "探索结果",
    "migration_dir": "探索结果",
    "database": "探索结果"
  },
  "patterns": {
    "dto_style": "探索结果",
    "exception_class": "探索结果",
    "state_management": "探索结果",
    "component_library": "探索结果"
  }
}
```

---

## 阶段 3：用户确认

使用 AskUserQuestion 展示探索结果，让用户确认或修改：

```
AskUserQuestion:
  question: "探索结果如下，是否需要修改？"
  options:
    - "确认无误，继续填充"
    - "需要修改"
```

如果用户选择修改，询问具体要修改哪些内容。

---

## 阶段 4：填充文件

### 4.1 填充 project.json

```bash
project init '<确认后的 JSON>'
```

### 4.2 填充 Skills

根据探索结果，替换各 skill 的 `<!-- BEGIN:xxx -->` 区域：

**backend-dev/SKILL.md:**
```markdown
<!-- BEGIN:STACK -->
**技术栈:** Java 17 / Spring Boot 3.x / Maven
<!-- END:STACK -->

<!-- BEGIN:STRUCTURE -->
**目录结构:**

- Controller: src/main/java/.../controller/
- Service: src/main/java/.../service/
- Repository: src/main/java/.../repository/
- Entity: src/main/java/.../entity/
- DTO: src/main/java/.../dto/
<!-- END:STRUCTURE -->

<!-- BEGIN:PATTERNS -->
**代码模式:**

- DTO 模式: 使用 Java record 定义请求/响应对象
- 异常处理: 使用 BusinessException，全局 @ExceptionHandler 处理
- 日志方式: Slf4j + @Slf4j 注解
<!-- END:PATTERNS -->
```

**frontend-dev/SKILL.md:** 类似填充

**database-migration/SKILL.md:** 类似填充

---

## 阶段 5：输出结果

```
## 项目初始化完成

### 技术栈
- 后端: [stack.backend]
- 前端: [stack.frontend]
- 数据库: [stack.database]

### 已更新文件
- .claude/project.json
- .claude/skills/backend-dev/SKILL.md
- .claude/skills/frontend-dev/SKILL.md
- .claude/skills/database-migration/SKILL.md

### 下一步
1. 检查生成的文件，按需调整
2. 使用 /plan 开始需求讨论
```

---

## 注意事项

- 如果某部分探索不到（如项目没有前端），对应 skill 保持框架状态
- 探索结果仅供参考，用户确认后才填充
- 可以多次运行，会覆盖之前的内容
