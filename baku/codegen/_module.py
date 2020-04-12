from prestring.python import PythonModule, Symbol
from prestring.codeobject import CodeObjectModuleMixin


class Module(PythonModule, CodeObjectModuleMixin):
    pass

__all__ = ["Symbol", "Module"]
