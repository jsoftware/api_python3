from jclient import JClient
from pathlib import Path
import random
import numpy as np
import pytest

NESTING = 4

def check_elementwise(jc, s1, s2):
  a = np.random.randint(100, size=s1)
  b = np.random.randint(100, size=s2)
  jc.set('a', a) ; jc.set('b', b)
  err = jc.do('r =: a +Broadcastly b')
  if err == 0:
    r = jc.get('r')
    assert np.array_equal(r, a + b)
  else:
    with pytest.raises(ValueError):
      a + b

def test_broadcastly():
  with JClient(Path(__file__).resolve().parents[NESTING]) as jc:
    pairs = [
      ((), ()),
      ((), (2,3)),
      ((1,4), (5,1)),
      ((3,4), (2,3,4)),
      ((1,4,1,1), (1,2,3,1,1,5)),
      # Incorrect.
      ((2), (3)),
      ((2, 1, 3, 4), (2, 4, 4, 4)),
      # Empty.
      ((0), (0)),
      ((0), ()),
      ((2, 0, 0), (1, 1, 0)),
      ((2, 0), (0, 1)),
    ]
    # Element-wise.
    for (s1, s2) in pairs:
       check_elementwise(jc, s1, s2)
    # Random.
    for _ in range(1000):
      s1 = tuple(random.randint(1, 2) for _ in range(random.randint(0, 10)))
      s2 = tuple(random.randint(1, 2) for _ in range(random.randint(0, 10)))
      check_elementwise(jc, s1, s2)
    # vecdot
    a = np.random.rand(2, 1, 3, 4)
    b = np.random.rand(5, 1, 4)
    jc.set('a', a) ; jc.set('b', b)
    assert not jc.do('r =: a +/@:*"1 Broadcastly b')
    assert np.allclose(jc.get('r'), np.vecdot(a, b))
    # hypot
    assert not jc.do('r =: | a j.Broadcastly b')
    assert np.allclose(jc.get('r'), np.hypot(a, b))
    # matmul
    a = np.random.rand(2, 1, 6, 3, 5)
    b = np.random.rand(3, 2, 1, 1, 5, 7)
    c = np.random.rand(5)
    jc.set('a', a) ; jc.set('b', b) ; jc.set('c', c)
    assert not jc.do('r =: a +/ .*"2 Broadcastly b')
    assert np.allclose(jc.get('r'), np.matmul(a, b))
    assert not jc.do('r =: a +/ .*"2 Broadcastly c')
    assert np.allclose(jc.get('r'), np.matmul(a, c))
