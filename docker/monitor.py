import json
import re
import os
import time
import logging
import openai
from kubernetes import client, config
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('log-monitor')

def load_patterns():
    with open('/config/patterns.json', 'r') as f:
        return json.load(f)['patterns']

def compile_patterns(patterns):
    return [(p, re.compile(p['regex'], re.IGNORECASE)) for p in patterns]

def check_log_line(line, compiled_patterns):
    for pattern, regex in compiled_patterns:
        if regex.search(line):
            return pattern
    return None

llm_cache = {}
LLM_COOLDOWN = int(os.getenv('LLM_COOLDOWN_SECONDS', '300'))

def get_llm_recommendation(pattern_name, log_line, pod_name):
    cache_key = f"{pattern_name}:{pod_name}"
    now = time.time()
    
    if cache_key in llm_cache and now - llm_cache[cache_key] < LLM_COOLDOWN:
        return "(cached - cooldown active)"
    
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        prompt = f"""Error detected in Kubernetes pod '{pod_name}':
Error Type: {pattern_name}
Log: {log_line}

Provide a concise fix recommendation (2-3 sentences):"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        llm_cache[cache_key] = now
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "LLM unavailable"

seen_alerts = {}
ALERT_DEDUPE_SECONDS = int(os.getenv('ALERT_DEDUPE_SECONDS', '60'))

def trigger_alert(pod_name, namespace, pattern, log_line):
    alert_key = f"{namespace}:{pod_name}:{pattern['name']}"
    now = time.time()
    
    if alert_key in seen_alerts and now - seen_alerts[alert_key] < ALERT_DEDUPE_SECONDS:
        return
    
    seen_alerts[alert_key] = now
    logger.warning(f"ALERT [{pattern['severity'].upper()}] - {pattern['name']} | Pod: {namespace}/{pod_name}")
    logger.info(f"Log: {log_line.strip()}")
    
    if os.getenv('ENABLE_LLM_RECOMMENDATIONS', 'false').lower() == 'true':
        recommendation = get_llm_recommendation(pattern['name'], log_line, pod_name)
        logger.info(f"Recommendation: {recommendation}")
    
    logger.info("-" * 80)

def monitor_logs():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    
    v1 = client.CoreV1Api()
    compiled_patterns = compile_patterns(load_patterns())
    
    target_namespaces = [ns.strip() for ns in os.getenv('TARGET_NAMESPACES', 'default').split(',')]
    poll_interval = int(os.getenv('POLL_INTERVAL_SECONDS', '30'))
    since_seconds = int(os.getenv('SINCE_SECONDS', '60'))
    
    logger.info(f"Monitoring namespaces: {', '.join(target_namespaces)}")
    logger.info(f"Loaded {len(compiled_patterns)} patterns")
    
    last_check = {}
    
    while True:
        try:
            for namespace in target_namespaces:
                try:
                    for pod in v1.list_namespaced_pod(namespace).items:
                        if pod.status.phase == 'Running':
                            pod_key = f"{namespace}:{pod.metadata.name}"
                            try:
                                if pod_key not in last_check:
                                    logs = v1.read_namespaced_pod_log(
                                        pod.metadata.name, 
                                        namespace, 
                                        since_seconds=since_seconds
                                    )
                                    last_check[pod_key] = time.time()
                                else:
                                    logs = v1.read_namespaced_pod_log(
                                        pod.metadata.name, 
                                        namespace, 
                                        since_seconds=int(time.time() - last_check[pod_key])
                                    )
                                    last_check[pod_key] = time.time()
                                
                                for line in filter(None, logs.split('\n')):
                                    matched = check_log_line(line, compiled_patterns)
                                    if matched:
                                        trigger_alert(pod.metadata.name, namespace, matched, line)
                            except Exception as e:
                                logger.debug(f"Error reading logs for {pod_key}: {e}")
                except Exception as e:
                    logger.error(f"Error monitoring namespace {namespace}: {e}")
            time.sleep(poll_interval)
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(poll_interval)

if __name__ == '__main__':
    monitor_logs()
