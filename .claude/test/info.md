# 测试配置信息

## 项目信息

- **项目名称**: WebRPGWithLLM
- **后端模块**: `core/`
- **测试目录**: `core/src/test/java/`
- **数据库**: SQLite (`data/webrpg.db`)

## 后端测试环境

### Maven 命令

```bash
# 运行所有测试
cd core && mvn test

# 运行指定测试类
cd core && mvn test -Dtest="TestClassName"

# 运行多个测试类
cd core && mvn test -Dtest="Test1,Test2,Test3"

# 运行指定包下的测试
cd core && mvn test -Dtest="work.toddout.core.game.**"
```

### 测试框架

- **JUnit 5**: 测试框架
- **Mockito**: Mock 框架
- **AssertJ**: 断言库
- **Spring Boot Test**: Spring 测试支持

### 包结构

```
core/src/test/java/work/toddout/core/
├── {module}/
│   ├── service/
│   │   └── XxxServiceTest.java
│   └── controller/
│       └── XxxControllerTest.java
└── CoreApplicationTests.java
```

## 测试规范

### 命名规范

- 测试类: `{SourceClass}Test.java`
- 测试方法: `test{Method}_{scenario}` 或 `should{Expected}_when{Condition}`

### 测试结构

```java
@Test
@DisplayName("中文描述")
void testMethod_scenario() {
    // Given - 准备数据

    // When - 执行操作

    // Then - 验证结果
}
```

### Mock 使用

- Service 测试: Mock Mapper/Repository
- Controller 测试: Mock Service

## 端口信息

- **后端服务**: 8080
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **API 基础路径**: `/api/`

## 注意事项

1. 单元测试使用 Mock，不连接真实数据库
2. 测试方法的 `@DisplayName` 使用中文描述
3. 每个 Service 方法至少测试：正常流程、异常流程、边界条件
4. Optional 返回值要测试 present 和 empty 两种情况
