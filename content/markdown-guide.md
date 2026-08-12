---
title: Markdown 写作指南
slug: markdown-guide
summary: 如何用 Markdown 写博客
published: true
---

# Markdown 写作指南

本文介绍如何在本博客中使用 Markdown 写作。

## 基本语法

### 标题

使用 `#` 号标记标题，一个 `#` 是一级标题，两个 `##` 是二级标题。

### 强调

- **粗体**：`**粗体**`
- *斜体*：`*斜体*`
- ~~删除线~~：`~~删除线~~`

### 列表

1. 有序列表项 1
2. 有序列表项 2
3. 有序列表项 3

- 无序列表项
- 无序列表项
- 无序列表项

### 链接

- 标准链接：[回到首页](/)
- 文章链接：[Hello World](/article/hello-world)
- Wiki 链接：[[hello-world]]

### 代码

行内代码：`print("hello")`

代码块：

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
console.log(greet("World"));
```

### 表格

| 语法 | 示例 |
|------|------|
| 标题 | `# H1` |
| 粗体 | `**bold**` |
| 链接 | `[text](url)` |

### 引用

> 这是一段引用。
>
> 可以多行。

### 分割线

---

## 文件格式

每篇文章是一个 `.md` 文件，放在 `content/` 目录下。

文件头部使用 YAML frontmatter：

```yaml
---
title: 文章标题
slug: url-slug
summary: 摘要
published: true
visibility: private
password: ""
tags: [tag1, tag2]
---
```

正文从 `---` 之后开始。
