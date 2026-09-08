FROM python:3.13-slim AS base
WORKDIR /app

# markitdown[pdf] needs these at build/runtime for PDF and mime-type handling
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# install deps first so this layer is cached across code-only changes.
# README.md has to come along too: pyproject.toml declares it as the
# package readme, and `uv sync` fails building project metadata without it.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

EXPOSE 50051
CMD ["uv", "run", "python", "-m", "owlbot.server"]
