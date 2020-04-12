from baku.codegen.detect import detect
from baku.codegen.emit import emit

data = {
    "article": {
        "content": {"abbrev": "", "body": "article content"},
        "comments": [
            {"user": "foo", "content": {"body": "comment content"}},
            {"user": "foo", "content": {"body": "comment content"}},
        ],
    }
}
result = detect(data)
print(emit(result))
