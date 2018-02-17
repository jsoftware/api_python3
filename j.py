# usage
#  put j.py and j_config.py where python can find them
#  edit j_config.py for your J installation
#  start python3
#   import j
#   j.init()
#   j.do('abc=: i.2 3')
#   q= j.get('abc')
#   j.set('ghi',23+q)
#   j.get('ghi')
#   j.do('+a.')
#   j.getlasterror()
#   j.test()

# python types supported: bytes, numpy int64, numpy float64 
# python strings treated as utf-8 bytes
# bytes treated as list
# numpy arrays have shape
# J booleans not supported
# json support would be reasonable next step
# import importlib - importlib.reload(j) - eases development

import j_config # define pathbin, pathdll, pathpro
from ctypes import *
import numpy

def tob(s):
 if type(s) is str:
  s= s.encode('utf-8')
 return s

def init():
 global libj,jt
 libj=  CDLL(j_config.pathdll)
 jt= libj.JInit()
 if jt==0:
  raise AsserttionError('J: init library failed')

 e= do("0!:0<'"+j_config.pathpro+"'[BINPATH_z_=:'"+j_config.pathbin+"'[ARGV_z_=:''")
 if e!=0:
  raise AssertionError('J: load profile failed')

def do(a):
 return libj.JDo(jt,tob(a))

def getlasterror():
 do("last_python_call_error=: 13!:12''") 
 return get('last_python_call_error')

def get(n):
 dt= c_ulonglong(0) ; dr= c_ulonglong(0) ; ds= c_ulonglong(0) ; dd= c_ulonglong(0)
 e= libj.JGetM(jt,tob(n),byref(dt),byref(dr),byref(ds),byref(dd))
 t= dt.value
 if t==0: # e not set for error
  raise AssertionError('J: get arg not a name')

 shape= numpy.fromstring(string_at(ds.value,dr.value*8),dtype=numpy.int64)
 count= numpy.prod(shape)
 if t==2:
  r= (string_at(dd.value,count)) #.decode("utf-8")
 elif t==4:
  r= numpy.fromstring(string_at(dd.value,count*8),dtype=numpy.int64)
  r.shape= shape
 elif t==8:
  r= numpy.fromstring(string_at(dd.value,count*8),dtype=numpy.float64)
  r.shape= shape
 else:
  raise AssertionError('J: get type not supported')

 return r

def set(n,d):
 n= tob(n) ; d= tob(d)
 dt= c_longlong(0) 
 
 if type(d) is bytes:
  dt.value= 2
  dr= c_longlong(1)
  ds= c_longlong(len(d))
  ss= c_char_p(string_at(addressof(ds),8))
  dd= c_char_p(d)
 else:
  dt.value= 4 if d.dtype=='int64' else 8
  p= numpy.asarray(d.shape)
  dr= c_longlong(len(p))
  ss= c_char_p(p.tobytes())
  dd= c_char_p(d.tobytes())

 e= libj.JSetM(jt,n,byref(dt),byref(dr), byref(ss) ,byref(dd))
 if e!=0:
  raise AssertionError('J: set arg not a name')

def test():
 do('b=: |.BINPATH[f=: 0.5+i=: i.2 3')
 xb= get('b')
 xi= get('i')
 xf= get('f')
 print(xb)
 print('\n',xi)
 print('\n',xf)
 set('xb',xb)
 set('xi',xi)
 set('xf',xf)
 do('+a.')
 print(getlasterror())
 do('r=: 0+(b-:xb),(i-:xi),f-:xf')
 return get('r')


