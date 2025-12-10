# 设计文档

## Meta
- **项目**: 项目名称
- **版本**: 1.0
- **状态**: draft / approved
- **创建时间**: YYYY-MM-DD
- **最后更新**: YYYY-MM-DD

---

# 第一部分：需求

## 1.1 背景与目标

### 背景
<!-- 为什么要做这个功能？解决什么问题？当前痛点是什么？ -->

### 目标
<!-- 这个功能要达成什么目标？成功标准是什么？ -->

### 范围
<!--
包含什么（In Scope）:
- 功能1
- 功能2

不包含什么（Out of Scope）:
- 暂不实现的功能
-->

## 1.2 用户故事

<!--
格式：作为 [角色]，我想要 [功能]，以便 [价值]

示例：
- US-01: 作为游戏玩家，我想要创建自定义 NPC，以便丰富游戏世界
- US-02: 作为游戏玩家，我想要编辑 NPC 的对话模板，以便定制 NPC 的性格
-->

| ID | 用户故事 | 优先级 |
|----|----------|--------|
| US-01 | 作为...，我想要...，以便... | 高 |
| US-02 | 作为...，我想要...，以便... | 中 |

## 1.3 功能需求

### FR-01: 功能名称
- **描述**: 详细描述这个功能做什么
- **输入**: 用户提供什么
- **输出**: 系统返回什么
- **业务规则**:
  - 规则1
  - 规则2
- **验收标准**:
  - [ ] AC-1: 具体可验证的标准
  - [ ] AC-2: 具体可验证的标准

### FR-02: 功能名称
<!-- 同上格式 -->

## 1.4 交互流程

### 主流程：功能名称

```
用户操作                    系统响应
─────────────────────────────────────────
1. 用户点击"创建"按钮    →  显示创建表单
2. 用户填写表单并提交    →  验证数据
3.                       →  保存到数据库
4.                       →  返回成功提示，跳转到列表页
```

### 异常流程

| 场景 | 触发条件 | 系统响应 |
|------|----------|----------|
| 验证失败 | 必填字段为空 | 显示错误提示，高亮错误字段 |
| 保存失败 | 数据库错误 | 显示"保存失败，请重试" |

## 1.5 非功能需求

- **性能**: 列表加载 < 1秒
- **安全**: 需要登录才能访问
- **兼容性**: 支持 Chrome、Firefox、Safari

---

# 第二部分：技术设计

## 2.1 架构设计

### 整体架构

```
┌──────────────────────────────────────────────────────────┐
│                        前端 (React)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  列表页面    │  │  创建页面   │  │  编辑页面    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└──────────────────────────────────────────────────────────┘
                           │ HTTP
                           ▼
┌──────────────────────────────────────────────────────────┐
│                       后端 (Spring Boot)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ Controller  │→ │  Service    │→ │  Mapper     │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└──────────────────────────────────────────────────────────┘
                           │ SQL
                           ▼
┌──────────────────────────────────────────────────────────┐
│                      数据库 (SQLite)                      │
│  ┌─────────────┐  ┌─────────────┐                        │
│  │  表1        │  │  表2        │                        │
│  └─────────────┘  └─────────────┘                        │
└──────────────────────────────────────────────────────────┘
```

### 模块划分

| 模块 | 职责 | 后端路径 | 前端路径 |
|------|------|----------|----------|
| xxx | 描述 | `core/.../xxx/` | `rpg-frontend/src/features/xxx/` |

## 2.2 数据模型

### 表：table_name

**用途**: 描述这个表存储什么数据

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| name | TEXT | NOT NULL | 名称 |
| description | TEXT | | 描述，可为空 |
| status | TEXT | NOT NULL, DEFAULT 'active' | 状态：active/inactive |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | | 更新时间 |

**索引**:
- `idx_table_name_status` ON (status)

**外键**:
- `fk_table_other` REFERENCES other_table(id)

### 实体关系图

```
┌─────────────┐       ┌─────────────┐
│   Table A   │ 1───N │   Table B   │
│─────────────│       │─────────────│
│ id (PK)     │       │ id (PK)     │
│ name        │       │ a_id (FK)   │
└─────────────┘       └─────────────┘
```

## 2.3 API 设计

### POST /api/xxx

**描述**: 创建新的 xxx

**请求体**:
```json
{
  "name": "string, 必填, 1-100字符",
  "description": "string, 可选",
  "config": {
    "key1": "value1"
  }
}
```

**响应 - 成功 (200)**:
```json
{
  "id": 1,
  "name": "xxx",
  "description": null,
  "config": {"key1": "value1"},
  "createdAt": "2024-01-15T10:00:00Z"
}
```

**响应 - 验证失败 (400)**:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "名称不能为空",
  "details": [
    {"field": "name", "message": "不能为空"}
  ]
}
```

### GET /api/xxx

**描述**: 获取 xxx 列表

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页数量，默认 20 |
| status | string | 否 | 过滤状态 |

**响应 (200)**:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20
}
```

### GET /api/xxx/{id}

**描述**: 获取单个 xxx

**响应 - 成功 (200)**: 同 POST 响应

**响应 - 未找到 (404)**:
```json
{
  "error": "NOT_FOUND",
  "message": "xxx 不存在"
}
```

### PUT /api/xxx/{id}

**描述**: 更新 xxx

**请求体**: 同 POST

**响应**: 同 GET

### DELETE /api/xxx/{id}

**描述**: 删除 xxx

**响应 (204)**: 无内容

## 2.4 前端设计

### 页面结构

```
/xxx                    # 列表页
/xxx/new                # 创建页
/xxx/:id                # 详情页
/xxx/:id/edit           # 编辑页
```

### 组件设计

#### 页面组件

| 组件 | 路径 | 职责 |
|------|------|------|
| XxxListPage | `pages/XxxListPage.tsx` | 列表页面，展示数据表格 |
| XxxCreatePage | `pages/XxxCreatePage.tsx` | 创建页面，表单提交 |
| XxxDetailPage | `pages/XxxDetailPage.tsx` | 详情页面，只读展示 |
| XxxEditPage | `pages/XxxEditPage.tsx` | 编辑页面，表单修改 |

#### UI 组件

| 组件 | 路径 | 职责 |
|------|------|------|
| XxxForm | `components/XxxForm.tsx` | 表单组件，创建/编辑共用 |
| XxxCard | `components/XxxCard.tsx` | 卡片组件，列表项展示 |

#### Hooks

| Hook | 路径 | 职责 |
|------|------|------|
| useXxxList | `hooks/useXxxList.ts` | 获取列表数据 |
| useXxxDetail | `hooks/useXxxDetail.ts` | 获取详情数据 |
| useXxxMutations | `hooks/useXxxMutations.ts` | 创建/更新/删除操作 |

### 状态管理

**全局状态 (Zustand)**: 无 / 描述需要的全局状态

**组件状态**: 表单状态、加载状态、错误状态

### UI 交互

#### 列表页
- 表格展示数据
- 支持分页
- 点击行跳转详情
- 右上角"新建"按钮

#### 表单页
- 使用 Mantine 表单组件
- 实时验证
- 提交后跳转列表

## 2.5 错误处理

| 场景 | 前端处理 | 后端处理 |
|------|----------|----------|
| 网络错误 | 显示"网络错误，请重试" | - |
| 验证失败 | 显示字段级错误 | 返回 400 + 错误详情 |
| 未找到 | 显示 404 页面 | 返回 404 |
| 服务器错误 | 显示"服务器错误" | 返回 500 + 日志记录 |

---

# 第三部分：实现指南

## 3.1 代码位置

### 后端

```
core/src/main/java/work/toddout/core/{module}/
├── controller/
│   └── XxxController.java
├── service/
│   ├── XxxService.java          # 接口
│   └── impl/
│       └── XxxServiceImpl.java  # 实现
├── repository/
│   └── XxxMapper.java           # MyBatis Mapper
├── entity/
│   └── Xxx.java                 # 数据库实体
└── dto/
    ├── XxxCreateDTO.java        # 创建请求
    ├── XxxUpdateDTO.java        # 更新请求
    └── XxxVO.java               # 响应对象
```

### 前端

```
rpg-frontend/src/features/{module}/
├── pages/
│   ├── XxxListPage.tsx
│   ├── XxxCreatePage.tsx
│   ├── XxxDetailPage.tsx
│   └── XxxEditPage.tsx
├── components/
│   ├── XxxForm.tsx
│   └── XxxCard.tsx
├── hooks/
│   ├── useXxxList.ts
│   ├── useXxxDetail.ts
│   └── useXxxMutations.ts
├── types/
│   └── index.ts
└── index.ts                     # 导出
```

## 3.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 数据库表 | snake_case | `actor_profile` |
| Java 类 | PascalCase | `ActorProfileService` |
| Java 方法 | camelCase | `findById` |
| React 组件 | PascalCase | `ProfileListPage` |
| React hook | camelCase, use前缀 | `useProfileList` |
| API 路径 | kebab-case | `/api/actor-profiles` |

## 3.3 依赖说明

### 新增依赖
<!-- 如果需要新增依赖，在此说明 -->
- 无

### 依赖现有模块
<!-- 列出依赖的现有模块 -->
- 无

---

# 第四部分：变更记录

<!--
迭代调整时在此记录。

### [C001] YYYY-MM-DD - 变更标题

**类型**: 新增 / 修改 / 删除 / 重构

**背景**: 为什么要做这个变更

**变更内容**:
- 原方案：...
- 新方案：...

**影响范围**:
- 数据模型：涉及哪些表/字段
- API：涉及哪些接口
- 前端：涉及哪些组件/页面

**关联任务**: Cxxx
-->
