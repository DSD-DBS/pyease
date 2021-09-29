"""Module with exeptions for use of EASE with Python.

.. seealso::

    The acronym EASE stands for "Eclipse Advanced Scripting Environment".
    Further information: https://www.eclipse.org/ease/

"""
# Standard library:
import logging
import typing as t

logger: logging.Logger = logging.getLogger()


class EaseError(Exception):
    """Raised when an unexpected error occurred."""


class EaseButtonClickError(EaseError):
    """Raised when a button cannot be clicked."""

    def __init__(self, button: str):
        self.button: t.Any = button

    def __str__(self):
        extramsg: str = ""
        if not self.button.isEnabled():
            extramsg = " The button is not enabled."
        return f"Cannot click the button '{self.button}'!{extramsg}"


class EaseButtonNotFoundError(EaseError):
    """Raised when a button cannot be found by a specified label."""

    def __init__(self, label: str):
        self.label: str = label

    def __str__(self):
        msg: str = f"Cannot find a button labeled '{self.label}'!"
        logger.exception(msg)
        return msg


class EaseNoSWTWorkbenchBotError(EaseError):
    """Raised when there is no SWTWorkbenchBot."""

    def __str__(self):
        return "There is not SWTWorkbenchBot available!"
