#!/bin/bash
# preflight-check.sh — 安装前环境校验

set -e

# 1. 检查 CLI 是否安装
if ! command -v skillhub &> /dev/null; then
    echo "❌ skillhub CLI 未安装，请先执行安装脚本"
    echo "   curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only"
    exit 1
fi

# 2. 检查目标目录是否存在
TARGET_DIR="${1:-$HOME/.openclaw/skills}"
if [ ! -d "$TARGET_DIR" ]; then
    echo "⚠️  目标目录不存在，自动创建: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# 3. 检查磁盘空间（至少 10MB）
AVAILABLE_SPACE=$(df -m "$TARGET_DIR" | awk 'NR==2{print $4}')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    echo "❌ 磁盘空间不足（${AVAILABLE_SPACE}MB），至少需要 10MB"
    exit 1
fi

# 4. 检查网络连接
if ! curl -s --connect-timeout 5 https://skillhub.cn > /dev/null 2>&1; then
    echo "⚠️  无法连接到 skillhub.cn，请检查网络或切换国内源"
    echo "   export SKILLHUB_REGISTRY=https://skillhub.cn"
fi

echo "✅ 环境校验通过"
