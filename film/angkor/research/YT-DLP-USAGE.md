# Angkor / yt-dlp 云端下载

此流程安装 yt-dlp 与 ffmpeg，在 GitHub Actions 云端执行；不要求在个人电脑安装。

## 运行方法
1. 打开仓库 Actions → **Angkor yt-dlp downloader** → Run workflow。
2. 在 video_url 输入一个公开视频 URL，点击 Run workflow。
3. 运行成功后，在本次 Actions 页面底部 **Artifacts** 下载 `angkor-yt-dlp-download`。
4. 压缩包包含视频、可获取的封面与来源元数据（info.json）、来源 URL 和文件清单。

## 边界
- 每次处理单条视频，不下载播放列表。
- 原文件存储在 GitHub Actions Artifacts 中，默认保留 **7 天**，**不会自动提交到 Git 仓库**，避免大文件冲击仓库容量。
- 受网站登录、反爬、地区或 DRM 等因素影响，某些网址可能无法下载；不要绕过访问控制。
- 不涉及任何 LOCKED 文件，也不覆盖 `film/angkor/` 现有内容。
- 仅下载你有权获取和使用的内容；来源记录不代表自动获得转载授权。
