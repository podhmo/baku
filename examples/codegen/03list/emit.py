from baku.codegen.detect import detect
from baku.codegen.emit import emit

father = {"name": "foo", "age": 40}
mother = {"name": "bar", "age": 40}
me = {"name": "boo", "age": 20, "parents": [father, mother]}
result = detect(me)
print(emit(result))
