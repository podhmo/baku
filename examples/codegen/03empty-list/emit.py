from baku.codegen.detect import detect
from baku.codegen.emit import emit

me = {"name": "boo", "age": 20, "parents": []}
result = detect(me)
print(emit(result))
