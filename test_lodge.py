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


def test_set_extra_fields_on_logging(stream, monkeypatch):
    monkeypatch.setenv("LOG_EXTRA_FIELDS", '{"program":{"name":"testlog","version":"v1"}}')
    with import_lodge() as lodge:
        log = lodge.get_logger("testlog")
        log.info("Logging with extra fields")

    log_entry = stream.read()
    log_structured = json.loads(log_entry)

    assert log_structured["message"] == "Logging with extra fields"
    assert "program" in log_structured.keys()
    assert log_structured["program"]["name"] == "testlog"
    assert log_structured["program"]["version"] == "v1"


def test_set_base_fields_on_logging(stream, monkeypatch):
    monkeypatch.setenv("LOG_BASE_FIELDS", '{"message":"%(message)s","anotherField":"yes"}')
    with import_lodge() as lodge:
        log = lodge.get_logger("testlog")
        log.info("Logging other base fields")

    log_entry = stream.read()
    log_structured = json.loads(log_entry)

    assert log_structured["message"] == "Logging other base fields"
    assert log_structured["anotherField"] == "yes"


def test_import_proxy_log(stream, monkeypatch):
    monkeypatch.setenv("LOG_ENV", "DEV")

    class StubFrame:
        f_globals = {"__name__": "package.module.submodule"}

    with import_lodge() as lodge:
        monkeypatch.setattr(lodge, "currentframe", lambda x: StubFrame())
        lodge.log.info("logging with lodge.log")

    log_entry = stream.read()
    log_entry_splitted = log_entry.split('|')

    assert log_entry_splitted[-1] == " logging with lodge.log\n"
    assert log_entry_splitted[1] == " INFO "
    assert log_entry_splitted[2] == " package.module.submodule "


def test_proxy_log_warn_with_level_error_should_not_log(stream, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    from lodge import log
    log.warn("warn")

    log_entry = stream.read()

    assert log_entry == ""


def test_proxy_exception_method(stream):
    with import_lodge() as lodge:
        log = lodge.get_logger("test")
        try:
            1/0
        except ZeroDivisionError:
            log.exception("test_message")

    log_entry = stream.read()
    json_entry = log_entry.split("\n")[0]
    log_structured = json.loads(json_entry)

    assert log_structured["message"] == "test_message"
    assert log_structured["level"] == "ERROR"
    assert "Traceback (most recent call last)" in log_entry
    assert "ZeroDivisionError: division by zero" in log_entry
