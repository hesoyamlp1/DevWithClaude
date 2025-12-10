---
name: frontend-dev
description: 前端 React + TypeScript 开发技能。在进行页面组件、UI 开发、状态管理等前端任务时自动调用。遵循 UI 和逻辑分离原则。
allowed-tools: Read, Grep, Glob, Edit, Write
---

# 前端开发技能

## 开发前必读

**在进行任何前端开发前，必须先阅读前端开发指南:**
- 文件路径: `/Users/linsuki/Passion/WebRPGWithLLM/rpg-frontend/DEVELOPMENT_GUIDE.md`

## 技术栈

- React + TypeScript
- Mantine UI (组件库)
- Zustand (状态管理)
- React Router (路由)
- Axios (HTTP 请求)
- React Hook Form + Zod (表单验证)

## 核心原则

### 1. UI 和逻辑分离
- Mantine 组件负责 UI
- 业务逻辑在 Hooks 或 Store 中

### 2. 主题系统
- 所有视觉配置在 `theme.ts`
- 外观修改不触及组件代码

### 3. 状态管理
- 全局状态用 Zustand
- 组件内状态用 `useState`

## 目录结构

```
src/
├── api/         # API 调用和 SSE (稳定)
├── store/       # Zustand 全局状态 (稳定)
├── types/       # TypeScript 类型 (稳定)
├── pages/       # 页面组件 (易变)
├── components/  # 可复用组件 (易变)
├── theme.ts     # Mantine 主题配置
└── App.tsx      # 路由配置
```

## 样式规范

### 正确做法
```typescript
<Box p="md" bg="gray.0">
    <Text c="blue" fw={500}>文本</Text>
    <Button variant="outline" size="sm">按钮</Button>
</Box>
```

### 禁止做法
```typescript
// 不要写内联样式
<div style={{ padding: '16px' }}>

// 不要写 CSS 文件
import './MyComponent.css';
```

## 组件开发模板

```typescript
// pages/SomePage.tsx
import { Stack, Title, Button } from '@mantine/core';
import { useState } from 'react';
import { useAppStore } from '@/store';
import { client } from '@/api/client';

export default function SomePage() {
    // 1. 全局状态
    const { sessionId, addEvent } = useAppStore();

    // 2. 组件内部状态
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // 3. 事件处理
    const handleSubmit = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const res = await client.post('/api/endpoint', { data });
            addEvent(res.data);
        } catch (err) {
            setError((err as Error).message);
        } finally {
            setIsLoading(false);
        }
    };

    // 4. 渲染
    return (
        <Stack>
            <Title order={3}>页面标题</Title>
            <Button onClick={handleSubmit} loading={isLoading}>
                提交
            </Button>
        </Stack>
    );
}
```

## 状态管理 (Zustand)

```typescript
// store/index.ts
import { create } from 'zustand';

interface AppState {
    sessionId: string | null;
    setSessionId: (id: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
    sessionId: null,
    setSessionId: (id) => set({ sessionId: id }),
}));
```

## API 调用

```typescript
import { client } from '@/api/client';

// 使用 client 实例，不直接用 axios
const res = await client.get<ResponseType>('/endpoint');
```

## 辅助脚本

脚本位置：`.claude/skills/frontend-dev/scripts/frontend_helper.py`

```bash
# 检查组件规范 (内联样式、CSS导入、状态管理等)
python3 .claude/skills/frontend-dev/scripts/frontend_helper.py check-component SessionChat.tsx

# 查找内联样式
python3 .claude/skills/frontend-dev/scripts/frontend_helper.py find-inline-styles

# 查找 CSS 文件导入
python3 .claude/skills/frontend-dev/scripts/frontend_helper.py find-css-imports

# 列出所有页面组件
python3 .claude/skills/frontend-dev/scripts/frontend_helper.py list-pages

# 列出所有可复用组件
python3 .claude/skills/frontend-dev/scripts/frontend_helper.py list-components

# 显示前端目录结构
python3 .claude/skills/frontend-dev/scripts/frontend_helper.py show-structure

# 检查状态管理使用情况
python3 .claude/skills/frontend-dev/scripts/frontend_helper.py check-store-usage
```

## 禁止事项

- 不要在组件中直接写复杂逻辑
- 不要写 CSS 文件或内联样式
- 可复用组件不要直接访问全局状态 (通过 props 传递)
- 不要主动编写文档 - 除非用户明确要求
