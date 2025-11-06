import os
import sys
from pathlib import Path
from typing import Any, Union
from ctypes import CDLL, byref, string_at, c_int64, c_char_p, c_void_p
import numpy as np
from numpy.typing import NDArray

class JClient:
  def __init__(self, j_dir_path: Union[str, Path], load_profile: bool = True):
    if sys.platform.startswith("win"):
      dll_name = 'j.dll'
    elif sys.platform.startswith("linux"):
      dll_name = 'libj.so'
    elif sys.platform.startswith("darwin"):
      dll_name = 'libj.dylib'
    else:
      raise RuntimeError(f"Unsupported OS: {sys.platform}")
    
    bin_path = Path(j_dir_path).expanduser() / "bin"
    dll_path = bin_path / dll_name
    profile_path = bin_path / "profile.ijs"
    
    try:
      self.libj = CDLL(dll_path)
    except OSError as e:
      raise RuntimeError(f"Failed to load J DLL: {e}")
    self.libj.JInit.restype = c_void_p
    self.libj.JGetR.restype = c_char_p
    
    self.jt = self.libj.JInit()
    if self.jt == 0:
      raise RuntimeError("J initialization failed")
    
    if load_profile:
      if 0 != self.do("0!:0<'" + str(profile_path) + "'[BINPATH_z_=:'" + str(bin_path) + "'[ARGV_z_=:''"):
        raise RuntimeError("Loading profile.ijs failed")
    
    self.__J_NP_TYPES = {
      1: 'bool',
      2: 'S1',
      4: 'int64',
      8: 'float64',
      16: 'complex128'
    }
    self.__NP_J_TYPES = {np.dtype(v): k for k, v in self.__J_NP_TYPES.items()}

  def close(self):
    if hasattr(self, 'jt') and self.jt:
      self.libj.JFree(c_void_p(self.jt))
      self.jt = 0

  # Run sentence and return error code.
  def do(self, sent: str) -> int:
    self.__check_handle()
    return self.libj.JDo(c_void_p(self.jt), sent.encode())

  # Get output result from last sentence.
  def getr(self) -> str:
    self.__check_handle()
    return string_at(self.libj.JGetR(c_void_p(self.jt))).decode()

  # Run sentence and print output result.
  def dor(self, sent: str) -> None:
    self.do(sent)
    s = self.getr()[:-1]
    if len(s) > 0:
      print(s)

  # Run J script from the file at the given path and return error code.
  def script(self, path: Union[str, Path]) -> int:
    return self.do("0!:0 < '" + str(path) + "'")

  # Get value of J noun.
  def get(self, noun_name: str) -> NDArray:
    self.__check_handle()
    jtype = c_int64(0); jrank = c_int64(0); jshape = c_int64(0); jdata = c_int64(0)
    err = self.libj.JGetM(c_void_p(self.jt), c_char_p(noun_name.encode()), byref(jtype), byref(jrank), byref(jshape), byref(jdata))
    if err != 0:
      raise RuntimeError(f"Invalid noun name: {noun_name}")
    shape = self.__to_numpy(jshape, jrank.value, 'int64')
    atoms_count = np.prod(shape)
    if jtype.value in self.__J_NP_TYPES:
      return np.reshape(self.__to_numpy(jdata, atoms_count, self.__J_NP_TYPES[jtype.value]), shape)
    else:
      raise TypeError('Type not supported')

  # Set J noun with value.
  def set(self, noun_name: str, data: Any) -> None:
    self.__check_handle()
    noun_name_bytes = noun_name.encode()
    if isinstance(data, str):
      data = data.encode()
    if isinstance(data, bytes):
      jtype = c_int64(2)
      jrank = c_int64(1)
      jshape = c_char_p(np.array([len(data)], dtype=np.int64).tobytes())
      jdata = c_char_p(data)
    elif isinstance(data, (np.ndarray, np.generic)) and data.dtype in self.__NP_J_TYPES:
      jtype = c_int64(self.__NP_J_TYPES[data.dtype])
      jrank = c_int64(data.ndim)
      jshape = c_char_p(np.asarray(data.shape, dtype='int64').tobytes())
      jdata = c_char_p(data.tobytes())
    else:
      raise TypeError('Type not supported')
    err = self.libj.JSetM(c_void_p(self.jt), c_char_p(noun_name_bytes), byref(jtype), byref(jrank), byref(jshape), byref(jdata))
    if err != 0:
      raise RuntimeError('Invalid noun name')

  # Run simple J REPL (Read-Eval-Print Loop). Enter .... to exit the loop.
  def repl(self) -> None:
    prompt = '   '
    sent = input(prompt)
    while sent != '....':
      self.dor(sent)
      sent = input(prompt)

  @staticmethod
  def __to_numpy(jdata, atoms_count, dtype_name: str) -> NDArray:
    return np.frombuffer(string_at(jdata.value, atoms_count * np.dtype(dtype_name).itemsize), dtype=dtype_name).copy()
  
  def __check_handle(self) -> None:
    if self.jt == 0:
      raise RuntimeError("Cannot communicate with J: it is not running")

  def __enter__(self):
    return self
  
  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()
    return False

  def __del__(self):
    try:
      self.close()
    except Exception:
      pass
