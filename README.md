# pyease

Python Library with helpful functions for
[Eclipse Advanced Scripting Environment](https://www.eclipse.org/ease/) (EASE)

## Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Prepare Eclipse workspace](#prepare-eclipse-workspace)
  - [Get the SWTWorkbenchBot and a logger](#get-the-swtworkbenchbot-and-a-logger)
- [Development](#development)
  - [Inject IPython kernel](#inject-ipython-kernel)

## Installation

```sh
pip install git+https://github.com/DSD-DBS/pyease.git
```

## Usage

### Prepare Eclipse workspace

The given library comes with a command line interface to automatically create and
prepare an empty Eclipse workspace with EASE settings.

To use EASE in an Eclipse workspace it is needed to configure some settings in the
workspace. The workbench needs to know where to find the Python executable to be used
and it must also be configured where EASE scripts will be located.

This step is automated and can be performed using the `pyease` library. Define where you
want a new Eclipse workspace to be created via an environment variable `EASE_WORKSPACE`.

Where EASE scripts will be located can be configured via another environment variable
named `EASE_SCRIPTS_LOCATION`.

**Example:**

```sh
EASE_WORKSPACE=$HOME/workspace \
EASE_SCRIPTS_LOCATION=$HOME/ease_scripts \
/path/to/python -m pyease.ease
```

### Get the SWTWorkbenchBot and a logger

To automate the user interface one mostly deals with the top level class
[SWTWorkbenchBot](https://download.eclipse.org/technology/swtbot/galileo/dev-build/apidocs/org/eclipse/swtbot/eclipse/finder/SWTWorkbenchBot.html)
that inherits from [SWTBot](https://download.eclipse.org/technology/swtbot/galileo/dev-build/apidocs/org/eclipse/swtbot/swt/finder/SWTBot.html).

```python
import pyease.ease as ease

BOT = ease.BOT
logger = ease.logger
logger.info("Hello world!")
```

## Development

### Inject IPython kernel

Developing EASE scripts with Python can be tedious. It is of great help to be able
to run an EASE script and be able to halt and get an IPython command line with the scope
at a specified location.

#### Preconditions

1. Install the GNU Project Debugger (GDB), e. g. `apt-get install gdb`
1. Install Python debug symbols, e. g. `apt-get install python3-dbg`
1. Install Python packages `ipykernel` and `jupyter`,
   e. g. `pip install ipykernel jupyter`
1. Create a custom gdb Python extension for easy injection of Python code into a halted
   (breakpoint) Python process:

   - Create a file `~/.gdbextension.py` with the following content:

     ```python
     import gdb

     def lock_GIL(func):
         def wrapper(*args):
             gdb.execute("call PyGILState_Ensure()")
             func(*args)
             gdb.execute("call PyGILState_Release()")

         return wrapper


     class Py(gdb.Command):
         def __init__(self):
             super(Py, self).__init__ (
                 "py",
                 gdb.COMMAND_NONE
             )

         @lock_GIL
         def invoke(self, command, from_tty):
             if command[0] in ('"', "'",):
                 command = command[1:]
             if command[-1:] in ('"', "'",):
                 command = command[:-1]
             cmd_string = f"exec('{command}')"
             gdb.execute(f'call PyRun_SimpleString("{cmd_string}")')


     class PyFile(gdb.Command):
         def __init__(self):
             super(PyFile, self).__init__ (
                 "pyfile",
                 gdb.COMMAND_NONE
             )

         @lock_GIL
         def invoke(self, filename, from_tty):
             cmd_string = f"with open('{filename}') as f: exec(f.read())"
             gdb.execute(f'call PyRun_SimpleString("{cmd_string}")')

     Py()
     PyFile()
     ```

   - Past the next code scnippet into a file `~/.gdbinit`.

     You may need to adapt the file path in the first line of the code snippet.

     ```sh
     source /usr/share/gdb/auto-load/usr/bin/python3.9-gdb.py
     source ~/gdbextension.py
     set history save on
     set history filename ~/.gdb_history
     ```

1. Patch py4j code:
   - Edit the file
     `/opt/capella/plugins/py4j-python_0.10.9.2-bnd-2odeag/src/py4j/java_collections.py`
     and encapsulate the first line of the method `__compute_item` in a

     ```python
     def __compute_item(self, key):
         try:
             new_key = self.__compute_index(key)
         except IndexError:
             return ""
     ```

### Steps

Note: when you want to do the next in a Docker container you must set the
following flags of the `docker run` command:
`--cap-add=SYS_PTRACE --security-opt seccomp=unconfined`

1. Launch Eclipse
1. Prepare the EASE script of interest you want to debug in an IPython
   command line shell by placing the following line at the location of interest:
   `import os; print(os.getpid()); breakpoint()`
1. Execute the script in Eclipse and note the PID that will be printed onto the console
1. Start GDB: `$ gdb`
1. In GDB

   ```text
   (gdb) attach <PID>
   (gdb) py "import IPython; IPython.embed_kernel()"
   ```

   This injects an IPython kernel at the line where you placed above Python code
   snippet that ends with a `breakpoint()` statement.

1. In a separate shell run `$jupyter console --existing kernel-<PID>.json`
