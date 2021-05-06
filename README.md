# lodge

A structured logging package in Python simple to use.

## Features

* Easy to use
* Env var configurations
* Structured production log ready!
* Options to customize fields
* Set log level by module
* Based on stdlib

## Install

Add to your setup as:
```python
  ...
  " lodge==<VERSION>",
  ...
```
or install with pip
```
pip install lodge
```

## Getting Started

```python
>>> from lodge import logger

>>> logger.info("Is that simple?")
{"message": "Is that simple?", "timestamp": "2021-03-21 14:26:54,838", "level": "INFO"}
```

### Global level with env var config

```python
$ export LOG_LEVEL=ERROR

>>> from lodge import logger

>>> logger.info("This will not appear")
>>> logger.error("Oh no")
{"message": "Oh no", "timestamp": "2021-03-21 14:26:54,839", "level": "ERROR"}
```

### Module level with env var config

```python
$ export PACKAGE_MODULE1_LOG_LEVEL=ERROR
$ export PACKAGE_MODULE2_LOG_LEVEL=INFO

# package/module1.py
>>> from lodge import logger

>>> logger.info("Module 1 info")
>>> logger.error("Module 1 error")
{"message": "Module 1 error", "timestamp": "2021-03-21 14:26:54,839", "level": "ERROR"}

# package/module2.py
>>> from lodge import logger

>>> logger.info("Module 2 info")
{"message": "Module 2 info", "timestamp": "2021-03-21 14:26:54,839", "level": "INFO"}
>>> logger.error("Module 2 error")
{"message": "Module 2 error", "timestamp": "2021-03-21 14:26:54,839", "level": "ERROR"}
```

### Change format to easier read on development
```python
$ export LOG_ENV=DEV

# package/module1.py
>>> from lodge import logger

>>> logger.info("a message")
2021-03-21 14:34:47,273 | INFO | package.module1 | a message
```

### Add extra fields
```python
$ export LOG_EXTRA_FIELDS='{"fausto":"olokinho"}'

>>> from lodge import logger

>>> logger.info("o loko")
{"message": "o loko", "timestamp": "2021-03-21 14:45:51,431", "level": "INFO", "fausto": "olokinho"}
```

### Overwrite base fields
```python
$ export LOG_BASE_FIELDS='{"message":"%(message)s"}'

>>> from lodge import logger

>>> logger.info("simple message")
{"message": "simple message"}
```
