# from asyncio import Lock

from nonebot.log import logger
from nonebot.plugin import on_request, on_command
from nonebot.adapters.onebot.v11 import GroupRequestEvent, GroupMessageEvent
from nonebot.adapters import Bot
from nonebot.permission import SUPERUSER
from nonebot_plugin_uninfo.permission import ADMIN

from ..config import ConfigCTX
from ..model.config import refuseAddGroupRequestdetailConfig

async def is_start_refuse(event: GroupRequestEvent) -> bool:
    config = ConfigCTX.get()
    if not config.refuse.group_id.get(str(event.group_id), None): 
        return False
        # config.refuse.group_id[str(event.group_id)] = refuseAddGroupRequestdetailConfig(
        #     group_id=str(event.group_id))
        # ConfigCTX.set()
    return config.refuse.group_id[str(event.group_id)].refuse_group_request

add_group_request = on_request(
    priority=10,
    block=True,
    rule=is_start_refuse,
)

start_refuse = on_command(
    "开启自动拒绝加群请求",
    priority=10,
    block=True,
    permission=SUPERUSER | ADMIN(),
    # rule = is_start_refuse
)

stop_refuse = on_command(
    "关闭自动拒绝加群请求",
    priority=10,
    block=True,
    permission=SUPERUSER | ADMIN(),
    # rule = is_start_refuse
)

@add_group_request.handle()
async def _add_group_request(bot: Bot, event: GroupRequestEvent):
    logger.info("add_group_request")
    logger.info(f"event: {event}")
    request_user_id = event.get_user_id()
    stranger_info = await bot.call_api("get_stranger_info", user_id = int(request_user_id))
    logger.info(f"stranger_info: {stranger_info}")
    level = stranger_info.get("level")
    logger.info(f"level: {level}")
    config = ConfigCTX.get()
    if level and config.refuse.group_id[str(event.group_id)].refuse_level >= level:
        await add_group_request.finish(f"{request_user_id}的等级{level}小于等于{config.refuse.group_id[str(event.group_id)].refuse_level}，拒绝加群请求")
    await add_group_request.finish(f"检测到{request_user_id}的加群请求，请处理")
    
@start_refuse.handle()
async def _start_refuse(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    config = ConfigCTX.get()
    if not config.refuse.group_id.get(str(group_id), None):
        config.refuse.group_id[str(group_id)].group_id = str(group_id)
        # ConfigCTX.set()
    if config.refuse.group_id[str(group_id)].refuse_group_request:
        await start_refuse.finish("已开启自动拒绝加群请求")
    config.refuse.group_id[str(group_id)].refuse_group_request = True
    ConfigCTX.set()
    await start_refuse.finish("已开启自动拒绝加群请求")

@stop_refuse.handle()
async def _stop_refuse(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    config = ConfigCTX.get()
    if not config.refuse.group_id.get(str(group_id), None):
        config.refuse.group_id[str(group_id)].group_id = str(group_id)
        ConfigCTX.set()
        await stop_refuse.finish("该群未开启自动拒绝加群请求")
    if config.refuse.group_id[str(group_id)].refuse_group_request:
        await start_refuse.finish("已关闭自动拒绝加群请求")
    