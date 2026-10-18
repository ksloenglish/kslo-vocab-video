# Sharing the skill and asset repository

## Verified access status

On **19 October 2026**, the owner explicitly authorised changing **`ksloenglish/kslo-vocab-video` from private to PUBLIC**:

<https://github.com/ksloenglish/kslo-vocab-video>

Verified anonymous repository-page and API access, raw `library/library.json`, the main-branch ZIP endpoint and unauthenticated Git `ls-remote`. Public Git transport initially lagged behind the visibility change; a subsequent no-cache check succeeded. Do not interpret that transient as a requirement for colleagues to log in.

This is a dated observation, not a permanent assumption. If access fails in a future task, check live visibility (`gh repo view … --json visibility,isPrivate,url`) or unauthenticated HTTP status before diagnosing. Do not change repository visibility or grant collaborator permissions without the owner's instruction. A public repo exposes tracked files, commit history and release assets; check for credentials/private records before any newly authorised publication. Public access is not a blanket copyright licence, so retain existing rights/notices rather than assigning new licences without approval.

## Colleague setup

1. Share the updated `.skill` attachment/card or the `skill/kslo-vocab-video/` directory in the repository. Colleagues add it to **My Skills** in their own Manus accounts.
2. The public asset repo needs **no owner-specific GitHub permission, GitHub account or GitHub integration just to download/clone it**. GitHub integration is optional for authenticated Git operations; use ordinary HTTPS Git if it is absent:

   ```bash
   git clone --depth 1 https://github.com/ksloenglish/kslo-vocab-video.git ~/kslo-vocab-video
   ```

   The skill's `scripts/fetch_assets.sh` selects an available authenticated `gh` clone or public HTTPS fallback. Alternatively download the GitHub ZIP. Unzip an archive to a clean directory and set `KSLO_ASSETS`; do not expect `git pull` to work on an unzipped folder without `.git`.
3. All required video-library, character, branding, Unit 1 reference and S2 vocabulary assets are in this repository. The bundled `original_creature_design.md` is the fallback for colleagues without the separate teacher-created card skill; do not send them to its unrelated private repos.
4. Ask, for example: **“Use kslo-vocab-video to make S2 Unit 3 from the vocabulary DOCX, retaining Miss K and the approved video format.”** Keep the speaking-list/pilot approval gates. For a level other than S2, supply the full item list and exact title first.

## Apply an updated skill beyond the current sandbox

A file update in `/home/ubuntu/skills/kslo-vocab-video/` applies to this sandbox. Deliver its **`SKILL.md` as an attachment** so Manus packages the whole directory into the skill card. Offer **Add to My Skills** to save/replace the user's stored skill for future tasks. Do not claim the global account skill has changed merely because local files were edited; it requires that frontend action. Share the same updated package with colleagues so they do not install an older repository snapshot.

Keep the repository's `skill/kslo-vocab-video/` snapshot synchronised with a verified release, but never mix per-unit videos/audio/illustrations into the small skill package. Publishing a skill snapshot does not authorise rebuilding accepted videos or changing their assets.
