#!/bin/bash
# 快速部署脚本（适用于 Ubuntu/Debian）

set -e

echo "🚀 开始部署博客系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 root 权限运行此脚本${NC}"
    echo "使用: sudo bash deploy.sh"
    exit 1
fi

# 配置变量
DOMAIN=""
EMAIL=""
ADMIN_PASSWORD=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --password)
            ADMIN_PASSWORD="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必需参数
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}请指定域名: --domain your-domain.com${NC}"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    echo -e "${RED}请指定邮箱: --email your@email.com${NC}"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    echo -e "${YELLOW}未指定管理员密码，将使用默认密码${NC}"
    ADMIN_PASSWORD="change-me-$(date +%s)"
fi

echo -e "${GREEN}域名: $DOMAIN${NC}"
echo -e "${GREEN}邮箱: $EMAIL${NC}"

# 更新系统
echo -e "${YELLOW}📦 更新系统...${NC}"
apt update && apt upgrade -y

# 安装依赖
echo -e "${YELLOW}📦 安装依赖...${NC}"
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# 创建应用目录
APP_DIR="/opt/blog"
echo -e "${YELLOW}📁 创建应用目录: $APP_DIR${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# 克隆代码（如果还没有）
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📥 克隆代码...${NC}"
    # git clone https://github.com/your-username/your-blog.git .
    echo "请手动克隆代码到 $APP_DIR"
    exit 1
fi

# 创建虚拟环境
echo -e "${YELLOW}🐍 创建虚拟环境...${NC}"
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo -e "${YELLOW}📦 安装 Python 依赖...${NC}"
pip install -e .

# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 创建环境配置
echo -e "${YELLOW}⚙️ 创建配置文件...${NC}"
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
ADMIN_PASSWORD=$ADMIN_PASSWORD
DATABASE_URL=sqlite:///blog.db
DEBUG=false
EOF

# 初始化数据库
echo -e "${YELLOW}🗄️ 初始化数据库...${NC}"
python3 -c "from app.database import init_db; init_db()"

# 创建 systemd 服务
echo -e "${YELLOW}🔧 创建系统服务...${NC}"
cat > /etc/systemd/system/blog.service << EOF
[Unit]
Description=Blog Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"
systemctl daemon-reload
systemctl enable blog
systemctl start blog

# 配置 Nginx
echo -e "${YELLOW}🌐 配置 Nginx...${NC}"
cat > /etc/nginx/sites-available/blog << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 配置 SSL
echo -e "${YELLOW}🔒 配置 SSL...${NC}"
certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

# 配置自动续期
echo -e "${YELLOW}🔄 配置证书自动续期...${NC}"
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# 完成
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo -e "${GREEN}访问地址: https://$DOMAIN${NC}"
echo -e "${GREEN}管理后台: https://$DOMAIN/admin/${NC}"
echo ""
echo -e "${YELLOW}管理员账号: admin${NC}"
echo -e "${YELLOW}管理员密码: $ADMIN_PASSWORD${NC}"
echo ""
echo -e "${YELLOW}请立即登录并修改密码！${NC}"
echo ""
echo "常用命令："
echo "  查看状态: systemctl status blog"
echo "  查看日志: journalctl -u blog -f"
echo "  重启服务: systemctl restart blog"
echo "  编辑配置: vim $APP_DIR/.env"