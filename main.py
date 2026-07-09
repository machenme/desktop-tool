import ctypes
import os
import shutil
import subprocess
import sys
import time
import webview


# 【新增】自动提升为管理员权限，防止剪切公共桌面时报 PermissionError
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


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

                # 如果目标已存在，尝试加后缀或者直接跳过
                if not os.path.exists(dst):
                    shutil.move(src, dst)
                    moved += 1
                else:
                    # 个人桌面已有同名文件，跳过避免覆盖
                    continue
            return f"成功移动/清理了 {moved} 个文件。"
        except PermissionError:
            return "错误：权限不足！请右键选择‘以管理员身份运行’。"
        except Exception as e:
            return f"错误: {str(e)}"

    def clear_icon_cache(self):
        """更彻底的 Win10/Win11 图标缓存清理"""
        try:
            # 1. 强制结束资源管理器
            subprocess.run(
                "taskkill /f /im explorer.exe",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            time.sleep(1.5)  # 给系统一点释放文件的时间

            local_appdata = os.environ["LOCALAPPDATA"]

            # 2. 删除旧版缓存
            cache_path = os.path.join(local_appdata, "IconCache.db")
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except:
                    pass

            # 3. 删除 Win10/Win11 核心图标缓存文件夹
            modern_cache_dir = os.path.join(
                local_appdata, r"Microsoft\Windows\Explorer"
            )
            if os.path.exists(modern_cache_dir):
                for f in os.listdir(modern_cache_dir):
                    if f.startswith("iconcache_") and f.endswith(".db"):
                        try:
                            os.remove(os.path.join(modern_cache_dir, f))
                        except:
                            continue  # 个别被占用的跳过

            return "图标缓存已深度清理！重启资源管理器中..."
        except Exception as e:
            return f"失败: {str(e)}"
        finally:
            # 无论成功与否，必须确保拉起 explorer，使用 start 命令更安全
            subprocess.Popen("start explorer.exe", shell=True)

    def clean_lnk_names(self):
        """精准清除尾部的快捷方式字样，不误伤文件名内部"""
        try:
            count = 0
            for f in os.listdir(self.desktop):
                if f.lower().endswith(".lnk"):
                    name, ext = os.path.splitext(f)  # name: 软件名, ext: .lnk

                    # 精准匹配结尾
                    if name.endswith(" - 快捷方式"):
                        name = name[: - len(" - 快捷方式")]
                    elif name.endswith("快捷方式"):
                        name = name[: - len("快捷方式")]

                    # 顺便处理 .exe 嵌套
                    if name.lower().endswith(".exe"):
                        name = name[: - len(".exe")]

                    # 极端情况：裁剪后文件名为空则跳过
                    if not name:
                        continue

                    new_name = name + ext
                    old_path = os.path.join(self.desktop, f)
                    new_path = os.path.join(self.desktop, new_name)

                    if old_path != new_path and not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        count += 1
            return f"优化了 {count} 个快捷方式名称。"
        except Exception as e:
            return f"更名失败: {str(e)}"

    def remove_exe_suffix(self):
        # 逻辑合并到了 clean_lnk_names 中，这里保留接口供前端调用
        return self.clean_lnk_names()


html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; padding: 20px; background: #f4f7f9; text-align: center; user-select: none; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        h3 { color: #333; margin-bottom: 20px; font-weight: 600; }
        button { 
            width: 100%; padding: 12px; margin: 8px 0; border: none; border-radius: 6px;
            background: #0078d4; color: white; cursor: pointer; font-size: 14px;
            transition: all 0.15s ease;
        }
        button:hover { background: #005a9e; }
        button:active { transform: scale(0.98); }
        #log { margin-top: 15px; font-size: 13px; color: #444; padding: 12px; background: #eef1f5; border-radius: 6px; min-height: 18px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="card">
        <h3>桌面图标优化助手</h3>
        <button onclick="safeRun('move_common_files')">1. 收回公共桌面图标到个人桌面</button>
        <button onclick="safeRun('clean_lnk_names')">2. 一键修复名称 (去后缀/快捷方式)</button>
        <button onclick="safeRun('clear_icon_cache')">3. 深度清理图标缓存 (全黑/白图标)</button>
        <div id="log">等待操作...</div>
    </div>

    <script>
        async function safeRun(method) {
            const log = document.getElementById('log');
            if (!window.pywebview || !window.pywebview.api) {
                log.innerText = "正在初始化底层通信...";
                setTimeout(() => safeRun(method), 200);
                return;
            }

            log.innerText = "正在处理，请稍候...";
            try {
                const res = await window.pywebview.api[method]();
                log.innerText = res;
            } catch (e) {
                log.innerText = "运行出错: " + e;
            }
        }

        window.addEventListener('pywebviewready', () => {
            document.getElementById('log').innerText = "系统就绪，点击按钮开始操作";
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    # 如果不是管理员，启动时自动请求 UAC 提升权限
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

    api = Api()
    window = webview.create_window(
        "桌面助手", html=html, js_api=api, width=400, height=450, resizable=False
    )
    webview.start(debug=False)