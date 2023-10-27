"""Main module."""

import logging

from europa_1400_tools.commands import app

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    app()
