# 博客配置指南

本指南帮助你配置博客系统，包括内容仓库、GitHub Token 和文章设置。

## 📋 快速开始

### 1. 配置 GitHub 内容仓库

在 Railway 环境变量中添加：

```bash
# GitHub 内容仓库（private 仓库）
GITHUB_CONTENT_REPO=your-username/your-content-repo
GITHUB_CONTENT_PATH=content
GITHUB_CONTENT_BRANCH=main

# GitHub Token（用于读取 private 仓库）
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### 2. 生成 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Fine-grained tokens"
3. 设置 Token 名称：`blog-content-reader`
4. 设置过期时间：建议 90 天
5. Repository access：选择 "Only select repositories"
6. 选择你的内容仓库
7. Permissions → Repository permissions：
   - **Contents**: Read-only（只需要读权限）
8. 点击 "Generate token"
9. 复制 Token（格式：`ghp_xxxxxxxxxxxxxxxxxxxx`）

### 3. 配置内容仓库结构

```
your-content-repo/
└── content/
    ├── tech/
    │   ├── python-basics.md
    │   └── fastapi-guide.md
    ├── notes/
    │   └── daily/
    │       └── 2026-08-12.md
    └── projects/
        └── blog-system.md
```

### 4. 文章 Frontmatter 格式

```yaml
---
title: 文章标题
slug: custom-slug  # 可选，默认从文件路径生成
summary: 文章摘要  # 可选
visibility: draft  # draft | public | private
published: true    # 是否发布
tags: [python, tutorial]  # 标签，可选
---

# 文章正文

这里是 Markdown 内容...
```

## 📁 可见性设置

### 1. Draft（默认）

**行为**：
- ✅ 同步时只保存元数据（标题、slug）
- ✅ 不保存内容
- ✅ 访问时返回 404
- ✅ 列表中不显示

**设置方式**：
```yaml
---
visibility: draft
---
```

或不设置 visibility（默认为 draft）：
```yaml
---
title: 文章标题
# 没有 visibility 字段，默认为 draft
---
```

### 2. Public

**行为**：
- ✅ 所有人可见
- ✅ 保存内容到数据库
- ✅ 显示在文章列表中

**设置方式**：
```yaml
---
visibility: public
---
```

### 3. Private

**行为**：
- ✅ 只有作者（管理员）可见
- ✅ 保存内容到数据库
- ✅ 只有登录后才能看到

**设置方式**：
```yaml
---
visibility: private
---
```

### 4. Restricted

**行为**：
- ✅ 只有指定用户可见
- ✅ 保存内容到数据库
- ✅ 需要在管理后台设置访问权限

**设置方式**：
```yaml
---
visibility: restricted
---
```

## 🔧 环境变量详解

### 必填变量

```bash
# JWT 签名密钥（必须修改）
SECRET_KEY=your-super-secret-key

# 管理员密码（必须修改）
ADMIN_PASSWORD=your-strong-password

# GitHub 内容仓库
GITHUB_CONTENT_REPO=your-username/your-content-repo

# GitHub Token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### 可选变量

```bash
# 应用名称
APP_NAME=My Blog

# 调试模式（生产环境建议关闭）
DEBUG=false

# 数据库 URL（默认使用 SQLite）
DATABASE_URL=sqlite:///blog.db

# 内容路径（默认为 content）
GITHUB_CONTENT_PATH=content

# 分支（默认为 main）
GITHUB_CONTENT_BRANCH=main

# Webhook 密钥（用于 GitHub Webhook）
WEBHOOK_SECRET=your-webhook-secret

# 管理员用户名（默认为 admin）
ADMIN_USERNAME=admin
```

## 📝 配置示例

### 示例1：完全私密博客

**目标**：所有文章都是 draft，只有自己能看到

**环境变量**：
```bash
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-password
GITHUB_CONTENT_REPO=your-username/private-content
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

**文章设置**：
```yaml
---
title: 我的日记
# 没有 visibility，默认为 draft
---

今天天气很好...
```

**结果**：
- ✅ 文章不会显示在列表中
- ✅ 访问文章返回 404
- ✅ 只有数据库中有记录（元数据）

### 示例2：部分公开博客

**目标**：技术文章公开，笔记私有

**环境变量**：
```bash
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-password
GITHUB_CONTENT_REPO=your-username/blog-content
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

**文章设置**：

技术文章（公开）：
```yaml
---
title: Python 基础教程
visibility: public
---

# Python 基础

内容...
```

个人笔记（私有）：
```yaml
---
title: 2026-08-12 笔记
visibility: private
---

今天学到了...
```

**结果**：
- ✅ 技术文章：所有人可见
- ✅ 个人笔记：只有自己可见

### 示例3：混合模式

**目标**：部分文章公开，部分私有，部分草稿

**文章设置**：

公开文章：
```yaml
---
title: 公开文章
visibility: public
---
```

私有文章：
```yaml
---
title: 私有文章
visibility: private
---
```

草稿文章：
```yaml
---
title: 草稿文章
visibility: draft
---
```

或不设置（默认为 draft）：
```yaml
---
title: 草稿文章
# 没有 visibility，默认为 draft
---
```

## 🔄 同步流程

### 自动同步（推荐）

1. 配置 GitHub Webhook：
   - Payload URL: `https://your-domain.com/webhook/github`
   - Content type: `application/json`
   - Secret: 与环境变量中的 `WEBHOOK_SECRET` 一致
   - Events: Just the push event

2. 每次推送代码时自动同步

### 手动同步

1. 访问管理后台：`https://your-domain.com/admin/`
2. 登录管理员账号
3. 点击"同步内容"按钮

## 🛠️ 故障排除

### 问题1：无法读取 private 仓库

**症状**：同步时提示 404 或 403 错误

**解决方案**：
1. 检查 `GITHUB_TOKEN` 是否正确
2. 检查 Token 权限是否包含 `Contents: Read-only`
3. 检查 Token 是否过期
4. 检查仓库名称是否正确

### 问题2：文章不显示

**症状**：同步成功，但文章不显示

**解决方案**：
1. 检查文章的 `visibility` 设置
2. 如果是 `draft`，文章不会显示（这是正常行为）
3. 如果是 `public`，检查 `is_published` 是否为 `true`

### 问题3：权限设置无效

**症状**：修改了 visibility，但行为没变

**解决方案**：
1. 重新同步内容
2. 检查数据库中的 visibility 值
3. 确认修改的是正确的文章

## 📊 文章状态总结

| Visibility | 同步时 | 访问时 | 列表显示 | 内容存储 |
|------------|--------|--------|----------|----------|
| **draft** | 只存元数据 | 返回 404 | ❌ 不显示 | ❌ 不存 |
| **public** | 存元数据+内容 | 正常显示 | ✅ 显示 | ✅ 存 |
| **private** | 存元数据+内容 | 只有作者能看 | ✅ 作者可见 | ✅ 存 |
| **restricted** | 存元数据+内容 | 指定用户能看 | ✅ 有权限者可见 | ✅ 存 |

## 🔐 安全建议

### 1. Token 安全

- ✅ 只给读权限（`Contents: Read-only`）
- ✅ 设置过期时间（建议 90 天）
- ✅ 只授权给特定仓库
- ❌ 不要给写权限（除非需要写回功能）

### 2. 密码安全

- ✅ 使用强密码（至少 12 位）
- ✅ 定期更换密码
- ❌ 不要使用默认密码

### 3. 内容安全

- ✅ 敏感内容设为 `draft` 或 `private`
- ✅ 定期检查文章可见性
- ❌ 不要公开敏感信息

## 📚 相关文档

- [Slug 编写指南](SLUG_GUIDE.md)
- [README](../README.md)

## 💡 最佳实践

1. **文章分类**：使用目录结构组织文章
2. **Slug 命名**：使用有意义的 slug，便于记忆
3. **可见性管理**：
   - 草稿 → `draft`
   - 个人笔记 → `private`
   - 分享内容 → `public`
4. **定期备份**：备份 GitHub 仓库
5. **监控日志**：查看同步日志，及时发现问题

## 🎯 总结

**配置步骤**：
1. 生成 GitHub Token（只读权限）
2. 配置环境变量
3. 准备内容仓库
4. 设置文章可见性
5. 同步内容

**默认行为**：
- 新文章默认为 `draft`
- Draft 文章不显示、不存储内容
- 只有明确设置 `visibility: public` 或 `visibility: private` 才会显示

**你的博客，你做主！** 🎉
