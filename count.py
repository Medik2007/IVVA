from pathlib import Path
import json

AI_DIR = "ai"
RAW_DIR = "vk"


CATEGORIES = [
    "Прямая вербовка",
    "Символическая поддержка СВО",
    "Милитаризация образования",
    "Волонтёрство и материальная поддержка",
]

i = 1
for file in Path(AI_DIR).glob("*.json"):
    with file.open("r") as f:
        data = json.load(f)

    with open(f"{RAW_DIR}/{file.name}", "r") as f:
        total_post_count = len(json.load(f))

    posts = data["posts"]
    file_cats = {c: 0 for c in CATEGORIES}

    for post in posts:
        for cat in CATEGORIES:
            if cat.lower() in post["output"].lower():
                file_cats[cat] += 1

    total_categorized = sum([v for v in file_cats.values()])
    categorized_percent = total_categorized / total_post_count * 100
    print(f"{i}. {data['name']}\n")
    print(
        f"Общее количество постов: {total_post_count}\nКоличество категоризированных постов: {total_categorized} ({categorized_percent:.2f}%)\n"
    )
    for k, v in file_cats.items():
        percent = v / total_categorized * 100
        print(f"{k}: {v} ({percent:.2f}%)")

    print("\n")
    i += 1
