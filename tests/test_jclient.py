from jclient import JClient
from pathlib import Path
import numpy as np
import pytest

NESTING = 4

def test_int64():
  with JClient(Path(__file__).resolve().parents[NESTING]) as jc:
    # Arrays.
    jc.do('a =: i. 2 3 4')
    a = jc.get('a')
    b = np.arange(2 * 3 * 4).reshape(2, 3, 4)
    assert np.array_equal(a, b)
    c = 100 + b
    jc.set('c', c)
    jc.do('c =: *: c')
    d = jc.get('c')
    assert np.array_equal(d, c ** 2)
    # Atoms.
    e = np.int64(42)
    jc.set('e', e)
    jc.do('e + 1 2 3')
    assert jc.getr() == '43 44 45\n'
    jc.dor('f =: 73')
    f = jc.get('f')
    assert np.array_equal(f, np.array(73))
  with pytest.raises(Exception):
    jc.dor('2 + 3')

def test_float64():
  jc = JClient(Path(__file__).resolve().parents[NESTING])
  # Arrays.
  jc.do('a =: 5 5 $ 1 % >: i. 25')
  a = jc.get('a')
  assert np.array_equal(a, np.reshape(1 / np.arange(1, 26), (5, 5)))
  b = np.array([np.inf, -np.inf, 3.7])
  jc.set('b', b)
  jc.do('b -: _ __ 3.7')
  assert jc.getr() == '1\n'
  # Atoms.
  jc.dor('c =: _.')
  c = jc.get('c')
  assert np.isnan(c)
  jc.set('d', np.float64(42.77))
  jc.do('d - 2')
  assert jc.getr() == '40.77\n'
  jc.close()
  with pytest.raises(Exception):
    jc.getr()

def test_extended():
  jc = JClient(Path(__file__).resolve().parents[NESTING])
  jc.do('1232342341231231324234223423421x + 189793817293879128379128739182739182791723912312x')
  assert jc.getr() == '189793817293879129611471080413970507025947335733\n'

def test_bytes():
  jc = JClient(Path(__file__).resolve().parents[NESTING])
  jc.set('a', b'A3@ 2Z% ^{]$ q')
  jc.set('b', "A3@ 2Z% ^{]$ q")
  jc.do('a -: b')
  assert jc.getr() == "1\n"
  a = jc.get('a')
  b = jc.get('b')
  assert a.dtype == np.dtype('S1')
  assert b.dtype == np.dtype('S1')
  assert np.array_equal(a, b)
  jc.do("c =: 3 3 $ 'abcd'")
  c = jc.get('c')
  assert c.dtype == np.dtype('S1')
  d = np.array([b'a', b'b', b'c', b'd'], dtype='S1').reshape((2, 2))
  jc.set('d', d)
  jc.do("d -: 2 2 $ 'abcd'")
  assert jc.getr() == '1\n'
  e = jc.get('d')
  assert np.array_equal(d, e)

def test_bool():
  jc = JClient(Path(__file__).resolve().parents[NESTING])
  jc.set('f', np.array([0, 1, 0, 0, 1], dtype='bool'))
  jc.do('f =: -. f')
  f = jc.get('f')
  assert np.array_equal(f, np.array([1, 0, 1, 1, 0], dtype='bool'))

def test_complex():
  jc = JClient(Path(__file__).resolve().parents[NESTING])
  a = np.array([1+2j, 3+4j, 5+6j], dtype=np.complex128)
  jc.set('a', a)
  jc.do('a =: *: a')
  b = jc.get('a')
  assert np.array_equal(b, a ** 2)

def test_script(tmpdir):
  jc = JClient(Path(__file__).resolve().parents[NESTING])
  test_file = tmpdir.join('testfile.ijs')
  test_file.write("cocurrent 'abc'\na =: 42\n'a' + 1")
  err = jc.script(test_file)
  assert err == 3
  assert jc.get('a_abc_') == np.int64(42)
  with pytest.raises(Exception):
    assert jc.get('a__')
    
