# V2 format: reusable Miss K library (started 2026-10-17 17:50)

## User decisions (17:49)
- Option A: NO Miss K on quiz screens. Picture larger; small round Miss K badge near the countdown that glows with a
  sound-wave ring while she says the answer (voice-call style). No per-item Seedance clips any more.
- Pop-ups: Miss K slides in from the right ~3 s with one generic line, after every 5 items WITHIN each part, skipped if
  it falls on the last item of a part. Lines (rotate, no repeat; line 6 only for the last pop-up of a video):
  1 Great job! Keep going! | 2 You're doing really well. Let's keep going! | 3 Nice work! Here come some more.
  4 Brilliant! You're on a roll! | 5 Keep it up! You've got this! | 6 Almost there! Just a few more to go!
- Generic reusable intro / transition / outro (approved scripts), unit title only as on-screen text:
  intro: "Hello, K S Lo students! I'm Miss K, your virtual English tutor. Let's revise some useful words and phrases
  together. Look at each picture, think of the answer, and say it out loud before time runs out. Ready? Let's go!"
  transition: "Great job with the phrases! Now let's try some words!" (skip if unit has only one type)
  outro: "Fantastic work, K S Lo students! Keep revising these words and phrases, and try using them in your writing
  and speaking. See you next time!"  (wave ONLY on "See you next time")
- ORDER: phrases first (Part 1: Phrases), then words (Part 2: Words); table order within each part.
- Default item recording via carrier sentence (falling tone) to cut retakes.
- Show mockups of the new quiz screen and the pop-up FIRST.
- Make the reusable Miss K clips + update the skill. DO NOT rebuild Unit 1 (current video is usable).
- Upload all reference materials (character images, reusable assets incl. videos, vocab DOCX) to the ksloenglish GitHub
  so another Manus account can build Unit 2 with the same skill. gh is logged in as user ksloenglish (has private repo
  kslo-skills = skill backup vault). Plan: new private repo ksloenglish/kslo-vocab-video (skill + assets); skill gets a
  fetch script.

## Work dir: /home/ubuntu/ksvid_lib
- audio/vo/{intro,transition,outro,pop1..pop6}.wav  (Leda en-GB, "K S Low")

## Progress 17:58
- VO done: audio/vo/{intro 13.6s, transition 3.8s, outro (=outro_A, 10.4s, "KS Lowe" ok), pop1..pop6}. outro_v0_rushed rejected ("KSL").
- refs built (make_refs lines): intro 15s, transition 6, outro 12, pop1 4, pop2 5, pop3 4, pop4 4, pop5 5, pop6 5.
- 10 Seedance jobs started 17:56 -> clips/missk_{intro,transition,outro_A,outro_B,pop1..6}.mp4 (outro A/B: pick wave on "See you next time").
- Mockups: mockups/{A_quiz_countdown,B_quiz_reveal_badge_speaking,C_popup}.png from mockup.py (BD=172, badge at 1540,548,
  QP_W=1780, ripple +44px; popup bubble 1000x300 at (150,330), Bebas 128 line1 + coral bold 50 line2, "N of T done" + segment bar,
  Miss K mk_place(1.0)). Deferred ask sent 17:57 (mockups OK? private repo ksloenglish/kslo-vocab-video OK?). Default: go ahead.

## Implementation plan (skill v2 format)
- SIZE: library clips (~8 MB) can't go in the skill (11 MB limit) -> host on GitHub repo ksloenglish/kslo-vocab-video
  (private). Skill gets scripts/fetch_assets.sh (gh repo clone --depth 1 to ~/kslo-vocab-video) and init_project copies
  library from $KSLO_ASSETS (default ~/kslo-vocab-video/library). Old transition template removed from skill.
- Repo layout: README.md, skill/kslo-vocab-video/, library/ (clips mp4 CRF18, <name>_aligned.wav voice aligned to lips,
  library.json durations, refs, vo takes, prompts.md), character/ (missk_master_A/B.png, missk_neutral.png),
  brand/ (logo), vocab/ (DOCX), reference/unit1/ (illustrations as JPEG, items.json, youtube text); Unit 1 final v5 MP4
  is 255 MB -> GitHub RELEASE asset (repo file limit 100 MB). Tag old skill as v1 (per-item clips format) in git history.
- timeline.py: phrases first (init_project numbers phrases 1..P, then words); parts list by type; popup segment after
  every 5th item within a part unless last of part; lines 1-5 rotate, pop6 for the last pop-up; POP_DUR = clip dur + 0.3;
  schedule names intro/transition/outro/popN; WORD_AT voice onset 3.75 directly (no clips); no word_onsets.
- render.py: no Miss K on items, badge (from mockup.py) + QP_W 1780; badge speaking window = item voice dur
  (work/item_voice.json); part card: Miss K slides out right, part text cx 960, labels by type; transition/conclusion:
  slide in from right (op + dx 500) instead of corner grow; render_popup; conclusion chips phrases then words, skip zero.
- build_audio.py: aligned/intro.wav at OPEN_MK_IN, transition, outro at conclusion+TRANS_GROW, popups at popup start;
  whoosh on popup in/out; items from audio/items/NN.wav (new prep_items.py trims chosen take; fit_items obsolete).
- init_project: order phrases first; copy library clips + aligned wavs + work/clip_speech.json from library.json.
- Docs: SKILL.md workflow (no per-item clips; carrier-sentence takes by default), requirements (new decisions),
  missk_clips.md (library only), visual_spec (badge, popup), youtube_text chapters order.

18:02 CREDITS RAN OUT (creditNotEnough) - outro_B and pop3 still saved. Do NOT start new generation. Waiting: intro, transition, outro_A, pop1, pop6.

## Progress 18:12
- Seedance results: intro, transition, outro_A, outro_B, pop1-5 OK; pop6 FAILED (copyright false positive) -> stopgap
  library pop6 = pop2 clip retimed to pop6 voice. Credits exhausted (creditNotEnough) - no more generation.
- New skill script retime_clip.py: warps clip video so lips follow TTS phrases (merge shortest pauses to match counts;
  --gap 0.12 for short lines). Library built at /home/ubuntu/ksvid_lib/library: clips/ (retimed + idle), aligned/ (= refs),
  source_clips/ (raw Seedance), library.json, stab.json. intro: 2 phrases slowed x0.70/0.72 (Seedance rushed them).
  outro = outro_B (wave only on "See you next time"; verified at conclusion+11.0 s).
- Skill patched: timeline.py rewritten, render.py (patch_render_v2format.py + qp_size 1780, removed self.words),
  build_audio.py (intro/outro/pop voices + pop whooshes), init_project.py (phrases first, library copy from
  $KSLO_ASSETS/library incl. stab.json, clip_speech.json), prep_items.py NEW, prep_clips.py names.
- Test project /home/ubuntu/vtest_v2 (KSLO_ASSETS=/home/ubuntu/ksvid_lib): keyed, mixed, frames verified OK (sheet).
- TODO: preview mp4; docs (SKILL.md, requirements, missk_clips, visual_spec, voice_and_audio, youtube_text chapters);
  remove obsolete skill files (fit_items, make_refs words, align_vo?, clip_speech, templates missk_idle/transition/
  transition_aligned); fetch_assets.sh; GitHub repo staging + push + release (Unit 1 v5 255 MB); size check.
