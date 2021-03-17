import json
from contextlib import contextmanager

import pytest


@contextmanager
def import_lodge():
    import lodge
    yield lodge
    del lodge


@pytest.fixture
def stream(mocker):
    messages = []  # noqa

    def write(msg):
        return messages.append(msg)

    def read():
        try:
            return messages.pop()
        except IndexError:
            return ''

    stderr = mocker.patch("lodge.DEFAULT_LOG_STREAM")
    stderr.write = write
    stderr.read = read

    return stderr


def test_log_info_defaults(stream):
    with import_lodge() as lodge:
        log = lodge.get_logger("test")
        log.info("Something")

    log_entry = stream.read()
    log_structured = json.loads(log_entry)

    assert log_structured["message"] == "Something"
    assert log_structured["level"] == "INFO"


def test_set_global_level_debug_should_log_debug(stream, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    with import_lodge() as lodge:
        log = lodge.get_logger("test")
        log.debug("debuging")

    log_entry = stream.read()
    log_structured = json.loads(log_entry)

    log_structured = json.loads(log_entry)
    assert log_structured["message"] == "debuging"
    assert log_structured["level"] == "DEBUG"


def test_set_global_level_error_should_not_log_debug(stream, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    with import_lodge() as lodge:
        log = lodge.get_logger("test")
        log.debug("Globally defined")

    log_entry = stream.read()

    assert log_entry == ""


def test_set_globally_specific_logger(stream, monkeypatch):
    monkeypatch.setenv("MYLOG_TEST_LOG_LEVEL", "ERROR")
    with import_lodge() as lodge:
        log1 = lodge.get_logger("mylog.test")
        log2 = lodge.get_logger("myotherlog.test")

        log1.info("Will not log")
        log2.info("Will log")

    log_entry = stream.read()
    assert "Will log" in log_entry

    log_entry = stream.read()
    assert log_entry == ''


def test_set_format_on_dev(stream, monkeypatch):
    monkeypatch.setenv("LOG_ENV", "DEV")
    with import_lodge() as lodge:
        log = lodge.get_logger("testlog")
        log.info("Here goes a message")

    log_entry = stream.read()
    log_entry_splitted = log_entry.split('|')

    assert log_entry_splitted[-1] == " Here goes a message\n"
    assert log_entry_splitted[1] == " INFO "
    assert log_entry_splitted[2] == " testlog "
