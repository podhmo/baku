from functools import partial
from baku.q import q, QBuilder


def test_it():
    builder = QBuilder()
    q_ = partial(q, builder=builder)
    assert str(q_("x")) == "x"
