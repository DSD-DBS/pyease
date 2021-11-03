"""Module to prepare an EASE workspace and with code for use of EASE with Python.

To get a prepared workspace the environment variables

* ``EASE_WORKSPACE`` and
* ``EASE_SCRIPTS_LOCATION``

must be set.

The environment variable ``EASE_WORKSPACE`` points to an absolute directory path that
will be used to create the prepared Capella workspace.

The directory must not exist and will be removed/ recreated if it is already given.
With that variable defined the current script is to be run using a Python3 interpreter.

The workspace that will be created comes with needed EASE preferences that are normally
set in the Capella GUI. These preferences tell EASE which Python interpreter is to be
used (it is the one used for this non EASE context no. 1) and defines where EASE can
find this present EASE script to execute it on startup of Capella as defined in the
special comment in the very first line of this module.

The environment variable ``EASE_SCRIPTS_LOCATION`` is an absolute directory path telling
EASE where to look for Python scripts.

Both of these environment variables must be set before one executes this present module
via

.. code-block:: bash

    python3 -m pyease.ease

The current script logs what it does into a log file named ``ease.log`` in the
current working directory.

.. note::

    The module expects, that Eclipse/ Capella is set to English language.

.. seealso::

    The acronym EASE stands for "Eclipse Advanced Scripting Environment".
    Further information: https://www.eclipse.org/ease/

"""
# Standard library:
import logging
import os
import re
import shutil
import subprocess
import sys
import typing as t
from pathlib import Path

# local:
import pyease.easeexceptions as exp

BOT: t.Any = None
DEBUG: bool = os.getenv("DEBUG", "0") == "1"
IS_EASE_CTXT: bool = True
MODULE_DIR: Path = Path(__file__).parents[0]

try:
    BOT = org.eclipse.swtbot.eclipse.finder.SWTWorkbenchBot()  # type: ignore # noqa
    """
    see https://download.eclipse.org/technology/swtbot/galileo/dev-build/apidocs/org/eclipse/swtbot/eclipse/finder/SWTWorkbenchBot.html
    see https://download.eclipse.org/technology/swtbot/galileo/dev-build/apidocs/org/eclipse/swtbot/swt/finder/SWTBot.html
    see https://www.eclipse.org/swt/widgets/

    """  # noqa: E501, W505
    # 3rd party:
    from eclipse.system.platform import getSystemProperty  # type: ignore # noqa
    from eclipse.system.resources import getWorkspace  # type: ignore # noqa
    from eclipse.system.ui import isHeadless  # type: ignore # noqa
except NameError:
    IS_EASE_CTXT = False

logger: logging.Logger = logging.getLogger()
logger.setLevel("DEBUG" if DEBUG else "INFO")


class _MyLoggingFilter(logging.Filter):
    def __init__(self):
        pass

    def filter(self, record):  # noqa:A003 "'filter' is shadowing a python builtin"
        filter_: bool = any(
            (
                record.msg.startswith("Command to send: "),
                record.msg.startswith("Received command "),
                record.msg.startswith("Answer received: "),
                record.msg.startswith("send_command:"),
                "Python Server ready to receive messages" in record.msg,
            )
        )
        # print(f"Record: {record}")
        return not filter_


formatter: logging.Formatter
if DEBUG:
    formatter = logging.Formatter(
        fmt=(
            "[%(asctime)s] %(levelname)-8s in "
            "%(module)s:%(funcName)s:%(lineno)d : %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
else:
    formatter = logging.Formatter(
        fmt=("[%(asctime)s] %(levelname)-8s : %(message)s "),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# logging console handler:
console_hdl: logging.Handler = logging.StreamHandler(sys.stderr)
console_hdl.setLevel("DEBUG" if DEBUG else "INFO")
console_hdl.setFormatter(formatter)
console_hdl.addFilter(_MyLoggingFilter())
logger.addHandler(console_hdl)


class ButtonWithLabelIsAvailable(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, label):
        """Construct class."""
        self.label = label

    def init(self, bot):
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition (if button with label is accessible)."""
        try:
            self.bot.button(self.label)
            logger.debug(f"Button labelled '{self.label}' is available.")
        except Exception:
            logger.debug(f"Button labelled '{self.label}' is not available.")
            return False
        return True

    def getFailureMessage(self):
        """Define message that will be raised when the timeout reached."""
        return f"Could not find a button labelled '{self.label}'!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


class ButtonWithLabelIsEnabled(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, label):
        """Construct class."""
        self.label = label

    def init(self, bot):
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition (if button with label is accessible)."""
        button: t.Any = self.bot.button(self.label)
        enabled: bool = button.isEnabled()
        logger.debug(
            f"Button labelled '{self.label}' is{'' if enabled else ' not'} enabled."
        )
        return enabled

    def getFailureMessage(self):
        """Define message that will be raised when the timeout reached."""
        return f"Could not find a button labelled '{self.label}'!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


class ButtonWithLabelIsNotAvailable(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, label: str):
        """Construct class."""
        self.label = label

    def init(self, bot: t.Any) -> None:
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition (if button with label is accessible)."""
        try:
            self.bot.button(self.label)
            logger.debug(f"Button labelled '{self.label}' is available.")
            return False
        except Exception:
            logger.debug(f"Button labelled '{self.label}' is not available.")
            return True

    def getFailureMessage(self) -> str:
        """Define message that will be raised when the timeout reached."""
        return f"Could not find a button labelled '{self.label}'!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


class ComboBoxWithLabelIsAvailable(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, label):
        """Construct class."""
        self.label = label

    def init(self, bot):
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition (if combo box with label is accessible)."""
        try:
            self.bot.comboBoxWithLabel(self.label)
            logger.debug(f"Combo box labelled '{self.label}' is available.")
        except Exception:
            logger.debug(f"Combo box labelled '{self.label}' is not available.")
            return False
        return True

    def getFailureMessage(self):
        """Define message that will be raised when the timeout reached."""
        return f"Could not find a combo box labelled '{self.label}'!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


class CompareResultIsAvailable(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, label):
        """Construct class."""
        self.label = label

    def init(self, bot):
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition."""
        try:
            BOT.button("OK").click()
        except Exception:
            pass
        try:
            logger.info("Wait for compare result...")
            compare_editor: t.Any = BOT.editorByTitle(self.label)
            synthesis_tree: t.Any = compare_editor.bot().tree(0)
            logger.info(
                f"Identified (handle) compare result tree view '{synthesis_tree}'."
            )
            return True
        except Exception:
            return False

    def getFailureMessage(self):
        """Define message that will be raised when the timeout reached."""
        return "Cannot access compare result!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


class MenuIsAvailable(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, label):
        """Construct class."""
        self.label = label

    def init(self, bot):
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition (if menu with label is accessible)."""
        try:
            self.bot.menu(self.label)
        except Exception:
            return False
        return True

    def getFailureMessage(self):
        """Define message that will be raised when the timeout reached."""
        return f"Could not find the menu labelled '{self.label}'!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


class TextfieldWithLabelIsAvailable(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, label):
        """Construct class."""
        self.label = label

    def init(self, bot):
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition (if text field with label is accessible)."""
        try:
            self.bot.textWithLabel(self.label)
            logger.debug(f"Text field labelled '{self.label}' is available.")
        except Exception:
            logger.debug(f"Text field labelled '{self.label}' is not available.")
            return False
        return True

    def getFailureMessage(self):
        """Define message that will be raised when the timeout reached."""
        return f"Could not find a text field labelled '{self.label}'!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


class TreeItemWithLabelMatchingRegExIsAvailable(object):
    """https://download.eclipse.org/technology/swtbot/helios/dev-build/apidocs/org/eclipse/swtbot/swt/finder/waits/DefaultCondition.html"""  # noqa: E501,W505

    def __init__(self, tree: t.Any, label_regex: str):
        """Construct class."""
        self.tree = tree
        self.label_regex = label_regex

    def init(self, bot):
        """Implement Java constructor."""
        self.bot = bot

    def test(self) -> bool:
        """Test the condition (if tree tiem with label is accessible)."""
        tree_item: t.Any
        tree_item_name: str
        for tree_item in self.tree.getAllItems():
            tree_item_name = tree_item.getText()
            if re.match(self.label_regex, tree_item_name) is not None:
                logger.debug(
                    f"Tree item with label matching '{self.label_regex}' is available."
                )
                return True
        logger.debug(
            f"Tree item with label matching '{self.label_regex}' is not available."
        )
        return False

    def getFailureMessage(self):
        """Define message that will be raised when the timeout reached."""
        return f"Could not find a tree item labelled '{self.label}'!"

    class Java:
        """Implement Java interface."""

        implements = ["org.eclipse.swtbot.swt.finder.waits.ICondition"]


def click_button_with_label(label: str, timeout: int = 5000, interval: int = 500):
    """Wait for a button to be available and enabled and click the button.

    The function waits until the button is available and enabled, or the timeout is
    reached. The interval is the delay between attempts to find and click the button.

    Parameters
    ----------
    label
        Label of the button to click
    timeout
        Timeout in ms until we wait to find a button named *label* in an enabled state
    interval
        The interval is the delay between attempts to find and click the button

    """
    if BOT is None:
        raise exp.EaseNoSWTWorkbenchBotError
    BOT.waitUntil(ButtonWithLabelIsAvailable(label), timeout, interval)
    BOT.waitUntil(ButtonWithLabelIsEnabled(label), timeout, interval)
    logger.debug(f"Click the identified button labelled '{label}'...")
    BOT.button(label).click()


def clone_project_from_git(
    git_repo_url: str, git_repo_branch: str, target_git_clone_dir: Path
):
    """Clone (with depth = 1) a Capella model from Git into a target directory.

    This function blocks the main thread until completion. When an ssh Git URL is
    provided the function expects that Gitlab user credentials for ssh are set on the
    computer executing this script.

    Parameters
    ----------
    git_repo_url
        URL to the remote Git repository
    git_repo_branch
        Branch name in the remote Git repository
    target_git_clone_dir
        Target directory path for the git clone of the repository

    """
    if target_git_clone_dir.is_dir():
        shutil.rmtree(target_git_clone_dir, ignore_errors=True)
    logger.info(
        f"Clone of project from '{git_repo_url}' (branch '{git_repo_branch}') "
        f"with depth set to 1 into directory '{target_git_clone_dir}'..."
    )
    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--branch",
                git_repo_branch,
                "--depth",
                "1",
                "--single-branch",
                git_repo_url,
                target_git_clone_dir,
            ],
            capture_output=True,
            check=True,
        )
        logger.info("Cloning Git project completed.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Clone of project from '{git_repo_url}' "
            f"(branch '{git_repo_branch}') failed: {e.stderr}"
        ) from e


def close_eclipse_view(title: str) -> None:
    """Close the Eclipse view specified by its *title*.

    If that view is not open the logger will report that on debug level.

    Parameters
    ----------
    title
        Title of the view to be opened

    """
    found_view: bool = False
    view: t.Any
    for view in BOT.views():
        found_view = view.getTitle() == title
        if found_view:
            view.close()
            break
    if not found_view:
        logger.debug(f"Cannot close view titled '{title}'. View cannot be found.")


def create_empty_workspace_with_ease_setup():
    """Create a workspace as needed for EASE scripts running on startup of Eclipse.

    The following environment variables must be set

    * ``EASE_WORKSPACE`` and
    * ``EASE_SCRIPTS_LOCATION``

    Find more information in the module docstring for :mod:`pyease.ease`.

    """
    workspace_str: str = os.getenv("EASE_WORKSPACE", "")
    if not workspace_str:
        raise OSError("Set the environment variable 'EASE_WORKSPACE'!")
    workspace_path: Path = Path(workspace_str).resolve()
    parent_dir: Path = workspace_path.resolve().parent
    if not parent_dir.is_dir():
        raise ValueError(
            f"The environment variable 'EASE_WORKSPACE' points to an existing "
            f"directory '{workspace_path}' but the parent directory does not exist!"
        )
    if not os.access(parent_dir, os.W_OK):
        raise ValueError(
            f"The directory '{workspace_path}' to create an EASE workspace "
            "is not writeable!"
        )
    if workspace_path.is_dir():
        if not os.access(workspace_path, os.W_OK):
            raise OSError(
                f"The directory '{workspace_path}' to create an EASE workspace "
                "exists but we cannot recreate it (permissions)!"
            )
        logger.info(f"Remove existing directory '{workspace_path}'...")
        shutil.rmtree(workspace_path)

    ease_scripts_location_str: str = os.getenv("EASE_SCRIPTS_LOCATION", "")
    if not ease_scripts_location_str:
        raise OSError("Set the environment variable 'EASE_SCRIPTS_LOCATION'!")
    ease_scripts_location_path: Path = Path(ease_scripts_location_str).resolve()
    parent_dir: Path = ease_scripts_location_path.resolve().parent
    if not parent_dir.is_dir():
        raise ValueError(
            f"The environment variable 'EASE_SCRIPTS_LOCATION' points to an existing "
            f"directory '{ease_scripts_location_path}' but the parent directory does "
            "not exist!"
        )
    logger.info(f"Create Eclipse workspace directory '{workspace_path}'...")
    logger.info("Set preferences for EASE:")
    workspace_path.mkdir(parents=True)
    # Create file that is needed to save the state of the workbench:
    root_dir: Path = Path(
        workspace_path / ".metadata/.plugins/org.eclipse.core.resources/.root"
    )
    logger.debug(f"Create directory '{root_dir}'...")
    root_dir.mkdir(parents=True)
    tree_file_path: Path = Path(root_dir / "1.tree")
    logger.debug(
        f"Create empty file '{tree_file_path}' needed to "
        "save the state of the workbench..."
    )
    tree_file_path.touch()

    # Create settings dir for the preferences we prepare in the following:
    settings_dir: Path = workspace_path / (
        ".metadata/.plugins/org.eclipse.core.runtime/.settings"
    )
    logger.debug(f"Create directory '{settings_dir}'...")
    settings_dir.mkdir(parents=True)

    # set path to Python interpreter to be used by EASE:
    py4j_file_path: Path = settings_dir / "org.eclipse.ease.lang.python.py4j.prefs"
    logger.debug(f"Create file '{py4j_file_path}'...")
    logger.info(f"\t- Python interpreter: '{sys.executable}'")
    python_exe: str = sys.executable.replace("\\", "\\\\")
    Path(py4j_file_path).write_text(
        "eclipse.preferences.version=1\n"
        f"org.eclipse.ease.lang.python.py4j.INTERPRETER={python_exe}\n"
    )

    # set default location for EASE scripts:
    ease_scripts_file_path: Path = settings_dir / "org.eclipse.ease.ui.scripts.prefs"
    logger.debug(f"Create file '{ease_scripts_file_path}'...")
    logger.info(
        f"\t- Default location for EASE scripts: '{ease_scripts_location_path}'"
    )
    module_dir_pipe_separated: str = (
        str(ease_scripts_location_path).replace(os.sep, "|").replace(":", "\\:")
    )
    if not module_dir_pipe_separated.startswith("|"):
        module_dir_pipe_separated = f"|{module_dir_pipe_separated}"

    module_dir: str = (
        str(ease_scripts_location_path).replace(os.sep, "/").replace(":", "\\:")
    )
    if not module_dir.startswith("/"):
        module_dir = f"/{module_dir}"
    Path(ease_scripts_file_path).write_text(
        "eclipse.preferences.version=1\n"
        f"file\\:||{module_dir_pipe_separated}/default=true\n"
        f"file\\:||{module_dir_pipe_separated}/location=file\\://{module_dir}\n"
        f"file\\:||{module_dir_pipe_separated}/recursive=true\n"
    )

    # allow scripts to run code in UI thread:
    ease_prefs_file_path: Path = settings_dir / "org.eclipse.ease.prefs"
    logger.info("\t- Allow scripts to run code in UI thread")
    logger.debug(f"Create file '{ease_prefs_file_path}'...")
    Path(ease_prefs_file_path).write_text(
        "eclipse.preferences.version=1\n"
        "scripts/scriptRemoteAccess=false\n"
        "scripts/scriptUIAccess=true\n"
    )
    # disable UI theme:
    swt_prefs_file_path: Path = settings_dir / (
        "org.eclipse.e4.ui.workbench.renderers.swt.prefs"
    )
    logger.debug(f"Create file '{swt_prefs_file_path}'...")
    logger.info("Set general Eclipse preferences:")
    logger.info("\t- Disable UI theme")
    Path(swt_prefs_file_path).write_text(
        "eclipse.preferences.version=1\nenableMRU=true\nthemeEnabled=false\n"
    )
    # disable exit prompt:
    ide_prefs_file_path: Path = settings_dir / "org.eclipse.ui.ide.prefs"
    logger.debug(f"Create file '{ide_prefs_file_path}'...")
    logger.info("\t- Disable exit prompt")
    Path(ide_prefs_file_path).write_text(
        "EXIT_PROMPT_ON_CLOSE_LAST_WINDOW=false\n"
        "eclipse.preferences.version=1\n"
        "quickStart=false\n"
    )


def fill_text_field_with_label(label: str, text: str):
    """Fill a text field by its label.

    Parameters
    ----------
    label
        Label of the text field
    text
        The *text* to set as content for the text field

    Raises
    ------
    easeexceptions.EaseNoSWTWorkbenchBotError
        When there is no WTWorkbenchBot available

    """
    if BOT is None:
        raise exp.EaseNoSWTWorkbenchBotError
    logger.debug(f"Wait for text field labelled '{label}'...")
    BOT.waitUntil(TextfieldWithLabelIsAvailable(label), 5000, 100)
    textfield: t.Any = BOT.textWithLabel(label)
    logger.debug(f"Set the content of the text field labelled '{label}' to '{text}'...")
    textfield.setText(text)


def import_git_project_from_folder(tmp_git_clone_dir: Path):
    """Import temporary cloned Git project from folder into Capella workspace.

    Parameters
    ----------
    tmp_git_clone_dir
        Temporary path as target for git clone

    """
    logger.info(f"Import Git project from folder ('{tmp_git_clone_dir}')...")
    BOT.menu("File").menu("Import...").click()
    git_node: t.Any = BOT.tree().getTreeItem("General")
    git_node.select()
    git_node.expand()
    git_node.getNode("Projects from Folder or Archive").doubleClick()
    combo_box: t.Any = BOT.comboBox(0)
    combo_box.setText(str(tmp_git_clone_dir))
    click_button_with_label(label="Finish", timeout=60000, interval=500)
    BOT.waitUntil(MenuIsAvailable("File"), 600000, 500)


def is_eclipse_view_shown(title: str) -> bool:
    """Check if an Eclipse view specified by its *title* is currently shown.

    Parameters
    ----------
    title
        Title of the view of request

    Returns
    -------
    bool
        True, when a view with the *title* is currently shown

    """
    for view in BOT.views():
        if view.getTitle() == title:
            return True
    return False


def is_projects_in_workspace() -> bool:
    """Check if we have any project(s) in the workspace.

    The view ``Project Explorer`` does not contain a widget of kind tree when there is
    no project in the workspace or the tree will be empty.
    This function tries to get a handle for that tree and if that fails we know,
    that there is no project in the workspace. If there is a tree, this function will
    check if there is any item in the tree.

    Returns
    -------
    bool
        True, when there is any project in the workspace

    """
    try:
        project_explorer_tree()
        return len(project_explorer_tree().getAllItems()) >= 1
    except Exception:
        return False


def kill_capella_process(signal: int = 9):
    """Kill Capella process.

    The EASE commands

    * ``eclipse.system.ui.exitApplication()``
    * ``eclipse.system.ui.shutdown()``

    might not stop the Capella process. Here is an agressive solution to kill
    the Capella process if needed.

    """
    for line in (
        subprocess.check_output(["ps", "-eo", "pid,comm"]).decode("utf8").splitlines()
    ):
        if "capella" in line.lower():
            match: t.Optional[re.Match] = re.match(r"(.*?)(\d+)(.*?)", line)
            if match is None:
                logger.error("Cannot identify PID of Capella process!")
                return
            pid: str = match.group(2)
            try:
                subprocess.check_call(["kill", "-" + str(signal), pid])
                logger.info("Killed process with PID " + pid)
            except subprocess.CalledProcessError as e:
                logger.exception(f"Could not kill Capella process: {e}")


def log_intro_messages():
    """Log some general information.

    Share Python interpreter in use and tell if we are running in an EASE context.
    Give a hint that one can enable debug level logging via an environment variable.

    """
    logger.info(f"Executed by: '{sys.executable}'.")
    logger.info(
        f"Running with debug mode {'enabled' if DEBUG else 'disabled'} "
        f"{'in' if IS_EASE_CTXT else 'not in'} EASE context."
    )
    if not DEBUG:
        logger.info(
            "Note that you can set an environment variable 'DEBUG=1' to get a debug "
            "level logging!\n"
        )
    if IS_EASE_CTXT:
        logger.info(f"Capella is{'' if isHeadless() else ' not'} run headless.")  # type: ignore # noqa
        timeout: int = getSystemProperty("org.eclipse.swtbot.search.timeout")
        logger.debug(
            f"System property 'org.eclipse.swtbot.search.timeout' is: {timeout} ms."
        )


def log_to_file(log_file_path: Path, mode: str = "w"):
    """Add logging to a file and log the path to the log file.

    Debug level will be INFO (default) or DEBUG, when an environment variable
    ``"DEBUG"`` has been set to ``"1"``.

    This function also filters some identified log messages which come with EASE itself
    to concentrate on own log messages only.

    Parameters
    ----------
    log_file_path
        Absolute path to the log file

    mode
        Write mode

    """
    file_hdl: logging.Handler = logging.FileHandler(
        filename=str(log_file_path), mode=mode
    )
    file_hdl.setLevel("DEBUG" if DEBUG else "INFO")
    file_hdl.setFormatter(formatter)
    file_hdl.addFilter(_MyLoggingFilter())
    logger.addHandler(file_hdl)
    logger.info(f"Log to '{log_file_path}'...")


def open_eclipse_perspective(name: str):
    """Open a named perspective in Eclipse.

    Parameters
    ----------
    name
        Name of the perspective

    """
    if BOT is None:
        raise exp.EaseNoSWTWorkbenchBotError
    BOT.menu("Window").menu("Perspective").menu("Open Perspective").menu(
        "Other..."
    ).click()
    logger.debug(f"Try to find Eclipse perspective '{name}'...")
    if not BOT.table().containsItem(name):
        logger.debug(
            f"Cannot find Eclipse perspective '{name}' "
            f"will search for '{name} (default)'..."
        )
        name = f"{name} (default)"
    if not BOT.table().containsItem(name):
        raise RuntimeError(
            f"Cannot find any Eclipse perspective '{name}' or " f"'{name} (default)'!"
        )
    try:
        BOT.table().getTableItem(name).select()
    except Exception as e:
        raise RuntimeError(
            f"Failed when selecting Eclipse perspective '{name}' to be opened!"
        ) from e
    logger.info(f"Open Eclipse perspective '{name}'...")
    click_button_with_label("Open")


def open_eclipse_view(category: str, title: str):
    """Show (open) the Eclipse view specified by its *category* and *title*.

    Parameters
    ----------
    category
        Category of the view (parent tree node in tree view of views)
    title
        Title of the view to be opened

    """
    if BOT is None:
        raise exp.EaseNoSWTWorkbenchBotError
    if is_eclipse_view_shown(title):
        return
    logger.debug(f"Show Eclipse view '{category}/{title}'...")
    BOT.menu("Window").menu("Show View").menu("Other...").click()
    category_node: t.Any = BOT.tree().getTreeItem(category)
    category_node.expand()
    view_node: t.Any = category_node.getNode(title)
    view_node.doubleClick()


def project_explorer_tree() -> t.Any:
    """Return the handle for the tree in the project explorer view.

    Returns
    -------
    t.Any
        Handle for the tree in the project explorer view

    """
    project_explorer_view: t.Any = BOT.viewByTitle("Project Explorer")
    project_explorer_bot: t.Any = project_explorer_view.bot()
    project_explorer_tree: t.Any = project_explorer_bot.tree()
    return project_explorer_tree


def workspace_path() -> Path:
    """Return the path to the current Eclipse workspace.

    Returns
    -------
    Path
        Absolute (resolved) path to the current Eclipse workspace

    """
    return Path(getWorkspace().getLocation().toString())


if __name__ == "__main__":
    log_file_dir: str = os.getenv("EASE_LOG_FILE_DIR", str(Path()))
    log_file_path: Path = Path(log_file_dir) / "ease.log"
    log_to_file(log_file_path=log_file_path)
    create_empty_workspace_with_ease_setup()
