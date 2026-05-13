FROM python:3.12-slim
WORKDIR /app
COPY backend/pyproject.toml ./pyproject.toml
RUN python - <<'PY'
import subprocess
import sys
import tomllib
from pathlib import Path

project = tomllib.loads(Path('pyproject.toml').read_text())
dependencies = project['project']['dependencies']
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', *dependencies])
PY
COPY backend/app ./app
RUN pip install --no-cache-dir --no-deps .
ENV LABELZONE_LOCAL_STORAGE_ROOT=/data/files
ENV LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
