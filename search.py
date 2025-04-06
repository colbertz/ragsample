import meilisearch
import sys
import json
import dashscope
from http import HTTPStatus
import requests

def print_rerank_results(reranked_results):
    if reranked_results:
        print("重排结果：")
        for i, result in enumerate(reranked_results):
            print(f"{i+1}. 相关性分数: {result['relevance_score']:.4f}")
            print(f"{i+1}. 原index: {result['index']}")
            print(f"   文档内容: {result['document']['text']}\n")

def search_in_meili(question):
    client = meilisearch.Client('http://localhost:7700', 'rmuds5OuiWit9ccjQdTnjOUG3zvKi-ayIwunj3R0ums')
    search_results = client.index('Buddhism').search(question, {'limit': 20})
    return search_results

def rerank_results(question, search_results):
    """
    使用gte-rerank模型对文档进行相关性重排
    :param query: 查询文本
    :param documents: 待排序的文档列表
    :return: 排序后的结果
    """
    documents = [hit['content'] for hit in search_results['hits']]
    dashscope.api_key = 'sk-...'
    resp = dashscope.TextReRank.call(
        model=dashscope.TextReRank.Models.gte_rerank,
        query=question,
        documents=documents,
        top_n=7,  # 返回前N个结果
        return_documents=True  # 返回包含原文的结果
    )
    
    if resp.status_code == HTTPStatus.OK:
        json_res = json.dumps(resp.output.results, indent=2, ensure_ascii=False)
        return json_res
    else:
        print(f'Request failed: {resp.code} - {resp.message}')
        return None

def ask_deepseek(question, search_results):
    knowledge = [result['document']['text'] for result in search_results]
    prompt = f'''你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。
        当所有知识库内容都与问题无关时，你的回答必须包括“知识库中未找到您要的答案！”这句话。
        以下是知识库：
        {knowledge}
        以上是知识库。
        
        问题：{question}'''

    try:
        api_url = "https://api.deepseek.com/v1/chat/completions"
        api_key = "sk-..."
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的知识库问答助手"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 5000,
            "stream": True
        }
        
        with requests.post(api_url, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            print("DeepSeek回答:\n", end="", flush=True)
            for chunk in response.iter_lines(decode_unicode=True):
                if chunk.startswith("data: "):
                    chunk = chunk[6:]
                try:
                    data = json.loads(chunk)
                    if "choices" in data and data["choices"]:
                        token = data["choices"][0]["delta"].get("content", "")
                        print(token, end="", flush=True)
                except json.JSONDecodeError:
                    continue
            print()

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python search.py <question>")
        sys.exit(1)

    question = sys.argv[1]
    
    # Perform the search in MeiliSearch
    search_results = search_in_meili(question)
    reranked_results = json.loads(rerank_results(question, search_results))  
    # debug reranked_results
    # print_rerank_results(reranked_results)

    ask_deepseek(question, reranked_results)

if __name__ == "__main__":
    main()