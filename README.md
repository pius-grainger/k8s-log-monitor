# K8s Log Monitor

**Intelligent Kubernetes log analysis with AI-powered recommendations**

Automatically detect and diagnose errors in your Kubernetes pods using pattern matching and OpenAI. Get instant fix recommendations for OutOfMemory errors, connection timeouts, database failures, and 15+ other common issues.

## ✨ Features

- 🔍 **17 Pre-configured Error Patterns** - Detects OOM, connection timeouts, database errors, HTTP 5xx, disk issues, and more
- 🤖 **AI-Powered Recommendations** - OpenAI GPT-4o-mini provides actionable fix suggestions
- ⚡ **Two Modes**: CLI for ad-hoc debugging, Continuous monitor for real-time alerting
- 🎯 **Multi-Namespace Support** - Monitor multiple namespaces simultaneously
- 🔔 **Smart Alerting** - Alert deduplication and severity-based filtering (CRITICAL, HIGH, MEDIUM, LOW)
- 💰 **Cost Tracking** - Shows token usage and estimated cost per analysis
- 🚀 **Production Ready** - Incremental log reading, proper logging, configurable intervals

## 📁 Project Structure

```
k8s-log-monitor/
├── cli/              # CLI tool for ad-hoc debugging
│   ├── debug-logs.py
│   ├── requirements-cli.txt
│   └── CLI-USAGE.md
├── k8s/              # Kubernetes manifests
│   ├── configmap.yaml
│   ├── rbac.yaml
│   └── deployment.yaml
├── docker/           # Continuous monitor
│   ├── Dockerfile
│   ├── monitor.py
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Option 1: CLI Tool (Recommended for ad-hoc debugging)

```bash
cd cli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-cli.txt
export OPENAI_API_KEY="your-key"
./debug-logs.py <pod-name> -n <namespace>
```

### Option 2: Continuous Monitor

```bash
# Build
cd docker
docker build -t log-monitor:latest .

# Deploy
cd ../k8s
kubectl create namespace monitoring
kubectl apply -f configmap.yaml
kubectl apply -f rbac.yaml
kubectl apply -f deployment.yaml

# View logs
kubectl logs -f -n monitoring deployment/log-monitor
```

## 📖 Documentation

- [CLI Usage Guide](cli/CLI-USAGE.md)
- [Test Pods](k8s/README-TESTS.md)

## ⚙️ Configuration

### Error Patterns
Edit `k8s/configmap.yaml` to add/modify patterns:
```yaml
{
  "name": "OutOfMemory",
  "regex": "OutOfMemoryError|OOMKilled|out of memory",
  "severity": "critical"
}
```

### Environment Variables
- `TARGET_NAMESPACES` - Comma-separated namespaces to monitor (default: "default")
- `ENABLE_LLM_RECOMMENDATIONS` - Enable AI recommendations (default: "false")
- `OPENAI_API_KEY` - Your OpenAI API key
- `POLL_INTERVAL_SECONDS` - Log polling interval (default: 30)
- `ALERT_DEDUPE_SECONDS` - Alert deduplication window (default: 60)
- `LLM_COOLDOWN_SECONDS` - LLM call cooldown per pod+error (default: 300)

## 💡 Use Cases

- **Incident Response**: Quickly diagnose production issues with AI recommendations
- **Development**: Catch errors early during local testing with Minikube
- **Monitoring**: Continuous alerting for critical errors across multiple namespaces
- **Cost Optimization**: Pay-per-use with CLI vs continuous monitoring

## 📊 Supported Error Types

OutOfMemory • ConnectionTimeout • NetworkError • DatabaseError • AuthenticationFailure • AuthorizationFailure • HTTP5xx • HTTP4xx • DiskFull • ReadOnlyFilesystem • CrashLoopBackOff • ImagePullError • ProbeFailures • TLS/SSL Errors • ThreadDeadlock • Application Exceptions

## 🤝 Contributing

Contributions welcome! Add new error patterns, improve AI prompts, or enhance the monitoring logic.

## 📝 License

MIT
