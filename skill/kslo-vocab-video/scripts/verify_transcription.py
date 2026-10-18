#!/usr/bin/env python3
"""Verify authoritative ASR JSON, never rendered terminal snippets.

Isolated take (strictly one expected answer):
  python3 verify_transcription.py --transcript /abs/take_transcription.json --expected boost
Full video (uses VOCAB_PROJECT items.json and timeline.SEGMENTS):
  VOCAB_PROJECT=/project python3 verify_transcription.py --transcript /abs/final_transcription.json

ASR-inserted articles are failures by default.  Use --allow-asr-articles deliberately only
when reporting a known ASR normalisation; this is still spelling evidence, never evidence
of stress, accent, vowel quality, or a final stop release.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


def norm(text):
    """Normalise punctuation/case for ASR word comparisons only."""
    if not isinstance(text, str):
        raise ValueError('transcript text must be a string')
    return re.sub(r'[^a-z0-9]+', ' ', text.lower().replace("'", '')).strip()


def _require_transcript(data):
    if not isinstance(data, dict):
        raise ValueError('ASR JSON must be an object')
    if not isinstance(data.get('segments'), list) or not isinstance(data.get('full_text'), str):
        raise ValueError('ASR JSON must contain segments[] and full_text')
    texts = []
    for i, segment in enumerate(data['segments']):
        if not isinstance(segment, dict) or not isinstance(segment.get('text'), str):
            raise ValueError(f'ASR JSON segment {i} has no text')
        texts.append(segment['text'])
    joined, full = norm(' '.join(texts)), norm(data['full_text'])
    if not full:
        raise ValueError('ASR JSON full_text is empty')
    if not joined:
        raise ValueError('ASR JSON contains no segment text')
    if joined != full:
        raise ValueError('ASR JSON segments and full_text disagree; do not guess from terminal output')
    return full


def _matches(text, expected, allow_articles=False):
    words = norm(expected).split()
    if not words:
        raise ValueError('expected answer is empty after normalisation')
    between = r'\s+'
    if allow_articles:
        between = r'\s+(?:(?:a|an|the)\s+)?'
    pattern = r'\b' + between.join(map(re.escape, words)) + r'\b'
    return list(re.finditer(pattern, text))


def check_isolated(data, expected, allow_articles=False):
    """Require both JSON representations to contain one and only one answer phrase."""
    text = _require_transcript(data)
    strict = _matches(text, expected)
    accepted = strict
    normalised = None
    if len(strict) != 1 and allow_articles:
        optional = _matches(text, expected, allow_articles=True)
        if len(optional) == 1:
            accepted = optional
            if norm(optional[0].group()) != norm(expected):
                normalised = optional[0].group()
    if len(accepted) != 1 or norm(text) != norm(accepted[0].group()):
        raise ValueError(f'isolated ASR must be exactly one {norm(expected)!r}; heard {text!r}')
    return dict(mode='isolated', expected=norm(expected), transcribed=accepted[0].group(), count=1,
                optional_asr_article_normalisation=normalised,
                phonetic_claims='none (ASR spelling does not verify stress, accent, or final consonants)')


def _timeline_item_numbers(segments):
    return [s['item'] for s in segments if s.get('kind') == 'item']


def _library_marker(line):
    """ASR often omits a popup's second sentence; its opening marker is the checkable cue."""
    return norm(re.split(r'[.!?]', line, maxsplit=1)[0])


def check_full(data, items, timeline_segments, allow_articles=False, check_library=False, pop_lines=None):
    """Require current project answers exactly once, in current timeline item order."""
    text = _require_transcript(data)
    item_numbers = [item.get('n') for item in items]
    if not item_numbers or any(not isinstance(n, int) for n in item_numbers):
        raise ValueError('items.json must contain numbered items')
    if _timeline_item_numbers(timeline_segments) != item_numbers:
        raise ValueError('timeline item order does not match items.json; refusing an order check')
    cursor, checks, article_notes = 0, [], []
    for item in items:
        expected = norm(item.get('display', ''))
        strict = _matches(text, expected)
        matches = strict
        used_optional = False
        if len(strict) != 1 and allow_articles:
            optional = _matches(text, expected, allow_articles=True)
            if len(optional) == 1:
                matches, used_optional = optional, norm(optional[0].group()) != expected
        if len(matches) != 1:
            raise ValueError(f'item {item["n"]} {expected!r}: expected exactly once, found {len(matches)}')
        match = matches[0]
        if match.start() < cursor:
            raise ValueError(f'item {item["n"]} {expected!r}: answer is out of timeline order')
        cursor = match.end()
        found = norm(match.group())
        record = dict(n=item['n'], expected=expected, transcribed=found, count=1)
        checks.append(record)
        if used_optional:
            article_notes.append(record)
    library = dict(requested=check_library, checks=[],
                   manual_note='ASR library-line checking was not requested; listen manually if it is relevant.')
    if check_library:
        if not isinstance(pop_lines, dict):
            raise ValueError('current POP_LINES are required for --check-library')
        library_cursor = 0
        uncertain = []
        for segment in timeline_segments:
            if segment.get('kind') != 'popup':
                continue
            expected = _library_marker(pop_lines.get(segment.get('pop'), ''))
            matches = _matches(text, expected)
            in_order = len(matches) == 1 and matches[0].start() >= library_cursor
            if in_order:
                library_cursor = matches[0].end()
            else:
                uncertain.append(segment['pop'])
            library['checks'].append(dict(pop=segment['pop'], expected_marker=expected,
                                          asr_count=len(matches), asr_in_order=in_order))
        library['asr_exact'] = not uncertain
        library['manual_note'] = ('ASR popup markers were inconclusive for ' + ', '.join(uncertain) +
                                  '; manually listen to the complete library line(s).') if uncertain else \
                                 'ASR popup markers passed; manually listen if pronunciation or recognition is uncertain.'
    return dict(mode='full', all_answers_exactly_once=True, answer_order_correct=True,
                timeline_item_order=item_numbers, answers=checks,
                optional_asr_article_normalisations=article_notes,
                library=library,
                phonetic_claims='none (manually listen/check stress, accent, and final stops when needed)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transcript', required=True, help='authoritative manus-speech-to-text JSON file')
    parser.add_argument('--expected', help='isolated answer expected in this JSON')
    parser.add_argument('--allow-asr-articles', action='store_true',
                        help='deliberately permit/report a/an/the inserted between expected words')
    parser.add_argument('--check-library', action='store_true',
                        help='also ASR-check current popup lines; manually listen if ASR is uncertain')
    parser.add_argument('--report', help='optional JSON report path (full mode defaults to work/transcription_verification.json)')
    args = parser.parse_args()
    try:
        transcript = Path(args.transcript).expanduser().resolve()
        data = json.loads(transcript.read_text())
        if args.expected:
            result = check_isolated(data, args.expected, args.allow_asr_articles)
            report = Path(args.report).expanduser() if args.report else None
        else:
            root_text = os.environ.get('VOCAB_PROJECT')
            if not root_text:
                raise ValueError('full mode requires VOCAB_PROJECT')
            root = Path(root_text).resolve()
            items = json.loads((root / 'items.json').read_text())
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from timeline import SEGMENTS, POP_LINES
            result = check_full(data, items, SEGMENTS, args.allow_asr_articles, args.check_library, POP_LINES)
            report = Path(args.report).expanduser() if args.report else root / 'work/transcription_verification.json'
        result['transcript_file'] = str(transcript)
        result['strict_articles'] = not args.allow_asr_articles
        if report:
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            result['report'] = str(report)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f'Transcription verification FAILED: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
