**项目名**: 桌面助手

**简介**:
- 简洁的 Windows 桌面优化 GUI 工具，基于 `pywebview`。提供将公共桌面文件移动到当前用户桌面、清理图标缓存以及批量规范化 `.lnk` 快捷方式名称的功能。

**主要功能**:
- **解决桌面找不到快捷方式图标的问题**
- **移动公共桌面文件**: 将 `C:\\Users\\Public\\Desktop` 下未在当前用户桌面存在的文件移动到用户桌面。
- **清理图标缓存(快捷方式图标变成白色那种)**: 暂时结束 `explorer.exe` 并删除本地图标缓存 `IconCache.db`，随后重启资源管理器以刷新图标显示。
- **清理快捷方式名**: 批量移除快捷方式中文名中的“快捷方式”字样，并将 `.exe.lnk` 规范为 `.lnk`。

**依赖**:
- Python >= 3.13
- `pywebview` (用于内嵌 Web UI)
- `pyinstaller` (可选，用于打包为单文件可执行程序)

可安装命令：

```bash
uv sync
```
或者:
```bash
pip install pywebview pyinstaller
```

**运行**:
- 在开发环境中直接运行:
```bash
uv run main.py
```

- 启动后会弹出一个固定大小的窗口，三个按钮对应三项主要功能，操作结果会在界面下方显示。

**打包 (生成可执行文件)**:
- 使用 `pyinstaller` 生成单文件窗口程序：
```bash
uv run pyinstaller --onefile --windowed main.py
```

- 打包完成后，可执行文件位于 `dist/` 目录中。若需要包含额外资源或图标，请参考 `pyinstaller` 文档并在命令中添加 `--add-data` / `--icon` 等参数。

**注意事项 / 权限**:
- `clear_icon_cache` 操作会终止并重启 `explorer.exe`，请保存未完成的工作以防数据丢失。
- 移动公共桌面文件可能需要文件系统权限；在某些环境下可能需要以管理员权限运行程序。
- 仅在 Windows 系统上测试与支持。

**项目文件**:
- 主脚本: `main.py`

**许可与反馈**:
- 随便写着玩的。
