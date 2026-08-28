"""查询阿里云专属实例上可用的模型列表"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 从环境变量读取阿里云 API Key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://llm-3vmkxv1h86lq5z6r.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)

try:
    resp = client.models.list()
    print("=" * 60)
    print("该实例上可用的模型列表：")
    print("=" * 60)
    for m in resp.data:
        print(f"  ID: {m.id}")
    print("=" * 60)
    print(f"共 {len(resp.data)} 个模型")
    print()
    print("找到名字带 embedding 的，就是向量模型，把名字告诉我即可。")
except Exception as e:
    print(f"查询失败: {e}")
