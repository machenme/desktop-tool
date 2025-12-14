import webview
import os
import shutil
import subprocess
import time


class Api:
    def __init__(self):
        self.desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.common_desktop = r"C:\Users\Public\Desktop"

    def move_common_files(self):
        try:
            if not os.path.exists(self.common_desktop):
                return "错误：找不到公共桌面文件夹。"
            files = os.listdir(self.common_desktop)
            moved = 0
            for f in files:
                if f.lower() == "desktop.ini":
                    continue
                src = os.path.join(self.common_desktop, f)
                dst = os.path.join(self.desktop, f)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
                    moved += 1
            return f"成功移动 {moved} 个文件。"
        except Exception as e:
            return f"错误: {str(e)}"

    def clear_icon_cache(self):
        try:
            # 杀死 explorer
            subprocess.run("taskkill /f /im explorer.exe", shell=True)
            time.sleep(1)
            # 删除缓存
            cache_path = os.path.join(os.environ["LOCALAPPDATA"], "IconCache.db")
            if os.path.exists(cache_path):
                os.remove(cache_path)
            # 重启 explorer
            subprocess.Popen("explorer.exe", shell=True)
            return "图标缓存已清理！"
        except Exception as e:
            subprocess.Popen("explorer.exe", shell=True)
            return f"失败: {str(e)}"

    def clean_lnk_names(self):
        try:
            count = 0
            for f in os.listdir(self.desktop):
                if f.lower().endswith(".lnk"):
                    # 1. 处理“快捷方式”字样
                    new_name = f.replace(" - 快捷方式", "").replace("快捷方式", "")
                    # 2. 处理 .exe.lnk 变 .lnk
                    if new_name.lower().endswith(".exe.lnk"):
                        new_name = new_name.replace(".exe.lnk", ".lnk")

                    old_path = os.path.join(self.desktop, f)
                    new_path = os.path.join(self.desktop, new_name)

                    if old_path != new_path and not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        count += 1
            return f"处理了 {count} 个快捷方式。"
        except Exception as e:
            return f"更名失败: {str(e)}"


html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Microsoft YaHei', sans-serif; padding: 20px; background: #f4f7f9; text-align: center; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h3 { color: #333; margin-bottom: 20px; }
        button { 
            width: 100%; padding: 12px; margin: 8px 0; border: none; border-radius: 6px;
            background: #0078d4; color: white; cursor: pointer; font-size: 14px; font-weight: bold;
            transition: 0.2s;
        }
        button:hover { background: #005a9e; transform: translateY(-1px); }
        button:active { transform: translateY(1px); }
        #log { margin-top: 15px; font-size: 13px; color: #666; padding: 10px; background: #eee; border-radius: 4px; min-height: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h3>桌面优化工具</h3>
        <button onclick="safeRun('move_common_files')">移动公共桌面文件</button>
        <button onclick="safeRun('clear_icon_cache')">清理图标缓存</button>
        <button onclick="safeRun('clean_lnk_names')">一键清理快捷方式名</button>
        <div id="log">等待操作...</div>
    </div>

    <script>
        // 增加自动重试的调用函数
        async function safeRun(method) {
            const log = document.getElementById('log');
            log.innerText = "正在尝试连接 Python...";

            // 检查 api 是否就绪，如果不就绪，等 500ms 再试
            if (!window.pywebview || !window.pywebview.api) {
                setTimeout(() => safeRun(method), 500);
                return;
            }

            log.innerText = "正在处理中，请稍候...";
            try {
                const res = await window.pywebview.api[method]();
                log.innerText = res;
            } catch (e) {
                log.innerText = "运行出错: " + e;
            }
        }

        // 初始化检查
        window.addEventListener('pywebviewready', () => {
            document.getElementById('log').innerText = "系统就绪";
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    api = Api()
    # debug=True 可以让你在界面点击右键查看浏览器控制台错误
    window = webview.create_window(
        "桌面助手",
        html=html,
        js_api=api,
        width=400,
        height=480,
        resizable=False,  # 固定窗口大小
    )
    webview.start(debug=False)
