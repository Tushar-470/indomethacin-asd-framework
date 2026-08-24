import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

terms = [
    'thermodynamic miscibility predicted',
    'objective quantitative performance',
    's_lit',
    'literature evidence score',
    'literature_evidence_score',
    '5 criteria',
    '5-criterion',
    '5-dimensional'
]

results = {'active': {}, 'historical_archived': {}}

for dirpath, dirnames, filenames in os.walk('.'):
    if '.git' in dirpath or 'node_modules' in dirpath or '.system_generated' in dirpath or '.pytest_cache' in dirpath or 'dist' in dirpath:
        continue
    is_archive = 'archive' in dirpath or 'stale_content_audit.json' in dirpath
    category = 'historical_archived' if is_archive else 'active'
    
    for f in filenames:
        if f.endswith(('.py', '.ts', '.tsx', '.json', '.yaml', '.md', '.csv', '.html')):
            if f == 'stale_content_audit.json' or f == 'audit_stale_terms.py':
                continue
            p = os.path.join(dirpath, f).replace('\\', '/')
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    for i, line in enumerate(fp, 1):
                        for term in terms:
                            if term.lower() in line.lower():
                                entry = f'{p}:{i} -> {line.strip()[:110]}'
                                results[category].setdefault(term, []).append(entry)
            except Exception as e:
                pass

print('=== ACTIVE V1.5 OCCURRENCES ===')
for term in terms:
    matches = results['active'].get(term, [])
    print(f'Term: "{term}": {len(matches)} matches')
    for m in matches[:10]:
        print(f'  [ACTIVE] {m}')

print('\n=== HISTORICAL / ARCHIVED OCCURRENCES ===')
for term in terms:
    matches = results['historical_archived'].get(term, [])
    print(f'Term: "{term}": {len(matches)} matches')
