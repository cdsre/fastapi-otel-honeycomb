FROM python:3.12.0

ARG REQUIREMENTS_FILE=/tmp/requirements.txt
ENV PYTHON_APP_FILE=/usr/local/bin/fastapi-otel-example.py

COPY requirements.txt "${REQUIREMENTS_FILE}"
RUN pip install -r "${REQUIREMENTS_FILE}"


COPY main.py /usr/local/bin/fastapi-otel-example.py
CMD ["opentelemetry-instrument", "python", "/usr/local/bin/fastapi-otel-example.py"]