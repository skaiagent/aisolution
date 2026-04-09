import os
import json
import time
import requests
import google.generativeai as genai
from tavily import TavilyClient

def check_link_health(url):
    """
    URL의 상태 코드를 확인합니다.
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

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

    # 1. 최신 트렌드 업데이트 (최근 팩트 기반)
    try:
        target = data["enterpriseTools"]["chatgpt"]
        query = "Latest pricing and model version for ChatGPT Enterprise April 2026"
        search_result = tavily.search(query=query)
        
        prompt = f"""
        당신은 AI 데이터베이스 관리자입니다. 
        아래 Tavily 검색 뉴스를 바탕으로 해당 AI 솔루션의 가장 최신 모델명, 최근 업데이트 내용(update), 그리고 그 정보를 추출해낸 핵심 출처 웹페이지 링크(source_url)를 찾아 수정된 JSON 객체 1개만 반환하세요.
        특히 2026년 4월 도입된 Codex Seat 요금제($20~$25) 정보를 우선 반영하세요.
        
        [뉴스 검색 결과]:
        {search_result.get('results', [])}
        
        [원본 데이터]:
        {json.dumps(target, ensure_ascii=False)}
        """
        
        response = model.generate_content(prompt)
        text_out = response.text.replace('```json', '').replace('```', '').strip()
        updated_item = json.loads(text_out)
        data["enterpriseTools"]["chatgpt"].update(updated_item)
        print("Successfully updated ChatGPT via AI Search.")

    except Exception as e:
        print("AI Update skipped or failed:", e)

    # 2. 링크 상태 전수 점검 (신뢰성 검증)
    print("Starting source link health check...")
    def validate_sources(items):
        source_list = items if isinstance(items, list) else items.values()
        for item in source_list:
            if "sources" in item:
                for key, url in item["sources"].items():
                    if not check_link_health(url):
                        print(f"[Warning] Broken Link Found: {item.get('name')} -> {url}")

    validate_sources(data["enterpriseTools"])
    validate_sources(data["minutesData"])
    validate_sources(data["builderData"])
    validate_sources(data["reportSlideData"])

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    update_data()
