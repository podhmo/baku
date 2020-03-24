from baku.codegen.detect import detect
from baku.codegen.emit import emit

data = {"name": "foo", "age": 20}
result = detect(data)
print(emit(result))
