# Use Python 3.13 slim as base (matches your pyproject.toml requirement)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv (for dependency management)
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the app with uvicorn (binds to 0.0.0.0 for external access)
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]