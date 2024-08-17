import httpx

async def get_session():
    return httpx.AsyncClient(headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    })


# 使用示例
# async def fetch(url):
#     async with get_session() as session:
#         async with session.get(url) as response:
#             return await response.text()
