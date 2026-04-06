from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register(
    "astrbot_plugin_test",
    "测试",
    "测试插件，用于检测插件加载和消息触发",
    "1.0.0"
)
class TestPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("测试插件已加载 - 加载成功")

    async def on_message(self, event: AstrMessageEvent):
        # 收到任何消息都输出日志并回复
        logger.info(f"测试插件收到消息: {event.message_str}")
        logger.info(f"消息类型: {event.get_message_type()}")
        logger.info(f"发送者: {event.get_sender_id()}")
        
        # 回复测试消息
        yield event.plain_result(f"测试插件收到: {event.message_str}")
        event.stop_event()

    async def terminate(self):
        logger.info("测试插件已终止")
