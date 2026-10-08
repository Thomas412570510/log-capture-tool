import os
import sys
from pathlib import Path

def main():
    print("==========================================")
    print("啟動自動化流程")
    print("==========================================")
    
    python_exe = sys.executable
    base_dir = Path(__file__).resolve().parent

    extractor_script = base_dir / "src" / "extractor.py"
    renderer_script = base_dir / "src" / "html_renderer.py"

    # 步驟 1: 執行資料擷取
    print("\n>>> 步驟 1: 執行 src/extractor.py")
    ret1 = os.system(f'"{python_exe}" "{extractor_script}"')
    if ret1 != 0:
        print("資料擷取失敗。")
        return
        
    # 步驟 2: 執行畫面渲染
    print("\n>>> 步驟 2: 執行 src/html_renderer.py")
    ret2 = os.system(f'"{python_exe}" "{renderer_script}"')
    if ret2 != 0:
        print("畫面渲染失敗。")
        return

    print("\n流程全部完成！")

if __name__ == "__main__":
    main()
