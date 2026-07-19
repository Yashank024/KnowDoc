import json

log_path = r"C:\Users\Lenovo\.gemini\antigravity-ide\brain\a542193b-291d-40f2-8b2d-b1e39aaf520d\.system_generated\logs\transcript_full.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx + 1 == 572:
            data = json.loads(line)
            content = data.get("content", "")
            # Find the python code block starting with `import json`
            code_start = content.find("import json")
            if code_start != -1:
                # Find the next python code block end or just write the whole python code section
                code_section = content[code_start:]
                with open("raw_ocr_script.py", "w", encoding="utf-8") as out:
                    out.write(code_section)
                print("Successfully wrote raw python code to raw_ocr_script.py!")
            else:
                print("Could not find start of code block.")
            break
