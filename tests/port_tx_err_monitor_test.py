import os
import pytest
from click.testing import CliRunner
from utilities_common.db import Db

import config.main as config
import show.main as show


class TestPortTxErrMonitorConfig(object):

    config_set_cmd = config.config.commands["port-tx-err-monitor"].commands["set"]
    config_disable_cmd = config.config.commands["port-tx-err-monitor"].commands["disable"]

    @classmethod
    def setup_class(cls):
        os.environ["UTILITIES_UNIT_TESTING"] = "1"

    @classmethod
    def teardown_class(cls):
        os.environ["UTILITIES_UNIT_TESTING"] = "0"

    def test_config_set_valid(self):
        db = Db()
        runner = CliRunner()
        obj = {"db": db.cfgdb}

        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "100", "--window", "10", "--enabled", "true"],
            obj=obj,
        )
        assert result.exit_code == 0, result.output

        entry = db.cfgdb.get_entry("PORT_TX_ERR_MONITOR", "CONFIG")
        assert entry["threshold"] == "100"
        assert entry["window_sec"] == "10"
        assert entry["enabled"] == "enabled"

    def test_config_set_disabled(self):
        db = Db()
        runner = CliRunner()
        obj = {"db": db.cfgdb}

        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "50", "--window", "5", "--enabled", "false"],
            obj=obj,
        )
        assert result.exit_code == 0, result.output

        entry = db.cfgdb.get_entry("PORT_TX_ERR_MONITOR", "CONFIG")
        assert entry["enabled"] == "disabled"

    def test_config_set_invalid_threshold(self):
        runner = CliRunner()
        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "0", "--window", "10", "--enabled", "true"],
        )
        assert result.exit_code != 0

    def test_config_set_invalid_window(self):
        runner = CliRunner()
        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "100", "--window", "0", "--enabled", "true"],
        )
        assert result.exit_code != 0

    def test_config_set_invalid_enabled(self):
        runner = CliRunner()
        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "100", "--window", "10", "--enabled", "yes"],
        )
        assert result.exit_code != 0

    def test_config_set_missing_options_no_existing(self):
        runner = CliRunner()
        db = Db()
        obj = {"db": db.cfgdb}
        result = runner.invoke(self.config_set_cmd, ["--threshold", "100"], obj=obj)
        assert result.exit_code != 0

    def test_config_set_no_options(self):
        runner = CliRunner()
        db = Db()
        obj = {"db": db.cfgdb}
        result = runner.invoke(self.config_set_cmd, [], obj=obj)
        assert result.exit_code != 0

    def test_config_partial_update_threshold(self):
        db = Db()
        runner = CliRunner()
        obj = {"db": db.cfgdb}

        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "100", "--window", "10", "--enabled", "true"],
            obj=obj,
        )
        assert result.exit_code == 0, result.output

        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "200"],
            obj=obj,
        )
        assert result.exit_code == 0, result.output

        entry = db.cfgdb.get_entry("PORT_TX_ERR_MONITOR", "CONFIG")
        assert entry["threshold"] == "200"
        assert entry["window_sec"] == "10"
        assert entry["enabled"] == "enabled"

    def test_config_partial_update_enabled(self):
        db = Db()
        runner = CliRunner()
        obj = {"db": db.cfgdb}

        result = runner.invoke(
            self.config_set_cmd,
            ["--threshold", "100", "--window", "10", "--enabled", "true"],
            obj=obj,
        )
        assert result.exit_code == 0, result.output

        result = runner.invoke(
            self.config_set_cmd,
            ["--enabled", "false"],
            obj=obj,
        )
        assert result.exit_code == 0, result.output

        entry = db.cfgdb.get_entry("PORT_TX_ERR_MONITOR", "CONFIG")
        assert entry["threshold"] == "100"
        assert entry["window_sec"] == "10"
        assert entry["enabled"] == "disabled"

    def test_config_disable(self):
        db = Db()
        runner = CliRunner()
        obj = {"db": db.cfgdb}

        runner.invoke(
            self.config_set_cmd,
            ["--threshold", "100", "--window", "10", "--enabled", "true"],
            obj=obj,
        )

        result = runner.invoke(self.config_disable_cmd, [], obj=obj)
        assert result.exit_code == 0, result.output

        entry = db.cfgdb.get_entry("PORT_TX_ERR_MONITOR", "CONFIG")
        assert not entry


class TestPortTxErrMonitorShowConfig(object):

    show_config_cmd = show.cli.commands["port-tx-err-monitor"].commands["config"]

    @classmethod
    def setup_class(cls):
        os.environ["UTILITIES_UNIT_TESTING"] = "1"

    @classmethod
    def teardown_class(cls):
        os.environ["UTILITIES_UNIT_TESTING"] = "0"

    def test_show_config_empty(self):
        runner = CliRunner()
        result = runner.invoke(self.show_config_cmd, [])
        assert result.exit_code == 0
        assert "No port TX error monitor configuration found" in result.output
