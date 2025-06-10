# docker/rpi.Dockerfile
FROM arm32v7/python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry && poetry install --no-root
COPY . .
CMD ["poetry", "run", "python", "src/cli/main.py"]
