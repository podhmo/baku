from baku.codegen.detect import detect
from baku.codegen.emit import emit

father = {"name": "foo", "age": 40}
mother = {"name": "bar", "age": 40}
me = {"name": "me", "age": 20, "parents": [father, mother]}
you = {"name": "you", "age": 20, "parents": []}
result = detect({"members2": [me, you], "members": [you, me]})
print(emit(result))
