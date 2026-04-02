# VaultX Android APK 构建 - Docker 方案（推荐）

## 🐳 使用 Docker 构建（最简单）

### 前置条件
- 安装 Docker Desktop（Windows）
- 项目文件在 `E:\CODE\VaultX\android\`

### 一键构建

```powershell
# 1. 打开 PowerShell
# 2. 运行以下命令

cd E:\CODE\VaultX\android

# 拉取 Kivy 官方构建镜像
docker pull kivy/buildozer

# 构建 APK（首次需要 30-60 分钟）
docker run -v ${PWD}:/home/user/code kivy/buildozer android debug

# APK 会生成在 bin/ 目录下
```

### 完成后

APK 文件位置：
```
E:\CODE\VaultX\android\bin\vaultx-1.0.0-arm64-v8a-debug.apk
```

---

## 📱 安装到手机

### 方法一：ADB 安装
```powershell
adb install E:\CODE\VaultX\android\bin\vaultx-*.apk
```

### 方法二：直接传输
1. 连接手机到电脑
2. 复制 APK 文件到手机
3. 在手机上打开 APK 安装

---

## ⚠️ 如果 Docker 不可用

### 方案 B：使用在线构建服务

1. 访问 https://buildozer.io/
2. 上传 `android/` 目录
3. 等待构建完成
4. 下载 APK

### 方案 C：使用 GitHub Actions

1. 将项目推送到 GitHub
2. 创建 `.github/workflows/build.yml`
3. 自动构建 APK

---

## 🔧 故障排除

### Docker 未安装
```powershell
# 下载 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### 构建失败
```powershell
# 查看详细日志
docker run -v ${PWD}:/home/user/code kivy/buildozer android debug 2>&1 | Tee-Object build.log
```

### 磁盘空间不足
```powershell
# Docker 需要 10-20 GB 空间
# 清理 Docker 缓存
docker system prune -a
```

---

## 📊 构建时间对比

| 方案 | 首次 | 后续 | 难度 |
|------|------|------|------|
| Docker | 30-60 分钟 | 5-10 分钟 | ⭐ 简单 |
| WSL | 30-60 分钟 | 5-10 分钟 | ⭐⭐⭐ 复杂 |
| 在线服务 | 10-20 分钟 | 10-20 分钟 | ⭐ 简单 |

---

**推荐**: 使用 Docker 方案，最简单可靠。
