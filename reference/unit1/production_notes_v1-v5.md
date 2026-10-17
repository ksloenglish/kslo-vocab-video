# S2 Unit 1 video – production notes

## User decisions
- Title: "S2 Unit 1 Useful Words and Phrases"; audience S2 students of HKMA K S Lo College ("K S Lo students").
- 16:9, 1080p, ~5 min. Blanks = first letter + 5 underscores per word (fixed length).
- "formulate strategies to do sth" -> display/say "formulate strategies to" (f_____ s_____ t_____).
- "a variety of sth" -> "a v_____ o_____" (keep single letter a).
- Strip trailing sth/sb. Miss K SAYS the shortened form. Full headword with sth shown in small text after reveal.
- Extras ALL YES: (a) after reveal show POS + Chinese meaning + sample sentence (item highlighted);
  (b) progress counter (7 / 30) + "Now let's try some phrases!" link after 17 words; (c) soft BGM under voice.
- Images: anime / original pocket-monster-like creatures, no text; based on sample sentence meaning.

## Data
- /home/ubuntu/ksvid/items.json (30 items: n, headword, display, is_phrase, question, blanks, pos_short, definition, zh, sentence, highlight[], slug)
- Illustrations: /home/ubuntu/ksvid/illus/NN_slug.png (2560x1440, all 30 done)

## Branding
- Logo: /home/ubuntu/ksvid/assets/logo_white.png = WHITE on transparent, 667x587: box with knocked-out "KSLO", "ENGLISH" below (condensed bold font like Bebas Neue). Use on navy.
- Fonts: /home/ubuntu/ksvid/assets/fonts (BebasNeue, Oswald[wght], Poppins Regular/Medium/SemiBold/Bold/ExtraBold/Italic, Nunito[wght]); CJK: /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc (TC idx 3? HK idx 4 – verify)

## Miss K
- Master (open smile): assets/missk_master.png ; neutral closed-mouth keyframe: assets/missk_neutral.png (2560x1440, green #00FF00 bg, navy blazer, coral bow, brown hair, gold star clip). Body approx x 880-1700 of 2560, full height.
- Voice: en-gb-csagent-8, language en-GB, style "bright, warm and cheerful"; says "K S Lo" as "K S Law" (correct local pronunciation).
- VO files (audio/): vo_greeting.wav 15.68s, vo_transition.wav 4.08s, vo_conclusion_v2.wav 13.24s (use v2), items/NN_slug.wav (per item, 0.64-1.66s)
- Seedance refs: audio/ref_greeting.wav (17s, voice @0.5s), ref_transition.wav (6s), ref_conclusion.wav (16s), ref_words_bK.wav (24s; 6 words, word k at 0.5+4k s)
- Seedance 2.5 clips (clips/): missk_idle.mp4 10s no audio; missk_greeting.mp4 17s; missk_transition.mp4 6s; missk_conclusion.mp4 16s; missk_words_b1..b5.mp4 24s (items 1-6,7-12,13-18,19-24,25-30). All first=last keyframe = neutral.

## Audio assets
- audio/bgm_a.mp3 (intro+words, ~180s), audio/bgm_b.mp3 (phrases+ending ~160s)
- SFX: sfx_logo_sting.mp3, sfx_whoosh.mp3, sfx_reveal.mp3, sfx_projector.mp3 (3s loop), sfx_finale.mp3; countdown beeps synthesized (1 kHz).

## Status / later decisions (21:34)
- USER: "Lo" in K S Lo must sound like "low" (NOT "law"). Fixed by splicing: audio/vo_greeting_final.wav, audio/vo_conclusion_final.wav (verified transcripts "KS Low").
- Seedance clips (24 fps, 1280x720) did NOT follow ref timing; they have their own speech timing. TTS aligned to clip lip timing by build_vo.py -> audio/aligned/{greeting,transition,conclusion}.wav (t=0 = clip start); word onsets per item in work/word_onsets.json (clip, onset, end, prev_off, next_on). work/clip_onsets.json raw.
- Keyed Miss K memmaps: clips/keyed/<name>.npy + meta.json (prep_missk.py, crop x0..x1 common). Body centre at 1280-frame x~645.
- Pipeline files: timeline.py (segments, total ~314 s), render.py (test/segs/all), build_vo.py, prep_missk.py. Audio mixer still to write (build_audio.py): VO item wavs at item start+WORD_AT-0.06; aligned greeting at opening+4.6; transition at trans+0.8; conclusion at conc+0.8; beeps at item+0.6/1.6/2.6; projector 0.6-3.6; reveal chime 3.6; whoosh at item start; logo sting ~0.3s; finale at outro start; bgm_a for opening..word 17, bgm_b from transition, ducking.

## Timing plan (per item 8.6 s)
- 0-0.6 card enters (whoosh); 0.6/1.6/2.6 countdown 3-2-1 with beeps (+projector loop); 3.6 time's up: reveal chime, answer, Miss K says word ~3.75; info + sentence; exit at 8.6.
- Layout 1920x1080: header y28-92 (small logo, title, progress); image card x70-1170 y115-734; question/answer panel x70-1430 y755-1050; right panel x1210-1870 y115-415 (countdown -> meaning card); Miss K keyed bottom-right (~650 px tall, centre x~1660).
- Opening: logo reveal + light sweep (~3s) -> title card -> Miss K greeting large on right -> shrinks to corner -> Part 1 Words -> items 1-17 -> Miss K transition large (Part 2 Phrases) -> items 18-30 -> conclusion large -> end card with logo & branding.

## V1 delivered 21:51 -> output/S2_Unit1_Useful_Words_and_Phrases.mp4 (314 s). USER FEEDBACK (22:10-22:21) for V2:
1. Logo must be transparent: NO glow/fill behind it (the white box with knocked-out KSLO letters is the logo itself; my SKY glow showed through the letters = "solid background"). Remove logo_glow everywhere.
2. Opening: logo appears centre, then do NOT minimise to top-left; logo must sit TOGETHER with the title "S2 Unit 1 Useful Words and Phrases" (title lockup). Small header logo in item screens may stay (subtle branding), but fade in, no fly.
3. Voice younger/anime: USER CHOSE "A: natural" = studio voice Leda, language_code en-GB, style "high pitch, bubbly, cheerful and excited inflection" (items: "clear, high pitch, bright and cheerful"). NO pitch lift. Text uses "K S Low" for correct pronunciation.
   New VO: audio/v2/vo_greeting.wav (16.08 s), vo_transition.wav (3.64), vo_conclusion.wav (13.08), items split audio/v2/items/NN_slug.wav (verified transcripts incl. "A variety of").
   Seedance refs: audio/v2/refs/word_NN.wav (5 s, word at 1.2 s), refs/greeting.wav (18 s, voice @0.5), transition.wav (6 s), conclusion.wav (15 s).
4. Arm glitch (e.g. 00:30): caused by idle<->multi-word-clip splices with 0.1 s crossfade cutting gestures. FIX: per-word Seedance clips clips/v2/missk_wNN.mp4 (5 s, first=last keyframe = assets/missk_neutral.png, hands clasped prompt) + idle played in ping-pong with sine time-warp tau(u)=(L/pi)*sin(pi*u/L) so every splice is neutral->neutral; small crossfades.
   New big clips: clips/v2/missk_greeting.mp4 (18 s), missk_transition.mp4 (6 s), missk_conclusion.mp4 (15 s), first=last neutral.
5. Position jump (e.g. 01:39): clips have different framing. FIX: stabilise every keyed clip to the neutral reference (similarity transform via feature matching + RANSAC, temporally smoothed per clip).
6. (22:21) POS label without full stop (v / n / adj / phr).
7. Blanks: one underscore per missing letter, spaced: "s _ _ _ _ _ _ _" (stunning = s + 7). Phrases: extra space between words: "n _   m _ _ _ _ _". "a variety of" -> "a   v _ _ _ _ _ _   o _" (single-letter word shown as is). Fit to panel width (shrink font if needed).
8. Miss K must say the full phrase "a variety of" (new recording includes "A").
Item timing plan: word clip placed so its speech onset = item WORD_AT (3.75); clip start ~2.55, end ~7.55; idle ping-pong between.

## V2 progress (22:34)
- 9. (22:33) Header chip: show 'ITEM' instead of WORDS/PHRASES next to "12 / 30" everywhere.
- Clips: clips/v2/missk_{greeting(18.08s),transition(6.08),conclusion(15.07),w01..w30(5.06)}.mp4. w04 original was zoomed 10% -> moved to missk_w04_zoomed.mp4; regenerating -> missk_w04_v2.mp4 (rename to missk_w04.mp4 when done). w19 said phrase at 0.05 s + stray sounds -> regenerating missk_w19_v2.mp4 (swap in, rerun clip_speech + stab for w19).
- prep_v2.py: per-clip similarity transform from first/last 0.7 s (neutral) SIFT->RANSAC, linear interp between; common zoom a (~1.011) about BODY_CX=632, top anchored; crop X0=160..X1=1120 -> clips/keyed2/<name>.npy + meta.json (x0=160). STAB_ONLY=1 env to only estimate. stab.json cached (delete entry to recompute).
- work/v2/clip_speech.json = speech segments of every v2 clip (dur, segs). Recompute snippet in history (python inline); needs rerun for new w04/w19.
- build_vo_v2.py: transcript-paired phrase alignment -> audio/aligned2/{greeting,transition,conclusion}.wav (t=0 = clip start), verified. Writes work/v2/word_onsets.json {n:{clip,onset,end,dur}}.
- Old keyed npy deleted (disk). v1 final video kept in output/.
- Renderer TODO: keyed2 source; global Miss K schedule (greeting@open+OPEN_MK_IN, wNN@item+WORD_AT-onset, transition@trans+0.8, conclusion@conc+0.8) with idle sine ping-pong between (neutral at both ends); remove logo_glow; opening lockup (logo stays centre, rises, title centred below, whole group slides left when Miss K enters); header logo fade-in; blanks per letter; POS w/o '.'; chip 'ITEM'; GREET_CLIP=18.08, TRANS_CLIP=6.08, CONC_CLIP=15.07.
- Audio TODO: build_audio.py -> v2 VO paths (items audio/v2/items/NN_slug.wav at item+WORD_AT-0.06; aligned2 clips at clip starts).
- (22:46) All 34 clips keyed (w04 + w19 regenerated, framing ok, zoom a=1.0112). render.py patched via patch_render_v2.py (from work/render_v1.py) + opening timing fix (logo rise 3.0-3.7, title t0=3.6). OPEN_MK_IN=5.4, total 315.13 s. check_mk.py: no pops in corner sections (only natural gestures in greeting/conclusion). build_audio.py repointed to aligned2 + v2/items; final_mix rebuilt.
- Full render job -> output/S2_Unit1_Useful_Words_and_Phrases_v2.mp4 (log work/render_v2.log). After: verify transcript + frames at 00:30, 01:39 equivalents, then deliver.
## V2 delivered 22:53 -> output/S2_Unit1_Useful_Words_and_Phrases_v2.mp4 (315.13 s). USER FEEDBACK 23:14 for V3:
1. Opening w/ Miss K: text LEFT-aligned like v1 (x=120), logo smaller, Miss K tag moved right next to Miss K.
2. Definition card: headword first then POS pill ("sustainable [adj]").
3. 'haggle' pronunciation weird (v2 take creaky/unvoiced).
4. Phrase blanks: reduce word gap (now WG=0.42*size, was 0.78).
5. Rising tone on many phrases -> re-record per item (single call each), choose takes by Praat final-rise metric (final_rise.py; >3 st = RISE).
6. Conclusion: stray 's' after "Fantastic work, K S Lo students" = v2 alignment copied tail 's' (ASR boundary mid-fricative) into phrase 2.
7. 05:02-05:04 unclear = phrase 3 tail + over-stretch. FIX: new conclusion TTS audio/v3/vo_conclusion.wav (unhurried) + build_vo_v3.py (cuts snapped to silences, stretch <=6%, no overlap) -> audio/aligned3/.
8. Final screen: removed 'S2 Unit 1 . Useful Words and Phrases' line.
User (23:16): show mockups ONLY for visuals; audio I check myself. Mockups: output/mockups_v3/{1_opening,1b_opening_motion,2_definition_card,4_phrase_blanks,8_final_screen}.png (render.py patched via patch_render_v3.py from work/render_v2.py). WAIT for approval before full render.
Audio item picks so far (audio/v3/items_raw): 07.wav, 14_A.wav (haggle voiced+falling), 17.wav, 18.wav, 22_A.wav, 26.wav. KEEP v2 for 19, 20, 28 (falling). Pending retakes: 21, 21_A, 24, 24_A, 25, 25_A, 11_A, 13, 30. v2 rising list: 17,21,22,24,25,26 (+ mild 11,13,18,30).
Plan for replaced items: trim, time-match to v2 item duration (atempo, onset aligned) so Seedance word-clip lips still match; write to audio/v3/items/NN_slug.wav; build_audio uses v3 if present.
V3 STATE 23:36: audio DONE (not yet in video). Items final picks -> audio/v3/items (make_items_v3.py): 07,13,14_A,17,18,21_Cw,22_A,24_A,25_Cw,26,30; others v2. Mixer uses v3 items + aligned3 greeting/conclusion (build_vo_v3.py, RMAX 1.15, silence-snapped cuts; greeting blip at 10.71 zeroed). audio/final_mix.wav rebuilt (v2 mix kept at work/final_mix_v2.wav). Previews: output/audio_preview_v3/*.mp3.
Visual mockups sent; WAITING for approval. Then: rm -rf work/segs; python3 render.py all 6; concat + mux -> output/S2_Unit1_Useful_Words_and_Phrases_v3.mp4.
Round 2 (23:49): LOCK_LOGO_CY=222, OUT_DY=68 (outro centred). Full render started via run_v3.sh -> output/S2_Unit1_Useful_Words_and_Phrases_v3.mp4
V3 FINAL 00:00: output/S2_Unit1_Useful_Words_and_Phrases_v3.mp4 (315.13 s). Item 24 swapped to 24_Cw (calm carrier take; 24_A had an emphatic final 'with' heard as 'with one' in the mix). 22 kept 22_A (22_C rose). Audio-only re-mux from work/video_only.mp4.
## V3 delivered 00:01. USER FEEDBACK 00:10 for V4:
1. 'unique' (12) sounds quieter. Finding: items vary +-2 dB in max short-term loudness (pyloudnorm, 400 ms); unique -1.2 dB vs median, lowest peak (-9.6). FIX: loudness-match all items in build_audio (max short-term LUFS to common target) + small extra for 12.
2. 'a variety of' (27): 'of' too short/unclear -> re-record (carrier 'A variety of. That's the phrase.' etc), pick clearest/longest 'of', falling tone; make_items_v3 PICK 27.
3. Conclusion: Miss K waves BEFORE saying 'See you next time' -> inspect clips/v2/missk_conclusion.mp4 ~11-15 s; fix (re-time or regenerate clip).
Only audio + conclusion segment need redo; video_only.mp4 segs in work/segs (re-render only conclusion seg, re-concat).
V4 DONE 00:27 -> output/S2_Unit1_Useful_Words_and_Phrases_v4.mp4 (315.13 s).
- build_audio: items loudness-matched (max short-term 400 ms -> ITEM_ST -18.2, clip +-3 dB) + ITEM_EXTRA {12: +1.0}; unique gain +2.58 dB.
- 27 = 27_Ew_fit ('The next phrase is: a variety of' carrier; 'a variety' atempo 0.85, 'of' natural 0.42 s; NOSTRETCH in make_items_v3).
- Conclusion clip replaced by clips/v4/missk_conclusion_B.mp4 (Seedance, ref audio/v3/ref_conclusion_v4.wav): hands clasped until final line, wave 13.3-14.45 s over 'See you next time' (13.74-14.41). Old clip kept as clips/v2/missk_conclusion_wave_early.mp4. Re-stabilised/keyed, re-aligned (aligned3/conclusion.wav), only seg 33 re-rendered.
V5 DONE 05:43 -> output/S2_Unit1_Useful_Words_and_Phrases_v5.mp4 (316.63 s). User asked final logo screen to fade to black.
- timeline OUTRO_DUR 6.5 -> 8.0; render_outro fade = eio(prog(t, OUTRO_DUR-3, OUTRO_DUR-1)) then black hold 1 s.
- build_audio music b: fade_out 2.6, ends TOTAL-1.0 (silent during black). Only seg 34 re-rendered. v4 backups in work/v4/.
