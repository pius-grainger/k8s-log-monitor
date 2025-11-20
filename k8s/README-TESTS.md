# Test Pods

Generate various error patterns for testing the log monitor.

## Deploy Test Pods

```bash
kubectl apply -f test-pods.yaml
```

## Test Pods Available

1. **oom-error-pod** - OutOfMemory errors
2. **connection-error-pod** - Connection timeouts and database errors
3. **auth-error-pod** - Authentication failures
4. **http-error-pod** - HTTP 5xx errors
5. **disk-error-pod** - Disk space errors

## View Logs

```bash
# View specific pod
kubectl logs -f oom-error-pod

# Test CLI tool
cd ../cli
./debug-logs.py oom-error-pod
./debug-logs.py connection-error-pod
```

## Monitor Alerts

```bash
# Watch continuous monitor
kubectl logs -f -n monitoring deployment/log-monitor
```

## Cleanup

```bash
kubectl delete -f test-pods.yaml
```
