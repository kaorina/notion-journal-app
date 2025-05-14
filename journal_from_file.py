import os
import requests
from dotenv import load_dotenv
from datetime import date

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_journal_entry(title: str, content: str):
    url = "https://api.notion.com/v1/pages"

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "Date": {
                "date": {"start": str(date.today())}
            },
            "Content": {
                "rich_text": [{"text": {"content": content}}]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content}
                    }]
                }
            }
        ]
    }

    res = requests.post(url, headers=headers, json=data)
    if res.status_code in [200, 201]:
        print("✅ Journal entry created!")
    else:
        print(f"❌ Error: {res.status_code}")
        print(res.text)

def read_journal_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 1行目はタイトル（"Title: xxxx" の形式）
    if lines and lines[0].startswith("Title:"):
        title = lines[0].replace("Title:", "").strip()
        content = "".join(lines[1:]).strip()
        return title, content
    else:
        raise ValueError("1行目に 'Title: xxx' の形式でタイトルを指定してください")

# 実行部分
if __name__ == "__main__":
    file_path = "journal.txt"
    try:
        title, content = read_journal_from_file(file_path)
        create_journal_entry(title, content)
    except Exception as e:
        print(f"⚠️ Error: {e}")
