from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

AGREEMENT_TEXT = """《星恒梦落用户使用协议》v1.0

一、协议范围
本协议适用于：QQ群聊、QQ私聊、任何通过本机器人进行的消息发送、工具调用等行为。

二、信息收集与使用
我们会收集：用户QQ号、聊天内容、协议同意状态。我们承诺不向第三方提供你的个人信息。

三、用户行为规范
禁止：违法活动；发布诈骗、赌博、色情、暴力等信息；恶意刷屏、攻击机器人。

四、免责声明
本机器人不保证服务完全无中断。用户违法操作后果自负。

五、确认方式
回复「同意」视为同意本协议。回复「不同意」将无法使用本机器人。"""

@register("agreement", "星恒梦落", "用户协议签订插件", "1.0.0")
class AgreementPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("协议签订插件已加载")

    @filter.on_message()
    async def on_private_message(self, event: AstrMessageEvent):
        if event.get_message_type() != "private":
            return
        
        uid = event.get_sender_id()
        status = await self.context.get("agreed_" + uid)
        
        if status is None:
            yield event.plain_result(AGREEMENT_TEXT)
            await self.context.set("agreed_" + uid, "waiting")
            return
        
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
            return
        
        if status == "no":
            return

    async def terminate(self):
        pass
