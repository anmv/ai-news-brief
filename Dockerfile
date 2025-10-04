# Define function directory
ARG FUNCTION_DIR="/app"

FROM public.ecr.aws/lambda/python:3.11

# Install tar and gzip which are required for the uv installer
RUN yum install -y tar gzip

COPY requirements.txt /var/task/

# Install dependencies using uv and then clean up
RUN set -ex && \
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    # Use uv to install dependencies from requirements.txt
    /root/.local/bin/uv pip install --system --no-cache -r ${LAMBDA_TASK_ROOT}/requirements.txt && \
    # Clean up uv installation files
    rm -rf /root/.local && \
    # Remove pip as requested to reduce image size
    rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.11

# Copy function code
COPY ${FUNCTION_DIR} ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.lambda_handler" ]