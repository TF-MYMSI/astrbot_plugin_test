from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import time

AGREEMENT_TEXT = """
星恒梦落用户使用协议

版本：v1.0
最后更新：2026年4月4日
联系方式：QQ群 752775661
本协议自2026年4月4日起正式生效

一、协议范围

星恒梦落机器人用户使用协议适用范围包括但不限于：QQ群聊、QQ私聊、任何通过本机器人进行的消息发送、工具调用等行为。

当你开始与本机器人对话，即视为你已阅读、理解并同意本协议的全部内容。

二、信息收集与使用规定

为保证机器人稳定运行与定期维护，我们会收集以下信息：用户信息（用户UID，即QQ号）、聊天信息（与本机器人进行的全部对话内容）、协议信息（关于本协议的同意或拒绝状态）。

我们承诺：不会向第三方提供任何用户的个人信息，除非法律要求；不会收集与本服务无关的任何个人信息。

三、用户行为规范规定

用户不得进行以下行为：利用本机器人进行任何形式的违法活动；发布、宣传诈骗、赌博、色情、暴力、诽谤、侵权等信息；恶意破坏机器人正常运行，如刷屏、攻击本机器人等；使用工具破解、逆向工程或以非正常方式调用本机器人。

若用户执行上述行为：本机器人会对用户进行警告、限制聊天、终止服务等措施；用户需对自身行为承担全部法律责任；如造成第三方损害，用户需自行承担赔偿等责任。

四、免责声明

本机器人不保证服务完全不中断、无错误或绝对安全。

本服务不对以下情况承担责任：因用户自身行为导致的任何损失；因网络故障、服务器维护、第三方服务中断等不可抗力导致的服务异常；用户因使用本机器人而产生的任何间接、附带、特殊损失。

若用户利用本机器人进行任何违法活动，将由用户自行承担全部后果，本机器人发布者不承担连带责任。

五、协议修改

本协议有权根据法律法规变化或服务需要进行修改。修改后的协议将在首次私聊或群聊中通知用户。

如用户继续使用本机器人，视为同意修改后的协议。如用户不同意修改，应立即停止使用。

六、未成年人保护

如你未满18周岁，请在法定监护人陪同下阅读本协议，在取得法定监护人的同意后，方可使用本机器人。

七、法律适用与争议解决

本协议的订立、执行和解释及争议的解决均适用中华人民共和国法律。

如发生争议，双方应友好协商解决；协商不成的，任何一方有权向本协议发布者所在地有管辖权的人民法院提起诉讼。

八、协议确认方式

回复「同意」视为用户已阅读、理解并同意本协议的全部内容，协议自本日起对你生效。

回复「不同意」将无法使用本机器人的全部功能。
"""

@register("agreement", "星恒梦落", "用户协议签订插件", "1.0.0")
class AgreementPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("协议签订插件已加载")

    async def on_message(self, event: AstrMessageEvent):
        # 只处理私聊消息
        if event.get_message_type() != "private":
            return
        
        uid = event.get_sender_id()
        status = await self.context.get("agreed_" + uid)
        
        # 情况1：用户从未签订协议
        if status is None:
            yield event.plain_result(AGREEMENT_TEXT)
            await self.context.set("agreed_" + uid, "waiting")
            await self.context.set("last_agreement_sent_" + uid, time.time())
            
            # 记录用户到统计列表
            user_list = await self.context.get("stat_user_list") or []
            if uid not in user_list:
                user_list.append(uid)
                await self.context.set("stat_user_list", user_list)
            
            # 更新总用户数统计
            total = await self.context.get("stat_total") or 0
            await self.context.set("stat_total", total + 1)
            return
        
        # 情况2：用户已收到协议，等待确认
        if status == "waiting":
            msg = event.message_str
            
            # 用户同意协议
            if "同意" in msg:
                await self.context.set("agreed_" + uid, "yes")
                yield event.plain_result("已记录你的同意。现在可以正常使用本机器人。")
                
                # 更新同意数统计
                agreed = await self.context.get("stat_agreed") or 0
                await self.context.set("stat_agreed", agreed + 1)
                return
            
            # 用户拒绝协议
            if "不同意" in msg:
                await self.context.set("agreed_" + uid, "no")
                yield event.plain_result("已记录你的拒绝。本机器人将无法为你服务。")
                
                # 更新拒绝数统计
                refused = await self.context.get("stat_refused") or 0
                await self.context.set("stat_refused", refused + 1)
                return
            
            # 用户回复其他内容，检查冷却
            last_sent = await self.context.get("last_agreement_sent_" + uid)
            now = time.time()
            cooldown_seconds = 30
            
            # 冷却期内只提示，不重新发送协议
            if last_sent and (now - last_sent) < cooldown_seconds:
                yield event.plain_result("请回复「同意」或「不同意」接受协议。")
                return
            
            # 冷却结束，重新发送完整协议
            await self.context.set("last_agreement_sent_" + uid, now)
            yield event.plain_result(AGREEMENT_TEXT)
            return
        
        # 情况3：用户已拒绝协议，不回复任何消息
        if status == "no":
            return
        
        # 情况4：用户已同意协议，正常放行（不拦截，继续执行其他插件或主程序）
        return

    # 统计命令：查看协议签订统计摘要
    @filter.command("agreement_stats")
    async def show_stats(self, event: AstrMessageEvent):
        """查看协议签订统计"""
        total = await self.context.get("stat_total") or 0
        agreed = await self.context.get("stat_agreed") or 0
        refused = await self.context.get("stat_refused") or 0
        waiting = total - agreed - refused
        
        # 计算同意率，避免除零错误
        if total > 0:
            rate = (agreed / total) * 100
            rate_text = f"{rate:.1f}%"
        else:
            rate_text = "0%"
        
        stats_text = f"协议签订统计\n总用户数：{total}\n已同意：{agreed}\n已拒绝：{refused}\n等待中：{waiting}\n同意率：{rate_text}"
        
        yield event.plain_result(stats_text)

    # 列表命令：查看详细用户列表（仅管理员可用）
    @filter.command("agreement_list")
    async def list_users(self, event: AstrMessageEvent):
        """查看已同意、已拒绝、等待中的用户列表（仅管理员）"""
        uid = event.get_sender_id()
        ADMIN_UID = "3384188179"
        
        # 权限检查
        if uid != ADMIN_UID:
            yield event.plain_result("只有管理员可以使用此命令。")
            return
        
        user_list = await self.context.get("stat_user_list") or []
        
        agreed_users = []
        refused_users = []
        waiting_users = []
        
        # 遍历所有用户，按状态分类
        for user_uid in user_list:
            status = await self.context.get("agreed_" + user_uid)
            if status == "yes":
                agreed_users.append(user_uid)
            elif status == "no":
                refused_users.append(user_uid)
            elif status == "waiting":
                waiting_users.append(user_uid)
        
        # 构建返回文本（限制显示数量，避免消息过长）
        max_display = 30
        result = "用户协议状态列表\n\n"
        
        result += f"已同意 ({len(agreed_users)}人)：\n"
        if agreed_users:
            result += "、".join(agreed_users[:max_display])
            if len(agreed_users) > max_display:
                result += f"\n... 共{len(agreed_users)}人"
        else:
            result += "无"
        
        result += f"\n\n已拒绝 ({len(refused_users)}人)：\n"
        if refused_users:
            result += "、".join(refused_users[:max_display])
            if len(refused_users) > max_display:
                result += f"\n... 共{len(refused_users)}人"
        else:
            result += "无"
        
        result += f"\n\n等待中 ({len(waiting_users)}人)：\n"
        if waiting_users:
            result += "、".join(waiting_users[:max_display])
            if len(waiting_users) > max_display:
                result += f"\n... 共{len(waiting_users)}人"
        else:
            result += "无"
        
        yield event.plain_result(result)

    # 重置命令：重置所有统计数据（仅管理员可用）
    @filter.command("agreement_reset")
    async def reset_stats(self, event: AstrMessageEvent):
        """重置统计数据（仅管理员）"""
        uid = event.get_sender_id()
        ADMIN_UID = "3384188179"
        
        # 权限检查
        if uid != ADMIN_UID:
            yield event.plain_result("只有管理员可以使用此命令。")
            return
        
        # 重置所有统计键值
        await self.context.set("stat_total", 0)
        await self.context.set("stat_agreed", 0)
        await self.context.set("stat_refused", 0)
        await self.context.set("stat_user_list", [])
        
        yield event.plain_result("统计数据已重置。")

    async def terminate(self):
        """插件被卸载时调用"""
        logger.info("协议签订插件已卸载")
