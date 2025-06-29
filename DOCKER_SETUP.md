# Docker Setup for AWS Lambda Web Adapter

## Overview
AWS Lambda Web Adapter allows you to run web applications (like Flask) in Lambda without code changes. It acts as a proxy between Lambda's event/context model and your web app's HTTP requests.

## Required Files

### 1. Dockerfile
```dockerfile
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
```

### 2. SAM Template (template.yaml)
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 900  # 15 minutes max for newsletter processing
    MemorySize: 1024

Resources:
  AINewsBriefingFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      ImageConfig:
        Command: ["python", "web_app.py"]
      Environment:
        Variables:
          GEMINI_API_KEY: !Ref GeminiApiKey
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
        RootApi:
          Type: Api
          Properties:
            Path: /
            Method: ANY
    Metadata:
      Dockerfile: Dockerfile
      DockerContext: .

Parameters:
  GeminiApiKey:
    Type: String
    Description: Gemini API Key for AI processing
    NoEcho: true

Outputs:
  APIEndpoint:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

## How Lambda Web Adapter Works

### Local Development
```
HTTP Request → Flask App (port 5000) → Response
```

### In Lambda
```
Lambda Event → Web Adapter → HTTP Request → Flask App (port 5000) → HTTP Response → Web Adapter → Lambda Response
```

## Key Features

### Environment Variables
- `PORT=5000`: Port your Flask app runs on
- `AWS_LWA_INVOKE_MODE=response_stream`: Enables streaming responses
- Your Flask app still uses `load_dotenv()` normally

### Request Handling
- Web Adapter converts Lambda events to HTTP requests
- Your Flask routes work exactly the same
- Static files, templates, everything works normally

### Logging
- `print()` statements become CloudWatch logs automatically
- No code changes needed for logging
- All Flask debug output goes to CloudWatch

## Build and Deploy Process

### 1. Build locally
```bash
# Test the Docker image locally first
docker build -t ai-news-briefing .
docker run -p 5000:5000 -e GEMINI_API_KEY=your_key ai-news-briefing
```

### 2. Deploy with SAM
```bash
# Initialize SAM (first time only)
sam build

# Deploy
sam deploy --guided --parameter-overrides GeminiApiKey=your_api_key_here
```

### 3. Test the deployed API
```bash
# Your Flask app is now available at the API Gateway URL
curl https://your-api-id.execute-api.region.amazonaws.com/Prod/
curl https://your-api-id.execute-api.region.amazonaws.com/Prod/generate
```

## Benefits of This Approach

### Minimal Changes
- ✅ No code modifications to Flask app
- ✅ Same local development experience
- ✅ All existing routes work identically

### Cloud Native
- ✅ Auto-scaling with Lambda
- ✅ Pay-per-request pricing
- ✅ Built-in monitoring with CloudWatch
- ✅ API Gateway integration included

### Easy Debugging
- ✅ Same Flask error messages
- ✅ Print statements visible in logs
- ✅ Can test locally with Docker first

## Potential Issues & Solutions

### Cold Starts
- **Issue**: First request may be slower
- **Solution**: Use provisioned concurrency for critical applications

### Request Timeouts
- **Issue**: Lambda has 15-minute maximum
- **Solution**: Newsletter processing typically takes 2-5 minutes, so this is fine

### Memory Usage
- **Issue**: Large newsletters might use more memory
- **Solution**: Start with 1024MB, increase if needed

### Network Timeouts
- **Issue**: Article fetching might timeout
- **Solution**: Already handled in existing code with timeout parameters
