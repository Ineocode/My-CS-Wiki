# 🗂️ CS 术语与命名字典

## 1. 精确名词命名法 (Precision Naming)

CS 领域要求绝对的精确检索。卡片命名采用 **"英文前缀 + 中文技术标题"** 的混合命名法，既保证分类清晰，又便于中文语境下的快速识别。

### 命名格式
```
[英文前缀]-[中文技术标题].md
```

**示例：**
- `concept-事件循环.md` (而非 `concept-Event_Loop.md`)
- `algo-快速排序.md` (而非 `algo-QuickSort.md`)
- `syntax-JS异步Promise.md` (而非 `syntax-JS_Promise.md`)
- `tool-Git变基操作.md` (而非 `tool-Git_Rebase.md`)

---

## 2. 领域前缀字典

根据技术知识的类型，选用以下前缀存入 `02_Wiki/00_Cards/`：

| 前缀 | 用途 | 中文标题示例 |
|------|------|-------------|
| `concept-` | 计算机基础理论、架构模式、网络协议、核心概念 | `concept-内存布局模型.md`, `concept-CAP定理.md`, `concept-十六进制.md` |
| `algo-` | 算法与数据结构 | `algo-二分查找.md`, `algo-B树.md`, `algo-快速排序.md` |
| `syntax-` | 特定编程语言的语法特性或 API | `syntax-C指针.md`, `syntax-Python装饰器.md`, `syntax-JS异步Promise.md` |
| `tool-` | 开发者工具、CLI 命令、配置文件 | `tool-Docker容器编排.md`, `tool-Git变基操作.md`, `tool-Valgrind内存检测.md` |
| `bug-` | 经典报错解析与排查思路 | `bug-CORS策略错误.md`, `bug-段错误排查.md` |

---

## 3. 中文技术标题命名规范

1. **简洁专业**：使用中文技术术语，避免口语化
   - ✅ `syntax-C指针算术.md`
   - ❌ `syntax-C语言里面那个指针加减的东西.md`

2. **包含关键上下文**：对于语言/框架特定的概念，在标题中注明
   - ✅ `syntax-JS闭包.md`, `syntax-Python列表推导式.md`
   - ❌ `syntax-闭包.md` (过于笼统)

3. **避免特殊字符**：中文标题中不使用 `/\:*?"<>|` 等特殊字符

4. **驼峰或连字符**：多词技术术语使用驼峰或连字符连接
   - ✅ `syntax-React副作用Hook.md`, `concept-事件驱动架构.md`
