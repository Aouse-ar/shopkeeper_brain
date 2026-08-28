import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from typing import Dict, Any, List, Tuple, Union
import httpx2
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
from langchain_core.messages import SystemMessage, HumanMessage
from knowledge.processor.query_process.state import QueryGraphState
from knowledge.processor.query_process.base import BaseNode, T
from knowledge.processor.query_process.exceptions import StateFieldError


class McpSearchNode(BaseNode):
    name = "mcp_search_node"
    """
     负责从网络查询当前的问题【整个知识库没有找到该问题，兜底的网络结果】
     mcp形式调用第三方的各种通用的搜索工具。
     百度：【电商】商品比价工具、商品搜索的工具、商品全维度对比工具、商品下单的工具 百度搜索工具 百度地图的工具..
     灵积服务平台:的通用搜索工具【bailian_web_search】
     mcp: 本质：就是各大平台把通用的功能，封装成了工具（函数） 然后通过mcp协议 客户端就可以直接调用它。【mcp客户端】---->【mcp服务端：任意选择某一个】

    """

    def process(self, state: QueryGraphState) -> Union[QueryGraphState, Dict[str, Any]]:

        # 1. 参数校验
        validated_rewritten_query, validated_item_names = self._validate_query_inputs(state)

        # 2. 创建mcp_client 并且让客户端执行工具  bailian_web_search
        mcp_result = asyncio.run(self._create_execute_web_search(validated_rewritten_query))

        if not mcp_result:
            return state

        # 3. 只更新state的web_search_docs
        return {"web_search_docs": mcp_result}

    def _validate_query_inputs(self, state: QueryGraphState) -> Tuple[str, List[str]]:

        # 1. 获取state的rewritten_query
        rewritten_query = state.get('rewritten_query', "")

        # 2. 获取state的item_names
        item_names = state.get('item_names', "")

        # 3. 校验
        if not rewritten_query or not isinstance(rewritten_query, str):
            raise StateFieldError(node_name=self.name, field_name="rewritten_query", expected_type=str)

        if not item_names or not isinstance(item_names, list):
            raise StateFieldError(node_name=self.name, field_name="item_names", expected_type=list)

        # 4. 返回
        return rewritten_query, item_names

    async def _create_execute_web_search(self, validated_rewritten_query: str) -> List[Dict[str, Any]]:

        mcp_url = self.config.mcp_dashscope_base_url
        headers = {"Authorization": f"Bearer {self.config.dashscope_api_key}"}

        try:
            http_client = httpx2.AsyncClient(headers=headers)
            async with streamable_http_client(mcp_url, http_client=http_client) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    execute_tool_result = await session.call_tool(
                        "bailian_web_search",
                        arguments={"query": validated_rewritten_query, "count": 3}
                    )

                    if not execute_tool_result or not execute_tool_result.content:
                        return []

                    text_content_text = execute_tool_result.content[0].text
                    if not text_content_text:
                        return []

                    try:
                        parsed = json.loads(text_content_text)
                        pages = parsed.get('pages', [])
                        if not pages:
                            return []
                        search_result = []
                        for page in pages:
                            snippet = page.get('snippet', "").strip()
                            title = page.get('title', "").strip()
                            url = page.get('url', "").strip()
                            search_result.append({"snippet": snippet, "title": title, "url": url})
                        return search_result
                    except Exception as e:
                        self.logger.error(f"反序列化MCP结果失败: {e}")
                        return []
        except Exception as e:
            self.logger.error(f"MCP连接或调用失败: {e}")
            return []


if __name__ == '__main__':
    state = {
        "rewritten_query": "今天北京天气怎么样，并且告诉我今天具体的日期是什么时候",
        "item_names": ["RS PRO RS-12 数字万用表"]
    }

    mcp_search = McpSearchNode()

    result = mcp_search.process(state)

    web_docs = result.get('web_search_docs')
    if not web_docs:
        print("未检索到网络搜索结果")
    else:
        for r in web_docs:
            print(json.dumps(r, ensure_ascii=False, indent=2))
