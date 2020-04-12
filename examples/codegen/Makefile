default: 00 01 02 03 04 05 06 07 08 09

SHELL := $(shell which bash)

# simple data
00:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# nested data
01:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# adjust class name with annotations
02:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# list
03:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# children=[], empty list
04:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# additionals=None, null
05:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# article.content and article.comments[].content, conflicted
06:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# fullname
07:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py

# members=[you,me], members2=[me,you], then, me.parents=[father,mother], you.parents=[]
08:
	diff -u	$(shell echo $@*/)emit.py $(shell echo $@*/)emit2.py |& tee $(shell echo $@*/)emit_emit2.diff
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py
	python $(shell echo $@*/)emit2.py |& tee $(shell echo $@*/)output2.graph.py

# with optionals, [{name,age,nickname},{name,age}]
09:
	python $(shell echo $@*/)emit.py |& tee $(shell echo $@*/)output.graph.py
