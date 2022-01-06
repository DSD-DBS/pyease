# Copyright 2021 DB Netz AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
