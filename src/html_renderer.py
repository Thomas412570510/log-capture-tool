import os
import json
import html
from pathlib import Path
from playwright.sync_api import sync_playwright

def generate_html_string(log_source: str, error_count: int, chunk_errors: list, page_num: int, total_pages: int) -> str:
    if error_count > 0:
        errors_html = "".join(f"<div class='error-item'>{html.escape(err)}</div>" for err in chunk_errors)
        page_indicator = f" (Page {page_num}/{total_pages})" if total_pages > 1 else ""
    else:
        errors_html = "<div class='success-box'>✔ System operating normally, no errors detected.</div>"
        page_indicator = ""

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
                    Error Log{page_indicator}
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

    MAX_DISPLAY = 15

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for data in all_cases_data:
            case_name = data.get("case_name")
            if not case_name:
                continue
                
            log_source = data.get("log_source", "Unknown")
            error_count = data.get("error_count", 0)
            errors = data.get("errors", [])

            # 恢復：在 output 建立各 case 的專屬資料夾
            output_case_dir = base_dir / base_output_dir / case_name
            output_case_dir.mkdir(parents=True, exist_ok=True)

            # 分割邏輯 (Chunking)
            if error_count == 0:
                chunks = [[]]
            else:
                chunks = [errors[i:i + MAX_DISPLAY] for i in range(0, len(errors), MAX_DISPLAY)]
                
            total_pages = len(chunks)

            for i, chunk in enumerate(chunks):
                page_num = i + 1
                html_content = generate_html_string(log_source, error_count, chunk, page_num, total_pages)
                
                # 檔案命名加入頁碼
                html_path = output_case_dir / f"report_{page_num}.html"
                html_path.write_text(html_content, encoding="utf-8")

                png_path = output_case_dir / f"report_{page_num}.png"
                page.goto(f"file:///{html_path.absolute().as_posix()}")
                page.wait_for_load_state("networkidle")
                page.locator("#capture-area").screenshot(path=str(png_path), omit_background=True)
                
                print(f"[Renderer] {case_name}: 第 {page_num}/{total_pages} 頁截圖完成 -> {png_path.name}")

        browser.close()

if __name__ == "__main__":
    run_html_rendering()
