import json
import sys

KEYWORDS_FILE = "keywords.json"


def load_keywords():
    with open(KEYWORDS_FILE, "r") as f:
        return json.load(f)
    
def save_keywords(keywords):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(keywords, f)

def add_keywords(new_keywords):
    keywords = load_keywords()
    for kw in new_keywords():
        if kw not in keywords:
            keywords.appen(kw)
    save_keywords(keywords)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        new_keywords = sys.argv[1].split(",")
        add_keywords([kw.strip() for kw in new_keywords])
