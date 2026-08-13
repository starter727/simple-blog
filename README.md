# My Blog - 个人博客系统

一个基于 FastAPI 的个人博客系统，支持文章级权限控制和 Markdown 内容管理。

## ✨ 功能特性

### 核心功能
- 📝 Markdown 文章管理（支持 YAML frontmatter）
- 🔐 文章级权限控制（公开/私有/受限/密码保护）
- 👥 用户认证（JWT Token）
- 🏷️ 文章分类（基于目录结构）
- 🔄 Git Webhook 自动同步
- 📱 响应式设计（Tailwind CSS）

### 内容管理
- 支持嵌套目录结构
- 自动从文件路径生成 slug
- WikiLink 语法支持（`[[链接]]`）
- 代码语法高亮（Pygments）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 pip
pip install -e .

# 或使用 uv（推荐）
uv pip install -e .
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件，填入：
# - SECRET_KEY: JWT 签名密钥（必须修改）
# - ADMIN_PASSWORD: 管理员密码（必须修改）
vim .env
```

### 3. 启动应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问应用

- 首页：http://localhost:8000
- 管理后台：http://localhost:8000/admin/
- API 文档：http://localhost:8000/docs

## 📁 项目结构

```
blog/
├── app/
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库配置
│   ├── auth_utils.py        # 认证工具
│   │
│   ├── models/              # 数据模型
│   │   ├── user.py          # 用户模型
│   │   └── article.py       # 文章模型
│   │
│   ├── schemas/             # 数据验证
│   │   └── article.py       # 文章模式
│   │
│   ├── services/            # 业务逻辑
│   │   ├── content_loader.py # 文件加载
│   │   ├── markdown_service.py # Markdown 渲染
│   │   ├── permission.py    # 权限控制
│   │   ├── sync.py          # 同步服务
│   │   └── wikilink_ext.py  # WikiLink 扩展
│   │
│   ├── routers/             # 路由处理
│   │   ├── auth.py          # 认证路由
│   │   ├── articles.py      # 文章路由
│   │   ├── admin.py         # 管理路由
│   │   └── webhook.py       # Webhook 路由
│   │
│   └── templates/           # 页面模板
│       ├── base.html        # 基础布局
│       ├── auth/            # 认证页面
│       ├── articles/        # 文章页面
│       └── admin/           # 管理页面
│
├── static/                  # 静态资源
│   └── css/style.css        # 自定义样式
│
├── content/                 # Markdown 内容
│   ├── tech/                # 技术文章
│   └── notes/               # 笔记
│
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量示例
└── README.md                # 项目说明
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | JWT 签名密钥（必填） | - |
| `ADMIN_PASSWORD` | 管理员密码（必填） | - |
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///blog.db` |
| `CONTENT_DIR` | 内容目录路径 | `./content` |
| `DEBUG` | 调试模式 | `false` |
| `WEBHOOK_SECRET` | GitHub Webhook 密钥 | - |

### 文章 Frontmatter

```yaml
---
title: 文章标题
slug: custom-slug  # 可选，默认从文件路径生成
summary: 文章摘要
visibility: public  # public | private | restricted
password: optional-password  # 可选
published: true
tags: [python, tutorial]
---

# 文章正文

这里是 Markdown 内容...
```

### 目录结构与分类

```
content/
├── tech/                    # 分类：tech
│   ├── python-basics.md     # slug: tech/python-basics
│   └── fastapi-guide.md     # slug: tech/fastapi-guide
├── notes/                   # 分类：notes
│   └── daily/
│       └── 2026-08-12.md    # slug: notes/daily/2026-08-12
└── hello-world.md           # 无分类，slug: hello-world
```

## 🔐 权限系统

### 文章可见性

| 类型 | 说明 | 访问控制 |
|------|------|----------|
| `public` | 公开 | 所有人可见 |
| `private` | 私有 | 仅作者可见 |
| `restricted` | 受限 | 指定用户可见 |
| 密码保护 | 需要密码 | 提供正确密码即可 |

### 权限检查优先级

1. **作者**：始终有权限
2. **私有文章**：只有作者能看
3. **受限文章**：必须在访问列表中
4. **密码保护**：需要提供正确密码
5. **默认**：允许访问

## 🔄 同步机制

### 手动同步

访问管理后台，点击"同步内容"按钮。

### 自动同步（GitHub Webhook）

1. 在 GitHub 仓库设置 Webhook
2. Payload URL: `https://your-domain.com/webhook/github`
3. Content type: `application/json`
4. Secret: 与 `.env` 中的 `WEBHOOK_SECRET` 一致

## 📋 迭代计划

### ✅ 已完成

- [x] 基础框架搭建（FastAPI + SQLAlchemy）
- [x] 用户认证系统（JWT）
- [x] 文章 CRUD（基于文件系统）
- [x] 权限控制系统
- [x] Markdown 渲染（带扩展）
- [x] 分类功能
- [x] Webhook 同步
- [x] 响应式 UI

### 🚧 进行中

- [ ] 完善错误处理
- [ ] 添加日志系统
- [ ] 优化性能（缓存）

### 📅 计划中

#### 短期（1-2 周）
- [ ] 文章搜索功能
- [ ] 文章标签系统
- [ ] RSS 订阅
- [ ] 评论系统（可选）

#### 中期（1-2 月）
- [ ] 多语言支持
- [ ] 文章版本历史
- [ ] 图片上传
- [ ] SEO 优化

#### 长期（3+ 月）
- [ ] 多用户博客
- [ ] API 开放平台
- [ ] 移动端 App
- [ ] 性能监控

## 🛠️ 开发指南

### 添加新功能

1. **数据模型**：在 `app/models/` 添加
2. **业务逻辑**：在 `app/services/` 实现
3. **路由处理**：在 `app/routers/` 定义
4. **页面模板**：在 `app/templates/` 创建

### 代码规范

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串
- 保持函数简洁

### 测试

```bash
# 运行测试
pytest

# 带覆盖率
pytest --cov=app
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- 作者：Your Name
- 邮箱：your.email@example.com
- 博客：https://your-blog.com
