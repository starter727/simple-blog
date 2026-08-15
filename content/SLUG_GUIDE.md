# Slug 编写指南

本指南帮助你正确设置文章的 slug，避免冲突和权限丢失问题。

## 什么是 Slug？

Slug 是文章的 URL 标识符，用于在浏览器中访问文章。

**示例**：
- 文章 URL: `https://your-blog.com/article/tech/python-basics`
- Slug: `tech/python-basics`

## 两种 Slug 生成方式

### 1. 自动生成（默认）

如果不指定 slug，系统会根据文件路径自动生成：

```
文件路径                                    → 自动生成的 Slug
─────────────────────────────────────────────────────────────
content/hello-world.md                     → hello-world
content/tech/python-basics.md              → tech/python-basics
content/notes/daily/2026-08-11.md          → notes/daily/2026-08-11
content/2026-08-11-hello-world.md          → hello-world（日期前缀被去掉）
```

**优点**：
- 无需额外配置
- 目录结构清晰

**缺点**：
- 移动文件会导致 slug 变更
- 可能产生意外的冲突

### 2. 手动指定

在文章的 frontmatter 中添加 `slug` 字段：

```yaml
---
title: Python 基础教程
slug: my-python-tutorial
visibility: public
---

# 内容...
```

**优点**：
- URL 稳定，不受文件位置影响
- 可以自定义更友好的 URL
- 避免自动生成的冲突

**缺点**：
- 需要手动管理

## 最佳实践

### ✅ 推荐做法

#### 1. 使用有意义的 slug

```yaml
# 好的 slug
slug: python-basics-tutorial
slug: fastapi-quick-start
slug: 2026-08-12-daily-notes

# 不好的 slug
slug: post-1
slug: article
slug: test
```

#### 2. 使用小写字母和连字符

```yaml
# 正确
slug: python-basics-tutorial

# 错误
slug: Python_Basics_Tutorial  # 避免大写
slug: python.basics.tutorial  # 避免点号
slug: python basics tutorial  # 避免空格
```

#### 3. 保持 slug 简洁

```yaml
# 好的长度
slug: python-basics
slug: fastapi-guide

# 太长
slug: python-basics-tutorial-for-beginners-2026-edition
```

#### 4. 使用目录结构组织

```yaml
# 技术文章
slug: tech/python-basics
slug: tech/fastapi-guide
slug: tech/docker-setup

# 笔记
slug: notes/daily/2026-08-12
slug: notes/weekly/week-33

# 项目
slug: projects/blog-system
slug: projects/api-design
```

### ❌ 避免的做法

#### 1. 避免通用名称

```yaml
# 容易冲突
slug: python
slug: tutorial
slug: guide
slug: notes
```

#### 2. 避免特殊字符

```yaml
# 错误
slug: python@basics
slug: fastapi#guide
slug: notes/daily/2026/08/12  # 避免斜杠过多
```

#### 3. 避免过长

```yaml
# 太长，难以记忆
slug: my-very-long-and-detailed-python-basics-tutorial-for-complete-beginners
```

## 命名规范建议

### 按类型命名

```yaml
# 技术文章：类型/主题
slug: tech/python-basics
slug: tech/fastapi-guide
slug: tech/docker-setup

# 笔记：类型/日期
slug: notes/daily/2026-08-12
slug: notes/weekly/week-33

# 项目：类型/项目名
slug: projects/blog-system
slug: projects/api-design

# 教程：类型/主题/部分
slug: tutorials/python/part-1
slug: tutorials/python/part-2
```

### 按时间命名

```yaml
# 日记
slug: daily/2026-08-12
slug: daily/2026-08-13

# 周报
slug: weekly/2026-week-33

# 月度总结
slug: monthly/2026-08
```

### 按项目命名

```yaml
# 项目文档
slug: blog-system/setup-guide
slug: blog-system/api-docs
slug: blog-system/deployment

# 项目笔记
slug: blog-system/notes/2026-08-12
```

## 冲突处理

### 如何避免冲突

1. **使用目录结构**：`tech/python-basics` 比 `python-basics` 更不容易冲突
2. **添加类型前缀**：`tutorial-python-basics`、`notes-python-basics`
3. **使用日期**：`2026-08-12-python-basics`
4. **手动指定 slug**：确保唯一性

### 如果发生冲突

**检测方式**：
- 同步时会自动检测重复的 slug
- 会在日志中显示警告信息
- 后出现的文件会被跳过

**解决方法**：
1. 检查同步日志，找出冲突的文件
2. 修改其中一个文件的 slug
3. 重新同步

## Slug 变更

### 何时会变更

1. **文件移动**：从 `tech/python.md` 移动到 `notes/python.md`
2. **手动指定**：从自动生成改为手动指定
3. **修改指定**：修改 frontmatter 中的 slug 字段

### 变更后的影响

**自动迁移**：
- ✅ 权限设置会自动迁移
- ✅ 可见性、密码等配置保留
- ✅ 不会创建重复记录

**注意事项**：
- ⚠️ 旧的 URL 会失效
- ⚠️ 搜索引擎索引需要更新
- ⚠️ 外部链接会失效

### 最佳实践

1. **尽早确定 slug**：发布前确定好 slug，避免后期变更
2. **使用手动指定**：对于重要文章，手动指定 slug
3. **保持稳定**：一旦发布，尽量不要修改 slug
4. **记录变更**：如果必须修改，记录变更原因

## 示例模板

### 技术文章

```yaml
---
title: Python 基础教程
slug: tech/python-basics
summary: Python 语言的基础知识和入门指南
visibility: public
published: true
tags: [python, tutorial, beginner]
---

# Python 基础教程

文章内容...
```

### 日记

```yaml
---
title: 2026年8月12日日记
slug: notes/daily/2026-08-12
summary: 今天的记录
visibility: private
published: true
---

# 今日记录

日记内容...
```

### 项目文档

```yaml
---
title: 博客系统部署指南
slug: projects/blog-system/deployment
summary: 博客系统的部署和配置指南
visibility: public
published: true
tags: [deployment, guide]
---

# 部署指南

部署步骤...
```

## 总结

| 场景 | 推荐做法 |
|------|----------|
| **普通文章** | 自动生成，使用目录结构 |
| **重要文章** | 手动指定，保持稳定 |
| **系列文章** | 使用统一前缀，如 `tutorials/python/part-1` |
| **日记** | 使用日期，如 `notes/daily/2026-08-12` |
| **项目文档** | 使用项目名，如 `blog-system/setup-guide` |

**核心原则**：
1. **有意义**：slug 应该能反映文章内容
2. **简洁**：不要太长，易于记忆
3. **稳定**：一旦确定，尽量不要修改
4. **唯一**：避免与其他文章冲突
