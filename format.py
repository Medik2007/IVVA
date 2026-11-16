from pathlib import Path
import vk_api
import json
import os

from dotenv import load_dotenv

load_dotenv()

LOAD_DIR = "vk"
SAVE_DIR = "raw"
VK_TOKEN = os.environ["VK_TOKEN"]
DEBUG = False

os.makedirs(SAVE_DIR, exist_ok=True)

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

data = []

for file in Path(LOAD_DIR).glob("*.json"):
    if file.name in ["kursk_gau.json", "kursksu.json"]:
        with file.open("r") as f:
            data.append(json.load(f))

with open("keywords.txt", "r") as file:
    keywords = set([c for c in file.read().splitlines() if c.strip()])


i = 0
for file in data:
    if len(file) == 0:
        continue

    id = str(file[0]["owner_id"])
    name = ""
    tag = str(i)
    i += 1

    if not DEBUG:
        if id.startswith("-"):
            response = vk.groups.getById(group_id=id[1:])
            name = response[0]["name"]
            tag = response[0]["screen_name"]
        else:
            response = vk.users.get(user_ids=id)
            name = response[0]["first_name"] + " " + response[0]["last_name"]
            tag = str(id)

    result = {
        "name": name,
        "tag": tag,
    }

    posts = []

    for post in file:
        text = post["text"]
        if post["text"] == "":
            continue

        post_categories = []

        table = str.maketrans({",": " ", ";": " ", "|": " ", "\n": " ", ".": " "})
        word_list = text.translate(table).lower().split()
        word_set = set(word_list)

        if not word_set.isdisjoint(keywords):
            posts.append(text)

    result["posts"] = posts

    with open(f"{SAVE_DIR}/{tag}.json", "w") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    # break
