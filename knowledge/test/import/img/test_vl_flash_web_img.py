import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 1. 初始化OpenAI客户端（DeepSeek）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1")
)

# 2. 创建聊天完成请求（支持图片URL + 文字）
completion = client.chat.completions.create(
    model="deepseek-v4-flash-vision-exp",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg"
                    },
                },
                {
                    "type": "text",
                    "text": "这道题怎么解答？"
                },
            ],
        },
    ],
)

answer = completion.choices[0].message.content
print(answer)