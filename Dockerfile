FROM python:3.8-slim-buster
LABEL maintainer="csaybar -- Copernicus Master in Digital Earth (CDE)"

# Global ARG
ARG YOUR_ENV
ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

# Install Python3-dev
RUN apt-get update && apt-get install -y python3-dev build-essential

# Install poetry
RUN pip install poetry==$POETRY_VERSION

# Copy all files
COPY . .

# Init the project
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
