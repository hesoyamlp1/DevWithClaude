---
name: database-migration
description: 数据库迁移和 Flyway 版本管理技能。在创建数据库表、修改表结构、编写迁移脚本时自动调用。
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# 数据库迁移技能

## Flyway 版本控制

**所有数据库变更必须通过 Flyway 迁移脚本**

### 脚本位置

迁移脚本放在: `core/src/main/resources/db/migration/`

### 命名规则

```
V<VERSION>__<DESCRIPTION>.sql
```

示例:
- `V1__init_schema.sql`
- `V2__add_player_table.sql`
- `V3__add_session_status_column.sql`

### 版本号规则

- 版本号递增: V1, V2, V3...
- **永远不要修改已执行的脚本**
- 新增变更创建新版本文件

## 创建新迁移的步骤

1. **查看当前最新版本**
```bash
ls core/src/main/resources/db/migration/
```

2. **创建新的迁移文件**
```sql
-- V<下一版本号>__<描述>.sql
-- 例如: V4__add_inventory_table.sql

CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES player(id)
);

CREATE INDEX idx_inventory_player ON inventory(player_id);
```

## SQL 编写规范

### 表结构规范

```sql
CREATE TABLE table_name (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 业务字段
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- 外键
    FOREIGN KEY (parent_id) REFERENCES parent_table(id)
);

-- 索引
CREATE INDEX idx_table_name_field ON table_name(field);
```

### SQLite 注意事项

- 使用 `INTEGER PRIMARY KEY AUTOINCREMENT` 自增主键
- 使用 `TEXT` 而非 `VARCHAR`
- 使用 `DATETIME` 存储时间
- SQLite 不支持 `ALTER COLUMN`，需要重建表

## 数据库访问

### 数据库位置
```
data/webrpg.db
```

### 使用 sqlite3 工具访问
```bash
sqlite3 data/webrpg.db
```

### 常用查询
```sql
-- 查看所有表
.tables

-- 查看表结构
.schema table_name

-- 查看 Flyway 版本历史
SELECT * FROM flyway_schema_history;
```

## Java 代码规范

### 禁止在 Java 中硬编码 SQL

```java
// 错误 - 硬编码 SQL
String sql = "SELECT * FROM player WHERE id = ?";

// 正确 - 使用 MyBatis Wrapper
QueryWrapper<Player> wrapper = new QueryWrapper<>();
wrapper.eq("id", playerId);
Player player = playerMapper.selectOne(wrapper);
```

### 复杂查询使用 SQL 文件

放在 `src/main/resources/sql/` 目录:
- 命名规范: `模块名_操作.sql`
- 例如: `player_find_by_status.sql`

## 辅助脚本

脚本位置：`.claude/skills/database-migration/scripts/migration_helper.py`

```bash
# 查看当前 Flyway 版本和迁移历史
python3 .claude/skills/database-migration/scripts/migration_helper.py version

# 生成下一个迁移文件名
python3 .claude/skills/database-migration/scripts/migration_helper.py next-name add_user_table

# 列出所有迁移文件
python3 .claude/skills/database-migration/scripts/migration_helper.py list

# 查看表结构
python3 .claude/skills/database-migration/scripts/migration_helper.py schema player

# 列出所有表
python3 .claude/skills/database-migration/scripts/migration_helper.py tables

# 检查迁移文件规范
python3 .claude/skills/database-migration/scripts/migration_helper.py check
```

## 禁止事项

- **永远不要修改已执行的迁移脚本**
- 不要在 Java 代码中硬编码 SQL
- 不要直接操作生产数据库
