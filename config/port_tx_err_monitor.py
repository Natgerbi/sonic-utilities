import click
from swsscommon.swsscommon import ConfigDBConnector
from .validated_config_db_connector import ValidatedConfigDBConnector

CFG_TABLE = "PORT_TX_ERR_MONITOR"
CFG_KEY = "CONFIG"


@click.group(name="port-tx-err-monitor")
@click.pass_context
def port_tx_err_monitor(ctx):
    """Port TX error monitor configuration"""
    config_db = ValidatedConfigDBConnector(ConfigDBConnector())
    config_db.connect()
    ctx.obj = {"db": config_db}


@port_tx_err_monitor.command("set")
@click.option("--threshold", type=click.IntRange(min=1),
              help="Max acceptable TX error delta within the time window")
@click.option("--window", type=click.IntRange(min=1),
              help="Evaluation time window in seconds")
@click.option("--enabled", type=click.Choice(["true", "false"]),
              help="Enable or disable monitoring")
@click.pass_context
def set_config(ctx, threshold, window, enabled):
    """Set port TX error monitor configuration"""
    if threshold is None and window is None and enabled is None:
        ctx.fail("At least one of --threshold, --window, or --enabled must be provided")

    db = ctx.obj["db"]
    existing = db.get_entry(CFG_TABLE, CFG_KEY) or {}

    entry = dict(existing)
    if threshold is not None:
        entry["threshold"] = str(threshold)
    if window is not None:
        entry["window_sec"] = str(window)
    if enabled is not None:
        entry["enabled"] = "enabled" if enabled == "true" else "disabled"

    if not all(entry.get(f) for f in ("threshold", "window_sec", "enabled")):
        ctx.fail("Missing required fields. On first setup all options "
                 "(--threshold, --window, --enabled) must be provided")

    try:
        db.set_entry(CFG_TABLE, CFG_KEY, entry)
    except ValueError as e:
        ctx.fail("Invalid ConfigDB. Error: {}".format(e))


@port_tx_err_monitor.command("disable")
@click.pass_context
def disable(ctx):
    """Remove port TX error monitor configuration"""
    db = ctx.obj["db"]
    try:
        db.set_entry(CFG_TABLE, CFG_KEY, None)
    except ValueError as e:
        ctx.fail("Invalid ConfigDB. Error: {}".format(e))
