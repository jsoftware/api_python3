# Python API for calling J

## Setup

Assuming J is already installed, use below commands to create a Python virtual environment for your project and install package.

### Windows
```
python3 -m venv MyProject
cd MyProject
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\Scripts\activate
pip install -e C:\your\path\to\j9.7\addons\api\python3
```

### Linux/macOS
```
python3 -m venv MyProject
cd MyProject
source bin/activate
pip install -e /your/path/to/j9.7/addons/api/python3
```

> **Important for macOS users:** The default system Python at `/usr/bin/python3` is not suitable for most projects that use dynamic libraries, including this one. To avoid issues, use a user-managed Python installation (e.g. Homebrew, Python.org, Conda).

## Initialization

Import

`from jclient import JClient`

and use with context manager

`with JClient('/your/path/to/directory/j9.7') as jc:`

or by standard object creation.

`jc = JClient('/your/path/to/directory/j9.7')`

Add `load_profile=False` after the path if you need a totally clean J session.

## Methods

### get
Gets the value of J noun and returns it in Python format. J types are converted according to the below table.

| J        | Python            |
|----------|-------------------|
| boolean  | numpy.bool        |
| literal  | numpy.dtype('S1') |
| integer  | numpy.int64       |
| floating | numpy.float64     |
| complex  | numpy.complex128  |

`val = jc.get('a')`

### set
Sets J noun with value from Python. Python types are converted according to the below table.

| Python            | J        |
|-------------------|----------|
| str               | literal  |
| bytes             | literal  |
| numpy.bool        | boolean  |
| numpy.dtype('S1') | literal  |
| numpy.int64       | integer  |
| numpy.float64     | floating |
| numpy.complex128  | complex  |

`jc.set('a', numpy.array([7, 42, 10], dtype='int64'))`

### do
Executes given J sentence and returns error code (0 if no error).

`err = jc.do('2 + 3')`

### script
Runs J script from the file at the given path and returns error code.

`err = jc.script('/your/path/to/file.ijs')`

### getr
Returns the result of the most recent J sentence.

`res = jc.getr()`

### dor
Executes given J sentence and prints the result.

`jc.dor('2 + 3')`

### close
Closes J session.

`jc.close()`

### repl
Runs simple J Read-Eval-Print Loop. Enter `....` to exit the loop.

`jc.repl()`

## Testing
Install `pytest` package

`pip install pytest`

and run all tests with

`pytest`
