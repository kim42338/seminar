import asyncio, discord
import re
from discord.ext import commands

from hungryapp import get_latest_post


token = 'ODY1NTQ2MzgxNDEzOTc0MDM2.YPFk4g.8fv3jZnR88SIPWcTsEX2l70CtPg'
channel_id = 865546111682215979
retired_id = 865933971229900801
client = discord.Client()


async def my_background_task():
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    retired_channel = client.get_channel(retired_id)
    uuids = []
    while True:
        try:
            latest_post = get_latest_post('honkai3rd')
        except Exception as e:
            print(F'Failed to get the latest post, {e}')
            continue
        if latest_post.uuid in uuids:
            continue
        else:
            print(F'Latest post {latest_post.uuid} detected')
            if '은퇴' in latest_post.title or '진행' in latest_post.title:
                print(F'은퇴 or 진행 detected in "{latest_post.title}"')
                await retired_channel.send('@everyone')
                await retired_channel.send(embed=latest_post.embed)
            else:
                await channel.send('@everyone')
                await channel.send(embed=latest_post.embed)
            uuids.append(latest_post.uuid)
        await asyncio.sleep(1)


client.loop.create_task(my_background_task())
client.run('ODY1NTQ2MzgxNDEzOTc0MDM2.YPFk4g.8fv3jZnR88SIPWcTsEX2l70CtPg')
