# K8s Log Debugger CLI

Ad-hoc tool to analyze pod logs with AI recommendations.

## Setup

```bash
cd cli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-cli.txt
export OPENAI_API_KEY="your-key-here"
```

## Usage

```bash
# Basic usage
./debug-logs.py error-generator

# Specify namespace
./debug-logs.py error-generator -n default

# Get more log lines
./debug-logs.py error-generator --tail 200

# Without OpenAI (just pattern matching)
unset OPENAI_API_KEY
./debug-logs.py error-generator
```

## Example Output

```
Fetching logs from default/error-generator...

================================================================================
Found 4 error(s) matching known patterns:
================================================================================

[HIGH] ConnectionTimeout
  [1] Thu Nov 20 17:18:15 UTC 2025 ERROR: connection timeout exceeded

[HIGH] DatabaseError
  [1] Thu Nov 20 17:18:15 UTC 2025 ERROR: database connection failed

================================================================================
AI RECOMMENDATIONS:
================================================================================

1. Root cause: Connection timeouts suggest network issues or overloaded services
2. Fix: Increase timeout values, check network policies, scale backend services
3. Prevention: Add retry logic, implement circuit breakers, monitor service health
```

## Cost

- OpenAI GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
- Typical analysis: ~$0.0001-0.0003 per pod
- Token usage and cost shown after each analysis
