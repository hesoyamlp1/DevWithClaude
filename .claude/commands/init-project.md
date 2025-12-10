# 初始化项目

检测技术栈，填充 skills，配置项目环境。

**使用时机**: 新项目首次使用此脚手架时。

## 执行步骤

### 1. 检测技术栈

```bash
# 后端
ls pom.xml 2>/dev/null && echo "Java + Maven"
ls build.gradle 2>/dev/null && echo "Java + Gradle"
ls package.json 2>/dev/null && grep -l "express\|nestjs\|fastify" package.json && echo "Node.js"
ls requirements.txt pyproject.toml 2>/dev/null && echo "Python"
ls go.mod 2>/dev/null && echo "Go"

# 前端
ls package.json 2>/dev/null && grep -l "react" package.json && echo "React"
ls package.json 2>/dev/null && grep -l "vue" package.json && echo "Vue"

# 数据库
grep -r "sqlite\|mysql\|postgresql\|mongodb" . --include="*.properties" --include="*.yml" --include="*.yaml" --include="*.json" 2>/dev/null | head -5
```

### 2. 读取配置文件

根据检测结果，读取相关配置：
- Java: `pom.xml` - 依赖和版本
- Node: `package.json` - 依赖
- Python: `requirements.txt` / `pyproject.toml`
- 数据库: `application.properties` / `application.yml`

### 3. 探索目录结构

```bash
# 目录结构
find . -type d -name "src" -o -name "controller" -o -name "service" -o -name "components" -o -name "pages" | head -20
```

### 4. 填充 Skills

根据检测结果，更新对应的 skill 文件：

#### backend-dev/SKILL.md
```markdown
## 技术栈
- **语言**: [检测到的语言和版本]
- **框架**: [检测到的框架]
- **构建**: [构建命令]

## 目录结构
- Controller: [路径]
- Service: [路径]
- Repository: [路径]

## 编码规范
[从现有代码推断]
```

#### frontend-dev/SKILL.md
```markdown
## 技术栈
- **框架**: [React/Vue/Angular]
- **语言**: [TypeScript/JavaScript]
- **UI库**: [检测到的 UI 库]

## 目录结构
- Pages: [路径]
- Components: [路径]
- Hooks: [路径]
```

#### database-migration/SKILL.md
```markdown
## 技术栈
- **数据库**: [SQLite/MySQL/PostgreSQL]
- **迁移工具**: [Flyway/Liquibase/其他]

## 迁移目录
[迁移脚本路径]
```

### 5. 更新 CLAUDE.md

在项目根目录的 CLAUDE.md 中添加项目特定信息：

```markdown
## 项目信息

- **名称**: [项目名]
- **技术栈**: [后端] + [前端] + [数据库]
- **构建**: [构建命令]
- **运行**: [运行命令]
```

### 6. 初始化任务文件

```bash
# 创建空的 tasks.json
echo '{"active": [], "archived": []}' > .claude/tasks.json

# 创建 designs 目录
mkdir -p .claude/designs
```

### 7. 输出结果

```
## 项目初始化完成

### 检测到的技术栈
- **后端**: [语言 + 框架]
- **前端**: [框架]
- **数据库**: [类型]

### 已更新的 Skills
- .claude/skills/backend-dev/SKILL.md
- .claude/skills/frontend-dev/SKILL.md
- .claude/skills/database-migration/SKILL.md

### 下一步
1. 检查生成的 skill 文件，按需调整
2. 开始需求讨论，使用 `/plan` 生成设计文档和任务
```

## 注意事项

- 如果检测不到某个技术栈，对应的 skill 保持模板状态
- 可以多次运行，会覆盖之前的内容
- 建议在运行后手动检查并补充 skill 内容
