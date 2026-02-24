import click
from natsort import natsorted
from tabulate import tabulate
from swsscommon.swsscommon import ConfigDBConnector
from swsscommon.swsscommon import SonicV2Connector
import utilities_common.cli as clicommon


CFG_TBL = "PORT_TX_ERR_MONITOR"
STATE_TBL = "PORT_TX_ERR_MONITOR_TABLE"


@click.group(name="port-tx-err-monitor", cls=clicommon.AliasedGroup)
@click.pass_context
def port_tx_err_monitor(ctx):
    """Show port TX error monitor information"""
    pass


@port_tx_err_monitor.command("config")
@click.pass_context
def show_config(ctx):
    """Show port TX error monitor configuration"""
    db = ConfigDBConnector()
    db.connect()
    entry = db.get_entry(CFG_TBL, "CONFIG")
    if not entry:
        click.echo("No port TX error monitor configuration found.")
        return
    header = ["Threshold", "Window(s)", "Enabled"]
    row = [entry.get("threshold", "N/A"),
           entry.get("window_sec", "N/A"),
           entry.get("enabled", "N/A")]
    click.echo(tabulate([row], header, tablefmt="simple"))


@port_tx_err_monitor.command("status")
@click.pass_context
def show_status(ctx):
    """Show port TX error monitor status"""
    db = SonicV2Connector(host="127.0.0.1")
    db.connect(db.STATE_DB)
    sep = db.get_db_separator(db.STATE_DB)
    keys = db.keys(db.STATE_DB, STATE_TBL + sep + "*")
    if not keys:
        click.echo("No port TX error monitor status entries found.")
        return
    header = ["Port", "Status", "Error Count"]
    rows = []
    for key in natsorted(keys):
        name = key.split(sep, 1)[1]
        data = db.get_all(db.STATE_DB, key)
        sv = data.get("status", "N/A")
        label = "OK" if sv == "ok" else "ERROR" if sv == "error" else sv
        rows.append([name, label, data.get("error_count", "0")])
    click.echo(tabulate(rows, header, tablefmt="simple"))
