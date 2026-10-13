# app/middleware/routerLogger.py

# 标准库日志模块，用于输出日志
import logging

# Starlette 提供的基于 HTTP 的中间件基类，继承它并实现 dispatch 即可
from starlette.middleware.base import BaseHTTPMiddleware

# 创建本模块专用的 logger，名字叫 "app.route"，方便按模块过滤/配置日志
logger = logging.getLogger("app.route")


# 自定义中间件：记录每个请求最终命中的路由和 endpoint
class RouteLoggerMiddleware(BaseHTTPMiddleware):
    # dispatch 是 BaseHTTPMiddleware 的核心方法，每个请求都会走这里
    async def dispatch(self, request, call_next):
        # 把请求交给后续处理链（路由匹配、依赖注入、接口函数、异常处理等），
        # 返回最终的 Response。注意：只有执行完这句，request.scope 里才会有路由信息
        response = await call_next(request)

        # 从 request.scope 取出"路由匹配结果"。
        # 路由匹配成功后，Starlette 会把命中的 Route 对象放进 scope["route"]；
        # 若没匹配到（404），这里是 None
        route = request.scope.get("route")

        # 取出该路由对应的 endpoint（即被调用的那个函数对象）。
        # route 为 None 时，getattr 返回 None，不会报错
        endpoint = getattr(route, "endpoint", None)

        # 取出路由的"路径模板"，例如 "/user/{id}"、"/user/list"。
        # 这是注册时写的原始路径，不是实际请求路径
        path_format = getattr(route, "path", None)
        # 打印一条日志，记录：请求方法、实际请求路径、命中的路由模板、
        # endpoint 函数名、响应状态码。
        # endpoint 的 __name__ 是函数名（如 get_user）；
        # 如果 endpoint 是 None，则直接打印 endpoint 本身（None）
        logger.info(
            "method=%s path=%s -> route=%s endpoint=%s status=%s",
            request.method,
            request.url.path,
            path_format,
            getattr(endpoint, "__name__", endpoint),
            response.status_code,
        )

        # 返回响应，交给上层继续处理（如响应包装中间件、发送给客户端）
        return response