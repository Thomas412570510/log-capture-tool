import os
import re
import json
from pathlib import Path

def parse_email(file_path: str) -> dict:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8", errors="ignore")
    
    body_content = content
    body_content = re.sub(r"^(?:主題|Subject):\s*(.+)$", "", body_content, flags=re.MULTILINE | re.IGNORECASE)
    body_content = re.sub(r"^(?:寄件者|From):\s*(.+)$", "", body_content, flags=re.MULTILINE | re.IGNORECASE)
    body_content = re.sub(r"^(?:收件者|To):\s*(.+)$", "", body_content, flags=re.MULTILINE | re.IGNORECASE)
    body_content = re.sub(r"^(?:日期|Date):\s*(.+)$", "", body_content, flags=re.MULTILINE | re.IGNORECASE)
    body_content = body_content.strip()

    return {
        "file_name": path.name,
        "body": body_content
    }

def extract_errors_from_text(text: str) -> list:
    lines = text.splitlines()
    errors = []
    for line in lines:
        if not line.strip():
            continue
        if re.search(r"(error|fail|exception|fatal|500)", line, re.IGNORECASE):
            errors.append(line.strip())
    return errors

def run_extraction(base_input_dir: str = "input", base_output_dir: str = "processed"):
    # 修復 4：採用絕對路徑與相對於本腳本的目錄位置
    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / base_input_dir
    
    if not input_path.exists():
        print(f"[Extractor] 找不到目錄 '{input_path}'")
        return

    case_dirs = sorted([d for d in input_path.iterdir() if d.is_dir() and d.name.lower().startswith("case")])
    if not case_dirs:
        case_dirs = sorted([d for d in input_path.iterdir() if d.is_dir()])
    if not case_dirs:
        return

    print("==========================================")
    print("啟動資料擷取模組 (Extractor)")
    print("==========================================")

    all_cases_data = []

    for case_dir in case_dirs:
        # 1. 讀取 Email
        email_data = {}
        email_files = list(case_dir.glob("email*.md")) + list(case_dir.glob("email*.txt"))
        if email_files:
            email_data = parse_email(str(email_files[0]))

        # 2. 擷取錯誤 Log
        log_errors = []
        log_source = "Unknown"

        # 優先找附件 .log
        log_files = list(case_dir.glob("*.log"))
        if log_files:
            log_file = log_files[0]
            text = log_file.read_text(encoding="utf-8", errors="ignore")
            log_errors = extract_errors_from_text(text)
            if log_errors:
                log_source = log_file.name

        # 如果沒有，找 Email 內文
        if not log_errors and email_data:
            body = email_data.get("body", "")
            log_errors = extract_errors_from_text(body)
            if log_errors:
                log_source = "Email Body"

        # 3. 準備 JSON 資料
        result_data = {
            "case_name": case_dir.name,
            "log_source": log_source,
            "error_count": len(log_errors),
            "errors": log_errors
        }
        all_cases_data.append(result_data)
        
        print(f"[Extractor] {case_dir.name}: 資料擷取完成")

    # 4. 統一輸出單一 JSON 到 processed 目錄
    processed_dir = base_dir / base_output_dir
    processed_dir.mkdir(parents=True, exist_ok=True)
    json_path = processed_dir / "extracted_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_cases_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n[Extractor] 所有資料已彙整並儲存至：{json_path.absolute()}")

if __name__ == "__main__":
    run_extraction()
