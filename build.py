"""Build script: 打包为单文件 exe."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SPEC = ROOT / "main.spec"
BUILD = ROOT / "build"
DIST = ROOT / "dist"


def build_exe() -> None:
    python = sys.executable
    print(f"Python: {python}")

    # 强制清除上次构建缓存
    for p in (BUILD, DIST):
        if p.exists():
            shutil.rmtree(p)
            print(f"已清除: {p}")

    result = subprocess.run(
        [python, "-m", "PyInstaller", str(SPEC), "--noconfirm"],
        cwd=ROOT,
    )

    if result.returncode != 0:
        print("\n打包失败")
        sys.exit(result.returncode)

    exe = DIST / "main.exe"
    size_mb = exe.stat().st_size / (1024 * 1024) if exe.exists() else 0
    print(f"\n打包完成 → {exe} ({size_mb:.1f} MB)")


def main() -> None:
    if not SPEC.exists():
        print(f"错误：找不到 {SPEC}")
        sys.exit(1)

    build_exe()


if __name__ == "__main__":
    main()
