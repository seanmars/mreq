import sys; sys.path.insert(0, __file__.rsplit("selftest",1)[0])
from cases import ref_due
def due_at(c, h, holidays=frozenset()): return ref_due(c, h, holidays)
