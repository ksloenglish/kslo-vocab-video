# YouTube titles and descriptions

Generate and deliver YouTube copy for **every completed unit video**, without waiting for the teacher to ask.
Match the friendly, practical style of the approved Unit 1 upload:
`https://www.youtube.com/watch?v=qyCHApdUaDA`.
The default wording is embedded in `scripts/youtube_text.py`; no live YouTube access is needed for normal builds.
The asset repository also contains `reference/unit1/S2_Unit1_YouTube_Title_and_Description.md` as a historical example.

## Title

Use the teacher's exact video title from `project.json` followed by:

```text
<video title> | Vocabulary Revision with Miss K | K S Lo English
```

For example:

```text
S2 Unit 2 Useful Words and Phrases | Vocabulary Revision with Miss K | K S Lo English
```

Do not add version numbers, production notes, creature-style labels or extra promotional claims.
Validate the title length before delivery. If it exceeds 100 characters, propose a shorter version for the teacher;
do not silently alter an approved custom title.

## Description structure

Keep the approved Unit 1 wording and these sections, changing only the level, unit, chapter times, lists and counts
as needed for the actual video:

1. Friendly opening: “Revise the useful words and phrases from <level> Unit <unit> with Miss K, your virtual English tutor!”
2. Explain the picture/first-letter guessing activity, saying answers aloud before the 3-second countdown ends,
   and checking Miss K's pronunciation, part of speech, Chinese meaning, definition and example sentence.
3. State the HKMA K S Lo College audience and quick revision before a dictation, quiz or test.
4. **Chapters:** Welcome, Part 1, Part 2 when present, and Wrap-up. Derive timestamps from the **final timeline**;
   do not copy Unit 1 times or its old words-first order. Normal format v2 is phrases first, then words.
5. List all featured **full headwords** in actual part order with accurate counts. Keep source placeholders such
   as sb/sth/A/B/v-ing in this list even if quiz answers and audio use a shortened form. Do not invent extra items.
6. **How to revise with this video:** say answers aloud; pause for more time; watch again to improve; use each item
   in a sentence of your own.
7. Close with “Keep up the great work, K S Lo students!”
8. Use `#KSLoEnglish #<level>English #EnglishVocabulary #VocabularyRevision #LearnEnglish`.

Never mention AI, Manus, “generated”, model names or how the video was produced. Do not claim a fully British
accent or other properties not verified in the final video. Do not add Pokémon/franchise branding to the copy.

## Generate, check and deliver

Run:

```bash
VOCAB_PROJECT=/absolute/project/path python3 $S/youtube_text.py
```

This writes the complete ready-to-copy **`output/youtube.md`**, containing separate title and description sections.
`finalize.sh` runs it automatically after both ordinary finalization and image-only finalization. Run it separately
when only YouTube copy is requested; do not re-render the video.

Check the level/unit, title, actual part order, headwords/counts and final chapter times before delivery.
The generator validates title and description lengths and excludes production wording. For very short videos,
it may need manual chapter adjustment; never advertise invalid individual 8.6-second item chapters.
If timing, item lists, part order or the title changes, regenerate the copy; image-only revisions with unchanged
content/timing should retain identical copy.

Deliver the MP4 **and link `output/youtube.md`** together. If the user explicitly asks for the text in chat,
provide title and description in separate copyable text blocks. This step creates copy only; do not upload a
video or publish/edit YouTube metadata without a separate user request.
