#!/usr/bin/env python3
import json
import re
import sys
import argparse
from kubernetes import client, config
import openai
import os

def load_patterns():
    with open('../k8s/configmap.yaml', 'r') as f:
        content = f.read()
        json_start = content.find('{')
        json_str = content[json_start:].strip().rstrip('|').strip()
        return json.loads(json_str)['patterns']

def check_logs(logs, patterns):
    matches = []
    for line in logs.split('\n'):
        if not line.strip():
            continue
        for pattern in patterns:
            if re.search(pattern['regex'], line, re.IGNORECASE):
                matches.append({'line': line, 'pattern': pattern})
    return matches

def get_openai_recommendation(matches, pod_name):
    if not matches:
        return None, None
    
    errors_summary = "\n".join([f"- [{m['pattern']['name']}] {m['line']}" for m in matches[:5]])
    
    prompt = f"""Analyze these errors from Kubernetes pod '{pod_name}':

{errors_summary}

Provide:
1. Root cause analysis
2. Specific fix recommendations
3. Prevention strategies"""

    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    
    usage = response.usage
    cost = (usage.prompt_tokens * 0.00015 + usage.completion_tokens * 0.0006) / 1000
    
    return response.choices[0].message.content, {
        'prompt_tokens': usage.prompt_tokens,
        'completion_tokens': usage.completion_tokens,
        'total_tokens': usage.total_tokens,
        'cost': cost
    }

def main():
    parser = argparse.ArgumentParser(description='Debug K8s pod logs with AI recommendations')
    parser.add_argument('pod', help='Pod name')
    parser.add_argument('-n', '--namespace', default='default', help='Namespace')
    parser.add_argument('--tail', type=int, default=100, help='Number of log lines')
    args = parser.parse_args()

    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    print(f"Fetching logs from {args.namespace}/{args.pod}...")
    logs = v1.read_namespaced_pod_log(args.pod, args.namespace, tail_lines=args.tail)
    
    patterns = load_patterns()
    matches = check_logs(logs, patterns)
    
    print(f"\n{'='*80}")
    print(f"Found {len(matches)} error(s) matching known patterns:")
    print(f"{'='*80}\n")
    
    for m in matches:
        print(f"[{m['pattern']['severity'].upper()}] {m['pattern']['name']}")
        print(f"  {m['line']}\n")
    
    if matches and os.getenv('OPENAI_API_KEY'):
        print(f"\n{'='*80}")
        print("AI RECOMMENDATIONS:")
        print(f"{'='*80}\n")
        recommendation, usage = get_openai_recommendation(matches, args.pod)
        print(recommendation)
        
        if usage:
            print(f"\n{'='*80}")
            print("TOKEN USAGE:")
            print(f"{'='*80}")
            print(f"Prompt tokens: {usage['prompt_tokens']}")
            print(f"Completion tokens: {usage['completion_tokens']}")
            print(f"Total tokens: {usage['total_tokens']}")
            print(f"Estimated cost: ${usage['cost']:.6f}")
    elif matches:
        print("\nSet OPENAI_API_KEY environment variable to get AI recommendations")

if __name__ == '__main__':
    main()
