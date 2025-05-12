import asyncio, os
from json import dumps, loads
from aiogram import Bot
from aiogram.types import Gifts
from github import Github, Auth
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def download_gifts(
        bot: Bot
):
    auth = Auth.Token("github_token")
    g = Github(auth=auth)

    repo = g.get_repo("DevMti/gift-catalog")
    images = repo.get_contents("/images")
    files = []
    for image in images:
        files.append(image.path.split("/")[-1])
    data = []

    available_gifts: Gifts = await bot.get_available_gifts()
    for gift in available_gifts.gifts:
        if gift.total_count != None: limited = True
        else: limited = False
        data.append({
            "id": gift.id,
            "price": round(gift.star_count * 3),
            "is_limited_edition": limited
        })
        if gift.id + ".tgs" not in files:
            file_name = f"{gift.id}.tgs"
            await bot.download(
                file=gift.sticker.file_id,
                destination=f"images/{file_name}",
            ) 
            print("new gift")
            with open(f"images/{file_name}", "rb") as f:
                repo.create_file("images/" + file_name, "gift image", f.read(), branch="main")

    contents = repo.get_contents("data.json", ref="main")
    if loads(contents.decoded_content.decode('utf-8')) != data:
        repo.update_file(contents.path, "gifts list", dumps(data, indent=4), contents.sha, branch="main")
    
    g.close()

async def main():
    async with Bot(token="bot_token") as bot:
        await download_gifts(bot)


async def setup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, 'interval', minutes=5)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    while True:
        await asyncio.sleep(1000)


if __name__ == '__main__':
    asyncio.run(setup())
