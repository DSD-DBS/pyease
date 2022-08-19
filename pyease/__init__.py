# SPDX-FileCopyrightText: Copyright DB Netz AG and the pyease contributors
# SPDX-License-Identifier: Apache-2.0

"""The pyease package."""
from importlib import metadata

try:
    __version__ = metadata.version("pyease")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0+unknown"
del metadata
