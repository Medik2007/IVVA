from llama_cpp import Llama
from pathlib import Path
import json, os

MODEL_REPO = "Qwen/Qwen3-8B-GGUF"
MODEL_FILE = "Qwen3-8B-Q4_K_M.gguf"

RAW_DIR = "raw"
SAVE_DIR = "ai"
PROMPT_FILE = "prompt.txt"

os.makedirs(SAVE_DIR, exist_ok=True)

data = []
for file in Path(RAW_DIR).glob("*.json"):
    with file.open("r") as f:
        data.append(json.load(f))

with open(PROMPT_FILE, "r") as f:
    prompt = f.read()


model = Llama.from_pretrained(
    repo_id=MODEL_REPO,
    filename=MODEL_FILE,
    n_ctx=8192,
    n_gpu_layers=20,
    n_batch=64,
    verbose=False,
)


for file in data:
    tag = file["tag"]
    results = []
    try:
        total_n = len(file["posts"])
        for i, text in enumerate(file["posts"]):
            print(f"\n\nProcessing post {i}/{total_n} from file {tag}")

            messages = [
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": "/no_think\n" + text,
                },
            ]

            response = model.create_chat_completion(
                messages=messages,
                max_tokens=1024,
                temperature=0.2,
                stream=True,
            )

            output = ""

            for chunk in response:
                content = chunk["choices"][0]["delta"].get("content", "") or ""  # type: ignore

                if output == "" and content.strip() in ["", "<think>", "</think>"]:
                    continue

                else:
                    print(content, end="", flush=True)
                    output += content

            print()

            results.append(
                {
                    "output": output.strip(),
                    "text": text,
                }
            )

    except KeyboardInterrupt:
        break

    finally:
        save = {
            "name": file["name"],
            "tag": tag,
            "posts": results,
        }
        with open(f"{SAVE_DIR}/{tag}.json", "w", encoding="utf-8") as file:
            json.dump(
                save,
                file,
                indent=4,
                ensure_ascii=False,
            )
