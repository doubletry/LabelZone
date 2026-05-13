FROM python:3.12-slim
WORKDIR /app
COPY backend/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir .
COPY backend/app ./app
ENV LABELZONE_LOCAL_STORAGE_ROOT=/data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
