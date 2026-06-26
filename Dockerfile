FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --requirement requirements.txt

COPY bot ./bot

RUN useradd --create-home --uid 10001 botuser
USER botuser

CMD ["python", "-m", "bot.main"]
