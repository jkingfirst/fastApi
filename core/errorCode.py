from enum import Enum
from typing import Optional

class ErrorCode(Enum):
    """
    统一错误码枚举
    格式： (业务错误码, 错误信息, HTTP状态码)
    """
    # ---------- 通用成功 ----------
    SUCCESS = (200, "成功", 200)

    # ---------- 客户端错误 4xx ----------
    PARAM_ERROR = (40000, "请求参数错误", 422)
    UNAUTHORIZED = (40100, "未认证", 401)
    TOKEN_EXPIRES = (40200, "认证已过期", 401)
    FORBIDDEN = (40300, "无权限访问", 403)
    NOT_FOUND = (40400, "请求的资源不存在", 404)
    METHOD_NOT_ALLOWED = (40500, "请求方法不允许", 405)
    REQUEST_TIMEOUT = (40800, "请求超时", 408)
    CONFLICT = (40900, "资源冲突", 409)
    PAYLOAD_TOO_LARGE = (41300, "请求体过大", 413)
    UNSUPPORTED_MEDIA_TYPE = (41500, "不支持的媒体类型", 415)
    TOO_MANY_REQUESTS = (42900, "请求过于频繁，请稍后重试", 429)

    # ---------- 服务端错误 5xx ----------
    INTERNAL_SERVER_ERROR = (50000, "服务器内部错误", 500)
    NOT_IMPLEMENTED = (50100, "功能未实现", 501)
    SERVICE_UNAVAILABLE = (50300, "服务暂时不可用", 503)
    GATEWAY_TIMEOUT = (50400, "网关超时", 504)

    # ---------- 业务错误码（按模块划分） ----------
    # 用户模块 2xxxx
    USER_NOT_FOUND = (20001, "用户不存在", 404)
    PASSWORD_ERROR = (20002, "密码错误", 400)
    USER_ALREADY_EXISTS = (20003, "用户已存在", 409)
    USER_DISABLED = (20004, "用户已被禁用", 403)
    TOKEN_INVALID = (20005, "Token 无效", 401)

    # 订单模块 3xxxx
    ORDER_NOT_FOUND = (30001, "订单不存在", 404)
    ORDER_STATUS_ERROR = (30002, "订单状态不允许此操作", 400)
    ORDER_ALREADY_PAID = (30003, "订单已支付", 409)

    # 商品模块 4xxxx
    PRODUCT_NOT_FOUND = (40001, "商品不存在", 404)
    PRODUCT_STOCK_INSUFFICIENT = (40002, "商品库存不足", 400)
    PRODUCT_OFF_SHELF = (40003, "商品已下架", 400)

    # 支付模块 9xxxx
    PAYMENT_FAILED = (90001, "支付失败", 400)
    REFUND_FAILED = (90002, "退款失败", 400)

    def __init__(self, code: int, message: str, http_status: int):
        self.code = code
        self.message = message
        self.http_status = http_status

    @classmethod
    def from_code(cls, code: int) -> Optional["ErrorCode"]:
        for item in cls:
            if item.code == code:
                return item
        return None