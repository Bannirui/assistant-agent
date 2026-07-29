from functools import wraps


class ToolRegistry:
    r"""
    策略模式的注册中心
    负责注册和分发
    有新的工具要添加就用注解加到这个注册中心
    """

    def __init__(self):
        # 缓存策略实现
        self._handlers: dict[str, callable] = {}

    def register(self, name: str, handler: callable) -> None:
        r"""
        负责注册中心的注册
        :param name: 函数名
        :param handler: 对应的函数实现
        """
        # 放到缓存
        self._handlers[name] = handler

    def execute(self, name: str, *, arguments: dict) -> str:
        r"""
        负责注册中心的分发
        :param name: 函数名
        :param arguments: 函数执行需要的实参
        :return: 函数的执行结果 为了统一 不同的函数执行结果都被转成了字符串
        """
        # 从注册中心找到具体的实现
        handler = self._handlers.get(name)
        if handler is None:
            return f"未知工具: {name}"
        # 函数执行
        return handler(arguments)


tool_registry = ToolRegistry()


def use_tool(registry: ToolRegistry | None = None, name: str | None = None):
    r"""
    定义注解 新增工具的时候用策略模式注册分发
    :param registry: 注册中心 不传用默认实例
    :param name: 工具名称 不传则自动从函数名推导 去掉下划线前缀
    """
    if registry is None:
        registry = tool_registry

    def decorator(fn):
        tool_name = name if name is not None else fn.__name__.lstrip("_")

        @wraps(fn)
        def wrapper(arguments: dict) -> str:
            return fn(arguments)

        # 注册到注册中心
        registry.register(tool_name, wrapper)
        return wrapper

    return decorator
