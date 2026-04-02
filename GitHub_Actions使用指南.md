# VaultX - GitHub Actions 构建指南

## 📋 已完成

✅ `.github/workflows/build-apk.yml` 文件已创建

---

## 🚀 执行步骤

### 方法一：运行脚本（推荐）

```powershell
# 在 PowerShell 中运行
cd E:\CODE\VaultX
.\push_workflow.bat
```

### 方法二：手动执行

```bash
# 在 Git Bash 或终端中执行
cd E:\CODE\VaultX

# 添加工作流文件
git add .github/workflows/build-apk.yml

# 提交
git commit -m "Add GitHub Actions workflow for building APK"

# 推送到 GitHub
git push origin main
```

---

## 📱 下载 APK 步骤

### 1. 访问 GitHub 仓库

打开浏览器，访问你的仓库：
```
https://github.com/YOUR_USERNAME/vaultx
```

（将 `YOUR_USERNAME` 替换为你的 GitHub 用户名）

### 2. 进入 Actions 页面

- 点击仓库顶部的 **"Actions"** 标签
- 或直接访问：`https://github.com/YOUR_USERNAME/vaultx/actions`

### 3. 查看构建状态

- 你会看到一个名为 **"Build Android APK"** 的工作流正在运行
- 点击它查看详细日志
- 构建时间约 **10-20 分钟**

### 4. 等待构建完成

构建过程：
```
⏳ Setup Python... (1 分钟)
⏳ Install dependencies... (2-3 分钟)
⏳ Build APK... (10-15 分钟)
✅ Upload artifact...
```

### 5. 下载 APK

构建完成后：
1. 点击完成的工作流（绿色 ✓ 标记）
2. 滚动到页面底部 **"Artifacts"** 区域
3. 点击 **"vaultx-apk"** 下载 ZIP 文件
4. 解压得到 `.apk` 文件

### 6. 安装到手机

**方法 A：ADB 安装**
```powershell
adb install vaultx-1.0.0-arm64-v8a-debug.apk
```

**方法 B：直接传输**
1. 连接手机到电脑
2. 复制 APK 到手机
3. 在手机上打开 APK 安装

---

## 🔧 故障排除

### Q: 构建失败怎么办？

1. 点击失败的工作流查看日志
2. 查找红色 ❌ 标记的错误步骤
3. 常见错误：
   - **依赖安装失败**：等待 GitHub 自动重试
   - **内存不足**：GitHub 有时会分配较少内存，重新运行即可
   - **超时**：重新运行工作流

### Q: 找不到 Artifacts？

- 确保 GitHub Actions 已完成（绿色 ✓）
- Artifacts 在工作流详情页底部
- 如果看不到，可能是构建失败，检查日志

### Q: APK 文件名是什么？

通常是：
```
vaultx-1.0.0-arm64-v8a-debug.apk
```

### Q: 如何手动触发构建？

1. 进入 Actions 页面
2. 选择 "Build Android APK" 工作流
3. 点击右侧 "Run workflow" 按钮
4. 选择分支并运行

---

## 📸 截图参考

### Actions 标签位置
```
[Code] [Issues] [Pull requests] [Actions] [Projects] [Wiki]
                                  ^^^^^^^
                                  点这里
```

### Artifacts 位置
```
工作流详情页面
↓ 滚动到底部
┌─────────────────────────────────┐
│ Artifacts                        │
│ ├─ vaultx-apk (下载)             │ ← 点击下载
└─────────────────────────────────┘
```

---

## ✅ 完整流程总结

```
1. 运行 push_workflow.bat
   ↓
2. 访问 GitHub 仓库 Actions 页面
   ↓
3. 等待构建完成（10-20 分钟）
   ↓
4. 下载 vaultx-apk.zip
   ↓
5. 解压得到 .apk 文件
   ↓
6. 传输到手机并安装
```

---

## 🎯 当前任务

**立即执行**：

```powershell
cd E:\CODE\VaultX
.\push_workflow.bat
```

然后访问 GitHub 仓库查看构建状态。
