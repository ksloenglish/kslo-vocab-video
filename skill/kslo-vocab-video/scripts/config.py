"""Shared configuration for the K S Lo English vocab-video pipeline.

Project root = $VOCAB_PROJECT (or the current directory). Every script imports this module.
Fixed project layout (created by init_project.py):

  project.json                 per-video text + options (see init_project.py for fields)
  items.json                   ordered items (words first, then phrases)
  illus/NN_slug.png            16:9 illustrations (2560x1440 preferred)
  assets/                      logo_white.png, missk_neutral.png, fonts/   (copied from templates)
  audio/sfx_*.mp3, bgm_a.opus, bgm_b.opus                                  (copied from templates)
  audio/items_raw/*.wav        every TTS take (raw) and extracted takes (*w.wav)
  audio/items/NN_slug.wav      FINAL per-item voice, trimmed (prep_items.py); work/item_voice.json = durations
  audio/refs/                  Seedance audio references (make_refs.py; only when regenerating library clips)
  audio/aligned/<name>.wav     library voice lines, already lip-matched to clips/missk_<name>.mp4 (t=0 = clip start)
  clips/missk_<name>.mp4       library clips (copied by init_project.py): idle intro transition outro pop1..pop6
  clips/keyed/<name>.npy       keyed + stabilised RGBA frames (prep_clips.py) + meta.json + stab.json
  work/clip_speech.json        library clip durations; work/library.json = library index (from GitHub)
  work/segs/, work/test/       render output; output/ final MP4
"""
import json, os

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.environ.get('VOCAB_PROJECT', os.getcwd()))
R = ROOT

_pj = os.path.join(ROOT, 'project.json')
PROJECT = json.load(open(_pj)) if os.path.exists(_pj) else {}


def proj(key, default=None):
    return PROJECT.get(key, default)


def p(*parts):
    """Absolute path inside the project."""
    return os.path.join(ROOT, *parts)


def load_items():
    return json.load(open(p('items.json')))


def clip_path(name):
    return p('clips', f'missk_{name}.mp4')


def word_clip_names(n_items):
    return [f'w{i:02d}' for i in range(1, n_items + 1)]


CJK_FONT = os.environ.get('CJK_FONT', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
CJK_INDEX = int(os.environ.get('CJK_INDEX', '4'))   # 4 = Traditional Chinese (Hong Kong) face in Noto CJK .ttc
