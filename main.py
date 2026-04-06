from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("test_qq", "测试", "QQ平台测试", "1.0.0")
class TestQQPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("QQ测试插件已加载")

    async def on_message(self, event: AstrMessageEvent):
        logger.info(f"QQ测试插件收到消息")
        logger.info(f"平台: {event.get_platform_name()}")
        logger.info(f"消息类型: {event.get_message_type()}")
        logger.info(f"内容: {event.message_str}")
        logger.info(f"发送者: {event.get_sender_id()}")
        # 回复一条测试消息
        yield event.plain_result(f"收到消息: {event.message_str}")
        event.stop_event()

    async def terminate(self):
        pass
