#!/usr/bin/env python3

import logging
import sys
import json
from typing import Any

import click
from rich.console import Console
from rich.highlighter import JSONHighlighter

from polyconf.core.model import Context
from polyconf.core.registry import Registry
import polyconf.plugins
from polyconf.core.utils import pipe


log = logging.getLogger(__name__)


def print_json(data: dict[str, Any]):
    """Pretty print json to stdout."""
    json_string = json.dumps(data, indent=4)
    json_console = Console(
        highlighter=JSONHighlighter(),
        stderr=False,
    )
    json_console.print(json_string)


# CLI ROOT
@click.group
@click.option("--verbose", "-v", is_flag=True, default=False, help="Use debug level logging.")
@click.pass_context
def root(ctx, verbose):
    """PolyConf.

    Collects configuration from many sources and composes a layered view of the result.
    The primary use case is as an imported configuration library.
    This CLI provides a way to explore PolyConf behavior ad hoc.
    """
    ctx.ensure_object(dict)
    ctx.obj |= {
        "verbose": verbose,
    }


@root.command
@click.option("--app-name", "-n", default="widget", help='VPC product [eg. "cdw"]')
@click.option("--select-plugin", "-p", multiple=True, default=["ALL"], help="Select plugin for use.")
def resolve(app_name, select_plugin):
    """Resolve configuration."""
    registry = Registry(selected_plugins=select_plugin)
    registry.init_plugins(polyconf.plugins, logger=log)

    context_initial = Context(
        app_name=app_name,
        app_prefix="JIRA",
        # given={"a": "b", "c": "d"},  # Not easily practical with CLI; just noting it here.
    )
    context_result = pipe(context_initial, *registry.plugins)

    log.info(f'Result Status: "{context_result.status}"')
    print_json(context_result.as_obj)


@root.command("list")
def list_():
    """List plugins available via discovery."""
    registry = Registry(selected_plugins=["ALL"])
    registry.init_plugins(polyconf.plugins)
    log.info(f"Discovered plugins: {list(registry.discovered_plugins.keys())}")


@root.command
def explain():
    """Not implemented yet."""
    click.echo("Not implemented yet")


def main():
    root(show_default=True)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
