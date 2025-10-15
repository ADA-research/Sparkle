"""Package meta file."""

import importlib.metadata

__name__ = "sparkle"
__version__ = importlib.metadata.version(__name__)

description = importlib.metadata.metadata(__name__)["Summary"]
licence = importlib.metadata.metadata(__name__)["License-Expression"]
authors = importlib.metadata.metadata(__name__)["Author"]
contact = importlib.metadata.metadata(__name__)["Maintainer-email"].split(", ")[-1]
