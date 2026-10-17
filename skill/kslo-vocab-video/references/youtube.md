# YouTube title and description (W3)

Deliver a YouTube title and description with every video. Generate them with `python3 $S/youtube_text.py`, which
writes `output/youtube.md`. Then read the text and check it against this guide before delivering. The format is fixed by
the delivered Unit 1 text (`templates/examples/unit1_youtube.md`). Keep every new unit consistent with it.

## Title

```
<video title> | Vocabulary Revision with Miss K | K S Lo English
```

- `<video title>` is `project.json` `title`, exactly as approved, e.g. "S2 Unit 1 Useful Words and Phrases". For other
  levels it is the teacher's title (W6).
- YouTube allows 100 characters at most. If the title would be longer, drop the middle part:
  `<video title> | K S Lo English`.

## Description (inside one code block in `youtube.md`, so it can be copied in one go)

Write these blocks in this order, with one blank line between them:

1. **Opening line:** "Revise the useful words and phrases from S2 Unit 1 with Miss K, your virtual English tutor!"
   For a non-standard title, use the title in place of "S2 Unit 1".
2. **How the video works:** "Look at each picture, use the first letters and the example sentence to guess the word or
   phrase, and say it aloud before the 3-second countdown ends. Then check your answer: Miss K says it for you, and
   you'll see its part of speech, Chinese meaning, definition and an example sentence."
   If the format changes, change this paragraph so it still describes what students actually see.
3. **Audience:** "Made for S2 students of HKMA K S Lo College. Great for quick revision before a dictation, quiz or test."
   (Use the project's level.)
4. **Chapters**, with timestamps taken from the timeline: `0:00 Welcome`, `Part 1: Phrases`, `Part 2: Words`, `Wrap-up`.
   YouTube needs the first chapter at 0:00, at least 3 chapters, and at least 10 s per chapter. Items (about 8.6 s
   each) are therefore never chapters.
5. **Item lists, in video order (phrases first):** `Phrases (13)` then a comma-separated list, a blank line, then
   `Words (17)` and its list. Use the **full DOCX headwords**, including "sth" / "sb" ("be combined with sth"), because
   that is what students study from. Never list display forms here.
6. **How to revise with this video:**
   1. Say each answer aloud before the countdown ends.
   2. Pause the video if you need more time.
   3. Watch again and see how many more you can get right.
   4. Use each word or phrase in a sentence of your own.
7. **Sign-off:** "Keep up the great work, K S Lo students!"
8. **Hashtags:** `#KSLoEnglish #S2English #EnglishVocabulary #VocabularyRevision #LearnEnglish` (`#S3English` etc. for
   other levels).

## Rules

- **Never mention AI, Manus, "generated", "machine" or how the video was made.** The script refuses banned words. Miss K
  is described only as "your virtual English tutor".
- Address the audience as "K S Lo students". Use British spelling (revise, practise, colour).
- Keep the tone warm and encouraging, without emoji.
- No item timestamps, no links unless the teacher gives them, and no claims about the school beyond the audience line.
- Deliver `output/youtube.md` together with the MP4. If the teacher edits the wording, apply the edit to
  `youtube_text.py` too, so later units stay consistent.
