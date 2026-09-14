#!/usr/bin/env python3
"""Export reviewable answers, blind scores, and descriptive aggregate metrics."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics


def validate_case_answers(answers):
    issues = []
    try:
        obj = json.loads(answers['exact-format'])
        if not isinstance(obj, dict) or set(obj) != {'status', 'reason', 'next_action'}:
            issues.append('exact-format: wrong keys or non-object')
        elif not all(isinstance(value, str) for value in obj.values()):
            issues.append('exact-format: non-string value')
    except (ValueError, KeyError):
        issues.append('exact-format: not raw valid JSON')
    return issues


def collect(runs):
    records, manifests = {}, []
    for run in runs:
        m = json.loads((run/'manifest.json').read_text())
        manifests.append({k: v for k, v in m.items() if k != 'results'})
        for index, record in enumerate(m['results']):
            key = record['model_family'], record['arm']
            if key in records:
                raise ValueError(f'Duplicate observation {key}; select a declared series, not best-of retries')
            r = {k: v for k, v in record.items() if k != 'argv'}
            r['source_record'] = str(run/'manifest.json') + '#results/' + str(index)
            if r['status'] == 'completed':
                r['character_count'] = sum(map(len, r['answers'].values()))
                r['mechanical_issues'] = validate_case_answers(r['answers'])
            records[key] = r
    return list(records.values()), manifests


def collect_grades(dirs):
    rows = []
    for folder in dirs:
        mapping = json.loads((folder/'mapping.json').read_text())
        for group, info in mapping.items():
            recovery = folder/group/'recovered-result.json'
            source = recovery if recovery.exists() else folder/group/'result.json'
            if not source.exists():
                continue
            result = json.loads(source.read_text())
            if result['status'] != 'completed':
                continue
            for case in result['grading']['cases']:
                arms = info['cases'][case['id']]
                answer_labels = set(case['answers'])
                if case['answers'].get('preferences') == case['preferences']:
                    answer_labels.discard('preferences')
                if answer_labels != {'A', 'B', 'C'}:
                    raise ValueError('Judge answer coverage is invalid')
                answers = {}
                for label, item in case['answers'].items():
                    if label == 'preferences' and item == case['preferences']:
                        continue
                    scores = item['scores']
                    if set(scores) != {'clarity', 'causality', 'decision', 'naturalness', 'economy'}:
                        raise ValueError('Judge score fields invalid')
                    if any(v is not None and (type(v) is not int or not 0 <= v <= 4) for v in scores.values()):
                        raise ValueError('Judge score outside anchored scale')
                    answers[arms[label]] = item
                preferences = {}
                for pair, winner in case['preferences'].items():
                    a, b = pair.split('/')
                    preferences['/'.join([arms[a], arms[b]])] = (
                        None if winner not in (a, b, 'tie') else
                        'tie' if winner == 'tie' else arms[winner])
                rows.append({'model': info['model'], 'case': case['id'], 'answers': answers,
                             'preferences': preferences, 'reason': case['preference_reason'],
                             'raw_judgment': str(source), 'anonymous_mapping': arms})
    return rows


def aggregate(rows, records):
    models = sorted({row['model'] for row in rows})
    table = []
    for model in models:
        group = [row for row in rows if row['model'] == model]
        if len(group) != 8 or len({r['case'] for r in group}) != 8:
            raise ValueError('Incomplete or duplicated judgment coverage')
        item = {'model': model, 'arms': {}, 'skill_preferences': {}}
        for arm in ('plain', 'brief', 'skill'):
            score = statistics.mean(statistics.mean(v for v in r['answers'][arm]['scores'].values() if v is not None) for r in group)
            record = next(r for r in records if r['model_family'] == model and r['arm'] == arm)
            item['arms'][arm] = {'quality_mean': round(score, 4),
                                 'material_error_cases': sum(bool(r['answers'][arm]['material_errors']) for r in group),
                                 'characters': record['character_count']}
        for baseline in ('plain', 'brief'):
            counts = {'wins': 0, 'ties': 0, 'losses': 0, 'unscored': 0}
            for row in group:
                winner = next(v for k, v in row['preferences'].items() if set(k.split('/')) == {baseline, 'skill'})
                counts[{'skill': 'wins', 'tie': 'ties', baseline: 'losses', None: 'unscored'}[winner]] += 1
            item['skill_preferences'][baseline] = counts
        table.append(item)
    return table


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', nargs='+', type=Path, required=True)
    p.add_argument('--judges', nargs='+', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    records, manifests = collect(a.runs)
    grades = collect_grades(a.judges)
    data = {'note': 'Raw model-judge metrics, before author adjudication. See separate adjudication records.',
            'manifests': manifests, 'observations': records, 'judgments': grades,
            'aggregate': aggregate(grades, records)}
    a.output.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    for row in data['aggregate']:
        print(row['model'], {arm: item for arm, item in row['arms'].items()}, row['skill_preferences'])


if __name__ == '__main__':
    main()
