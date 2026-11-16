import os
import json
import time
import requests

import vk_api
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

API_TOKEN = os.environ["VK_TOKEN"]

START_DATE = datetime(2025, 9, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 9, 1, tzinfo=timezone.utc)

with open("vk_list.txt", "r", encoding="utf-8") as file:
    CHANNELS = [c for c in file.read().splitlines() if c.strip()]

os.makedirs("vk", exist_ok=True)


vk_session = vk_api.VkApi(token=API_TOKEN)
vk = vk_session.get_api()


def main(owner_id, owner_name):
    posts = []
    offset = 0

    try:
        while True:
            time.sleep(0.5)
            step = 50
            response = vk.wall.get(
                owner_id=owner_id,
                count=step,
                offset=offset,
            )
            offset += step
            finish = False

            if len(response["items"]) < step:
                finish = True

            for post in response["items"]:

                post_date = datetime.fromtimestamp(
                    post["date"],
                    tz=timezone.utc,
                )

                if post_date > END_DATE:
                    print("skipped")
                    continue

                if post_date < START_DATE:
                    finish = True
                    break

                post["date"] = post_date
                posts.append(post)
                print(f"""
Message loaded
Data: {post['date']}
Id: {post['id']}
Channel: {channel_name}

                """)

            if finish:
                break
    finally:
        with open(f"vk/{owner_name}.json", "w", encoding="utf-8") as f:
            json.dump(
                posts,
                f,
                ensure_ascii=False,
                indent=4,
                default=str,
            )

        print(f"{channel_name}: saved {len(posts)} posts")


if __name__ == "__main__":
    for c in CHANNELS:
        time.sleep(0.5)
        channel_name = c.rstrip("/").split("/")[-1]
        id = requests.get(
            "https://api.vk.com/method/utils.resolveScreenName",
            params={
                "access_token": API_TOKEN,
                "screen_name": channel_name,
                "v": "5.199",
            },
        ).json()["response"]["object_id"]
        id = str(id)
        if not channel_name.startswith("id"):
            id = f"-{id}"
        print(f"Starting {channel_name}: {id}")
        main(id, channel_name)
