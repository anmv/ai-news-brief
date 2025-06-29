FROM public.ecr.aws/lambda/python:3.11

# Install Lambda Web Adapter extension
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.7.0 /lambda-adapter /opt/extensions/lambda-adapter

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

# Set the command to run your Flask app
CMD ["python", "web_app.py"]

# Environment variables for Lambda Web Adapter
ENV PORT=5000
ENV AWS_LWA_INVOKE_MODE=response_stream
