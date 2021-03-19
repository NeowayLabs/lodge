FROM python:3.9-slim as dev

WORKDIR /lodge

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONDONTWRITEBYTECODE=pleasedont

RUN pip install pytest pytest-cov pytest-mock mypy flake8 bandit


from dev

COPY setup.cfg setup.py lodge.py ./
RUN pip install .
