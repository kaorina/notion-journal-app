import streamlit as st
import os
import requests
from openai import OpenAI
from datetime import date
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def improve_english_journal_with_explanation(text: str) -> tuple[str, str]:
    prompt = f"""あなたは英語教師です。
以下の英語日記を、より自然な英語になるように添削してください。
その後、どのような点を修正したのかを、日本語で簡単に解説してください。

【日記】
{text}

以下のフォーマットで返してください：

【添削後】
<添削した文章>

【解説】
<修正ポイントの日本語解説>
"""

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    full_reply = response.choices[0].message.content.strip()

    # 添削後と解説の部分を取り出す
    import re
    revised_match = re.search(r"【添削後】\s*(.*?)\s*【解説】", full_reply, re.DOTALL)
    explanation_match = re.search(r"【解説】\s*(.*)", full_reply, re.DOTALL)

    revised = revised_match.group(1).strip() if revised_match else ""
    explanation = explanation_match.group(1).strip() if explanation_match else "（解説の取得に失敗しました）"

    return revised, explanation

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
    return res.status_code in [200, 201]

# ====================
# Streamlit UI
# ====================

st.title("📘 My Notion Journal")

with st.form("journal_form"):
    title = st.text_input("Title", value=str(date.today()))
    content = st.text_area("Your Journal", height=250)

    col1, col2 = st.columns(2)
    summit = st.form_submit_button("✍️ 投稿のみ")
    revise_and_summit = st.form_submit_button("✨ 添削して投稿")

    if summit:
        if content.strip() == "":
            st.error("Content cannot be empty.")
        else:
            success = create_journal_entry(title, content)
            if success:
                st.success("✅ Journal entry created!") 
            else:
                st.error("❌ Error creating journal entry.")

    if revise_and_summit:
        if content.strip() == "":
            st.error("Content cannot be empty.")
        else:
            # メッセージ表示用のプレースホルダーを用意
            status_placeholder = st.empty()
            status_placeholder.info("✏️ 添削中...")

            revised, explanation = improve_english_journal_with_explanation(content)
            success = create_journal_entry(title, revised)

            # プレースホルダーをクリアして、infoを非表示に
            status_placeholder.empty()

            if success:
                st.success("✅ 添削して投稿しました！")
                st.markdown("### ✨ 添削後の内容")
                st.code(revised, language="markdown")
                st.markdown("### 💡 添削ポイントの解説（日本語）")
                st.info(explanation)
                st.balloons()
            else:
                st.error("❌ 添削後の投稿に失敗しました。")
                