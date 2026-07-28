import uvicorn
from .config import settings

if __name__ == "__main__":
    # ASGI服务器把请求转发给对应的FastAPI
    uvicorn.run(
        # 转发给哪个文件的哪个对象处理其功能求
        "src.main:app",
        # 监听的地址
        host=settings.copilot_host,
        # 监听的端口
        port=settings.copilot_port,
        # 开发环境自动重启 生产环境关闭
        reload=settings.copilot_env == "development",
    )