import json
import os
import googletrans
from googletrans import Translator
import copy


def load_translate(input_path):
    en2zh = {}
    for root, dirs, files in os.walk(input_path):
        for fn in files:
            if not fn.endswith(".txt"):
                continue
            print(f"Loading {fn}...")
            with open(os.path.join(root, fn), encoding="UTF-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip().split("=")
                    if len(line) != 2:
                        continue
                    en2zh.update({line[0]: line[1]})
    print(f"Loaded {len(en2zh)} translations")
    return en2zh


class TranslateWithCache(object):
    CACHE_FILE = "./data/translate_cache_character.json"

    def __init__(self, enable_google_translate=True):
        if not os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, "w+", encoding="UTF-8") as f:
                f.write("{}")
        with open(self.CACHE_FILE, "a+", encoding="UTF-8") as f:
            f.seek(0)
            self.cache = json.load(f)
        print(googletrans.LANGUAGES)
        self.enable_google_translate = enable_google_translate
        self.translator = Translator()
        self.last_push_count = len(self.cache)

    def goole_translate(self, txt, src="en", dest="zh-cn"):
        if not self.enable_google_translate:
            return None
        try:
            result = self.translator.translate(txt, src=src, dest=dest)
            print(f"{txt} -> {result.text}")
            return result.text
        except Exception as e:
            print(e)
            return None

    def translate(self, txt, src="en", dest="zh-cn"):
        if txt in self.cache:
            return self.cache[txt]
        result = self.goole_translate(txt, src, dest)
        if result is not None:
            self.cache.update({txt: result})
        return result

    def push(self):
        if len(self.cache) > self.last_push_count:
            with open(self.CACHE_FILE, "w+", encoding="UTF-8") as f:
                f.write(json.dumps(self.cache, ensure_ascii=False, indent=4))
                self.last_push_count = len(self.cache)


def translate_json():
    translator = TranslateWithCache()
    en2zh = load_translate("../image2text_prompt_generator/data/translate_cache/tags/")
    with open("./data/danbooru-tags.json", encoding="UTF-8") as f:
        tags = json.load(f)
    print(f"Loaded {len(tags)} tags")
    count = 0
    for tag in tags:
        tag_name = copy.copy(tag["name"]).replace("_", " ")
        if tag_name in en2zh:
            tag["zh_cn"] = en2zh[tag_name]
        elif tag_name in en2zh:
            tag["zh_cn"] = en2zh[tag_name]
        elif tag["category"] == 3:
            text = translator.translate(tag_name, src="en", dest="zh-cn")
            print(f"Translated {tag['name']} -> {text}")
            count += 1
            if count % 10 == 0:
                translator.push()
            if text is not None:
                tag["zh_cn"] = text
            else:
                tag["zh_cn"] = ""
    with open("./data/danbooru-tags-zh-cn-1.json", "w+", encoding="UTF-8") as f:
        f.write(json.dumps(tags, ensure_ascii=False))


if __name__ == "__main__":
    translate_json()
