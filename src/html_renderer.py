import os
import json
import html
from pathlib import Path
from playwright.sync_api import sync_playwright

def generate_html_string(data: dict) -> str:
    log_source = data.get("log_source", "Unknown")
    error_count = data.get("error_count", 0)
    errors = data.get("errors", [])

    if error_count > 0:
        MAX_DISPLAY = 15
        display_errors = errors[:MAX_DISPLAY]
        # 修復 1：使用 html.escape 防止 Log 中的 < 或 > 符號破壞 HTML 排版
        errors_html = "".join(f"<div class='error-item'>{html.escape(err)}</div>" for err in display_errors)
        
        if error_count > MAX_DISPLAY:
            hidden_count = error_count - MAX_DISPLAY
            errors_html += f"<div class='error-item' style='text-align: center; color: #57606a; background-color: #f6f8fa; border: 1px dashed #d0d7de;'>... 還有 {hidden_count} 筆錯誤被折疊，請參閱原始檔案 ...</div>"
    else:
        errors_html = "<div class='success-box'>✔ System operating normally, no errors detected.</div>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body {{ font-family: 'Inter', 'Segoe UI', sans-serif; background-color: transparent; padding: 40px; margin: 0; display: inline-block; }}
            .report-card {{ background: #ffffff; border: 1px solid #e1e4e8; border-radius: 12px; box-shadow: 0 8px 24px rgba(149, 157, 165, 0.15); width: 800px; overflow: hidden; }}
            .header {{ background: #fff5f5; border-bottom: 1px solid #ffebe9; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }}
            .header-title {{ color: #cf222e; font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 10px; }}
            .badge {{ background-color: #ffffff; color: #57606a; border: 1px solid #d0d7de; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }}
            .content {{ padding: 24px; }}
            .error-list {{ display: flex; flex-direction: column; gap: 10px; }}
            .error-item {{ background-color: #f6f8fa; border-left: 4px solid #cf222e; padding: 12px 16px; border-radius: 6px; color: #24292f; font-family: 'Consolas', monospace; font-size: 14px; word-break: break-all; }}
            .success-box {{ background-color: #dafbe1; border: 1px solid #4ac26b; color: #1a7f37; padding: 16px; border-radius: 8px; font-weight: 600; text-align: center; font-size: 15px; }}
        </style>
    </head>
    <body>
        <div class="report-card" id="capture-area">
            <div class="header">
                <div class="header-title">
                    <svg width="22" height="22" viewBox="0 0 16 16" fill="currentColor">
                        <path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8zm6.5-.25A.75.75 0 017.25 7h1.5a.75.75 0 01.75.75v2.5a.75.75 0 01-.75.75h-1.5a.75.75 0 01-.75-.75v-2.5zm1.5-3a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"></path>
                    </svg>
                    Error Log
                </div>
                <div class="badge">Source: {log_source}</div>
            </div>
            <div class="content">
                <div class="error-list">
                    {errors_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def run_html_rendering(base_output_dir: str = "output"):
    # 修復 4：採用絕對路徑與相對於本腳本的目錄位置
    base_dir = Path(__file__).resolve().parent.parent
    json_path = base_dir / "processed" / "extracted_data.json"
    
    if not json_path.exists():
        print("[Renderer] 找不到 processed/extracted_data.json，請先執行擷取腳本。")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        all_cases_data = json.load(f)

    if not all_cases_data:
        print("[Renderer] 找不到任何案例資料。")
        return

    print("==========================================")
    print("啟動畫面渲染模組 (HTML Renderer)")
    print("==========================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        output_dir = base_dir / base_output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        for data in all_cases_data:
            case_name = data.get("case_name")
            if not case_name:
                continue

            html_content = generate_html_string(data)
            html_path = output_dir / f"{case_name}_report.html"
            html_path.write_text(html_content, encoding="utf-8")

            png_path = output_dir / f"{case_name}_report.png"
            page.goto(f"file:///{html_path.absolute().as_posix()}")
            
            # 修復 2：等待網路與字體載入完畢，避免字體跑版
            page.wait_for_load_state("networkidle")
            
            page.locator("#capture-area").screenshot(path=str(png_path), omit_background=True)
            
            print(f"[Renderer] {case_name}: 截圖完成 -> {png_path.name}")

        browser.close()

if __name__ == "__main__":
    run_html_rendering()
