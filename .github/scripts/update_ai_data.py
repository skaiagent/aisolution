import os
import json
import time
import requests
import google.generativeai as genai
from tavily import TavilyClient

def update_data():
    tavily_key = os.environ.get("TAVILY_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if not tavily_key or not gemini_key:
        print("API Keys not found. Please set them in GitHub Secrets.")
        return

    # Initialize Clients
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    tavily = TavilyClient(api_key=tavily_key)

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Example: we will just update one primary trend model to save LLM tokens in the test
    # You can expand the loop to update the whole dataset by uncommenting/looping
    try:
        target = data["enterpriseTools"]["chatgpt"]
        query = f"Latest model version and release date for OpenAI ChatGPT Enterprise in 2026/2025"
        search_result = tavily.search(query=query)
        
        prompt = f"""
        당신은 AI 데이터베이스 관리자입니다. 
        아래 Tavily 검색 뉴스를 바탕으로 해당 AI 솔루션의 가장 최신 모델명, 최근 업데이트 항목을 추출하여 수정된 JSON 객체 1개만 반환하세요.
        마크다운 코드 블록(` ```json `)을 쓰지 말고 순수 중괄호 {{}} 로 시작하는 JSON 텍스트로만 반환하세요.
        
        [뉴스 검색 결과]:
        {search_result.get('results', [])}
        
        [수정해야 할 원본 데이터]:
        {json.dumps(target, ensure_ascii=False)}
        """
        
        response = model.generate_content(prompt)
        text_out = response.text.replace('```json', '').replace('```', '').strip()
        
        updated_item = json.loads(text_out)
        data["enterpriseTools"]["chatgpt"].update(updated_item)
        print("Successfully updated ChatGPT info via Tavily & Gemini!")

    except Exception as e:
        print("Update skipped or failed:", e)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    update_data()
