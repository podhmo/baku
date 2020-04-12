from baku.codegen.detect import detect
from baku.codegen.emit import emit

me = {"name": "me", "age": 20, "nickname": "M"}
you = {"name": "you", "age": 20}
result = detect({"members": [you, me]})
print(emit(result))
