# GitHub Pages 部署指南

本文档说明如何将租房数据分析网站部署到 GitHub Pages。

## 前提条件

- 已有 GitHub 账号
- 本地已安装 Git
- 项目代码已推送到 GitHub 仓库

## 部署步骤

### 方式一：通过 GitHub 仓库设置（推荐）

1. **推送 gh-pages 目录到 GitHub**

   确保 `gh-pages/` 目录下的所有文件已提交并推送到 GitHub：

   ```bash
   git add gh-pages/
   git commit -m "Add GitHub Pages website"
   git push origin main
   ```

2. **配置 GitHub Pages**

   - 访问你的 GitHub 仓库页面
   - 点击 **Settings** → **Pages**
   - 在 **Source** 下拉菜单中选择：
     - Branch: `main`
     - Folder: `/gh-pages`
   - 点击 **Save**

3. **等待部署完成**

   - GitHub 会自动构建和部署网站（通常需要 1-2 分钟）
   - 部署成功后，页面上会显示网站地址：
     ```
     Your site is published at https://<username>.github.io/<repository-name>/
     ```

4. **访问网站**

   打开上述地址，即可查看部署的数据分析网站。

### 方式二：通过 gh-pages 分支（高级）

如果你希望使用独立的 `gh-pages` 分支：

```bash
# 1. 安装 gh-pages 工具（可选）
npm install -g gh-pages

# 2. 部署 gh-pages 目录到 gh-pages 分支
gh-pages -d gh-pages

# 3. 在 GitHub Settings → Pages 中选择 gh-pages 分支
```

## 本地测试

在部署前，建议先在本地测试网站：

```bash
# 进入 gh-pages 目录
cd gh-pages

# 启动本地 HTTP 服务器
python3 -m http.server 8000

# 打开浏览器访问
# http://localhost:8000
```

**注意事项**：
- 必须使用 HTTP 服务器访问，直接双击 `index.html` 可能因跨域问题导致 JSON 加载失败
- 确保 `data/analysis_data.json` 文件存在且格式正确

## 文件结构

确保 `gh-pages/` 目录结构如下：

```
gh-pages/
├── index.html          # 主页
├── css/
│   └── style.css       # 样式文件
├── js/
│   └── app.js          # JavaScript 逻辑
└── data/
    └── analysis_data.json  # 分析数据（JSON格式）
```

## 常见问题

### Q1: 网站显示 404 错误

**解决方案**：
- 确认 GitHub Pages 设置中的 Source 配置正确（Branch: main, Folder: /gh-pages）
- 检查 `gh-pages/index.html` 文件是否存在
- 等待 2-3 分钟让 GitHub 完成部署

### Q2: 图表不显示

**解决方案**：
- 打开浏览器开发者工具（F12）→ Console，查看是否有 JavaScript 错误
- 检查 `data/analysis_data.json` 文件是否存在
- 确认 ECharts CDN 链接正常加载

### Q3: 样式错乱

**解决方案**：
- 检查 `css/style.css` 文件是否存在
- 确认 HTML 中的 CSS 引用路径正确

### Q4: JSON 数据加载失败（跨域错误）

**解决方案**：
- 本地测试时必须使用 HTTP 服务器，不能直接打开 HTML 文件
- GitHub Pages 部署后不会有跨域问题

## 更新网站

当分析数据或代码有更新时：

```bash
# 1. 重新生成 JSON 数据（如果数据有更新）
uv run python scripts/convert_csv_to_json.py

# 2. 提交更改
git add gh-pages/
git commit -m "Update analysis data and charts"

# 3. 推送到 GitHub
git push origin main

# GitHub 会自动重新部署（1-2 分钟后生效）
```

## 自定义域名（可选）

如果你有自己的域名，可以配置自定义域名：

1. 在 `gh-pages/` 目录下创建 `CNAME` 文件：
   ```bash
   echo "yourdomain.com" > gh-pages/CNAME
   ```

2. 在域名提供商处配置 DNS：
   - 添加 CNAME 记录，指向 `<username>.github.io`

3. 在 GitHub Pages 设置中填入自定义域名

## 隐私与安全

- ✅ 本网站为静态页面，不收集用户数据
- ✅ 所有数据均为公开的分析结果，不包含敏感信息
- ⚠️ 项目说明：遵循学术诚信，代码和原始数据集不公开，仅部署静态网页用于展示和评阅

## 技术支持

如有问题，请检查：
1. [GitHub Pages 官方文档](https://docs.github.com/en/pages)
2. [ECharts 官方文档](https://echarts.apache.org/zh/index.html)
3. 浏览器控制台的错误信息

---

**部署完成后，建议测试以下功能**：
- ✅ 所有图表正常显示
- ✅ 城市切换器（板块分析）工作正常
- ✅ 导航菜单平滑滚动
- ✅ 返回顶部按钮显示并可点击
- ✅ 响应式布局在移动端正常显示
