
FROM python:3.11-slim

# Make a non-root user (optional but recommended)
ARG USER=appuser
ARG UID=1000
ARG GID=1000

RUN addgroup --system --gid ${GID} ${USER} &&         adduser --system --uid ${UID} --ingroup ${USER} ${USER}

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY src/ /app/src/

# Environment variables expected at runtime:
#   - NOTION_TOKEN: your Notion internal integration token
#   - ROOT_PAGE_ID: the target parent page id where the dashboard/databases will be created
ENV PYTHONUNBUFFERED=1

USER ${USER}

# Default command (run the bootstrapper)
CMD ["python", "/app/src/bootstrap_notion_task_hub.py"]
