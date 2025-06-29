# Cloud Readiness Checklist

## Goal: Make AI News Briefing Engine ready for AWS Lambda deployment

Focus on three core requirements:
1. **All configuration in environment variables**
2. **True statelessness** 
3. **No local file storage**

## Current Status Analysis

### ✅ Configuration (Mostly Ready)
- `config.py` already uses env vars via `python-dotenv`
- API key handled via `GEMINI_API_KEY` environment variable
- Model settings in `config.py` - **GOOD**

### ❌ Statelessness (ISSUES FOUND)
**Problems identified:**
- Interactive Q&A mode in `main.py` uses `input()` - **BREAKS LAMBDA**
- 40+ `print()` statements throughout codebase - **NEEDS LOGGING**
- Core processing mixed with CLI interaction - **NEEDS SEPARATION**

### ✅ Local File Storage (GOOD)  
**Status:** No file write operations found - **READY**
- All processing stays in memory
- No temp files or local storage detected

## Action Items for Cloud Readiness

### 1. Environment Configuration
- [ ] Move all hardcoded config to environment variables
- [ ] Remove dependency on `.env` file (use Lambda environment instead)
- [ ] Ensure graceful fallbacks for missing config

### 2. Statelessness 
- [ ] Remove interactive Q&A from Lambda handler
- [ ] Ensure each execution is completely independent
- [ ] No global state between invocations

### 3. No Local Storage
- [ ] Audit all file operations
- [ ] Remove any temp file creation
- [ ] Keep all processing in memory

## Lambda Entry Point Strategy
Create `lambda_function.py` that:
- Accepts event/context parameters
- Runs the newsletter processing pipeline
- Returns results as JSON (no interactive elements)
- Handles errors gracefully

## Corrected Next Steps (Based on Code Audit)

**Priority 1**: Separate business logic from CLI interface
- Create stateless `process_newsletter()` function (no print/input statements)
- Extract core logic from `main.py` into reusable module

**Priority 2**: Replace print statements with structured logging
- 40+ print statements need to become logging or return values
- Remove all `input()` calls from core processing

**Priority 3**: Create Lambda entry point
- `lambda_function.py` that calls stateless processing function
- Returns JSON instead of printing to console

**Priority 4**: Test cloud-ready version locally (no interactive elements)
