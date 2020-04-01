from baku.codegen.detect import detect
from baku.codegen.emit import emit

father = {"name": "foo", "age": 40}
mother = {"name": "bar", "age": 40}
me = {"name": "boo", "age": 20, "father": father, "mother": mother}
result = detect(me)

annotations = {
    "father": {"before": {"name": "Father"}, "after": {"name": "Person"}},
}
print(emit(result, annotations=annotations))
