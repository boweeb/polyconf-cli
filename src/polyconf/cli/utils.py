"""CLI Utilities."""

import json
import logging
from typing import TYPE_CHECKING, Any

from polyconf.core.model import Context
from rich import print as rich_print
from rich.console import Console
from rich.highlighter import JSONHighlighter
from rich.panel import Panel
from rich.pretty import Pretty


# if TYPE_CHECKING:
#     from polyconf.core.model import Context


log = logging.getLogger(__name__)


def report_result(context: Context, output: str) -> None:
    """Report result."""
    log.info("Result Status: %s", context.status)

    out_map = {
        "primitive": context.result.as_native_value,
        "serialized": context.result.serialize(),
        "raw": context.result,
    }

    rich_print(
        Panel(
            Pretty(out_map[output]),
            title="Result",
        ),
    )


def print_json(data: dict[str, Any]):
    """Pretty print json to stdout."""
    json_string = json.dumps(data, indent=4)
    json_console = Console(
        highlighter=JSONHighlighter(),
        stderr=False,
    )
    json_console.print(json_string)
