FROM python:3.13-alpine

# Install necessary dependencies
RUN apk add --no-cache bash build-base libffi-dev openssl-dev postgresql-dev gcc musl-dev libffi-dev python3-dev

# Set working directory
WORKDIR /app

ENV PYTHONPATH="/app:${PYTHONPATH:-}"

# Create virtual environment
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH

# Activate the venv for future commands
ENV PATH="$VENV_PATH/bin:$PATH"

# Upgrade pip and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the app source code
COPY . .

# Make sure entrypoint is executable
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x ./entrypoint.sh

# Use virtualenv python for entrypoint execution
ENTRYPOINT ["/app/entrypoint.sh"]
