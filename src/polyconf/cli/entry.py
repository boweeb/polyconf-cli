#!/usr/bin/env python3

import logging
import sys
from dataclasses import asdict

import click
from polyconf.core.model import Context
from polyconf.core.registry import Registry

import polyconf.plugins
from polyconf.cli import utils as u


log = logging.getLogger(__name__)


# CLI ROOT
@click.group
@click.option("--verbose", "-v", is_flag=True, default=False, help="Use debug level logging.")
@click.pass_context
def root(ctx, verbose: bool):
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
@click.option("--select-plugin", "-p", multiple=True, default=("ALL",), help="Select plugin for use.")
@click.option(
    "--output", "-o", default="primitive", type=click.Choice(["primitive", "serialized", "raw"]), help="Output format."
)
def resolve(app_name: str, select_plugin: tuple[str, ...], output: str) -> None:
    """Resolve configuration."""
    select_plugin_list: list[str] = list(select_plugin)
    log.debug("Selecting plugins: %s", select_plugin_list)

    registry = Registry(selected_plugins=select_plugin_list)
    registry.init_plugins(polyconf.plugins, logger=log)

    result = registry.resolve(
        Context(
            app_name=app_name,
            app_prefix="JIRA",
            # given={"a": "b", "c": "d"},  # Not easily practical with CLI; just noting it here.
        )
    )

    u.report_result(context=result, output=output)


@root.command("list")
def list_():
    """List plugins available via discovery."""
    registry = Registry(selected_plugins=["ALL"])
    registry.init_plugins(polyconf.plugins, logger=log)
    log.info("Discovered plugins: %s", list(registry.discovered_plugins.keys()))


@root.command
def explain():
    """Not implemented yet."""
    click.echo("Not implemented yet")


def main() -> None:
    """Entry point."""
    root(show_default=True)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
