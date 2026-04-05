from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

AGREEMENT_TEXT = """
星恒梦落用户使用协议
版本：v1.0
...

回复「同意」视为同意本协议。回复「不同意」将无法使用本机器人。
"""

@register("agreement", "星恒梦落", "用户协议签订插件", "1.0.0")
class AgreementPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("协议签订插件初始化成功")

    @filter.regex(r".*")  # 匹配所有消息
    async def handle_message(self, event: AstrMessageEvent):
        """处理所有消息"""
        # 只处理私聊
        if event.get_message_type() != "private":
            return
        
        uid = event.get_sender_id()
        status = await self.context.get("agreed_" + uid)
        
        # 未签协议
        if status is None:
            yield event.plain_result(AGREEMENT_TEXT)
            await self.context.set("agreed_" + uid, "waiting")
            event.stop_event()  # 阻止其他插件处理
            return
        
        # 等待确认
        if status == "waiting":
            msg = event.message_str
            if "同意" in msg:
                await self.context.set("agreed_" + uid, "yes")
                yield event.plain_result("已记录你的同意。现在可以正常使用。")
            elif "不同意" in msg:
                await self.context.set("agreed_" + uid, "no")
                yield event.plain_result("已记录你的拒绝。本机器人将无法为你服务。")
            else:
                yield event.plain_result("请回复「同意」或「不同意」。")
            event.stop_event()
            return
        
        # 已拒绝，不回复并阻止
        if status == "no":
            event.stop_event()
            return

    async def terminate(self):
        logger.info("协议签订插件已终止")
