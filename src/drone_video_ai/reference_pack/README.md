# Reference Pack (Capability 3)

Metadata-first exemplar dataset per `.claude/specs/drone-video-pipeline/spec.md`
(Capability 3) and `plan.md`'s "Exemplar record" schema section. See
`schema.py` for the `ExemplarRecord` shape and `storage.py` for the
storage-layout validator.

## Scope reminder (per spec Scope-out)

- No automated scraping or bulk downloading of any kind is implemented or
  permitted in this package -- every exemplar below is metadata + manual/
  agent-researched derived analysis only; no video/image file is ever
  downloaded or persisted for an `all-rights-reserved` record.
- The AC3.4 minimum ("exactly one manually-curated worked example") was
  satisfied by `skypixel11_africa_unseen_ellisvanjason.json`. Scaling past
  that one example is an explicit, ongoing user-directed decision (each
  further batch -- the 9-exemplar expansion, and any batch added since --
  was built at the repo owner's direct request to continue growing this
  pack) rather than an unattended/automated pipeline; it still respects the
  spec's boundaries: no bulk footage downloading, no automated "stream and
  discard" pipeline (every record is individually researched), and the pack
  stays internal/unshared. The remaining Open Question 6 sign-off items this
  does *not* cover (CC-BY-NC use in commercial contexts, direct creator
  outreach) remain open should either scenario come up.
- Actual footage-file retention (`local_media_path` non-null) is reserved
  strictly for exemplars individually verified as `cc-by` / `cc0` /
  `public-domain` / `owned` (spec line 38) -- never inferred from "it won an
  award" or "it's a public showcase". `storage.py` enforces this mechanically.
- `editorial_style` (added when the pack was extended toward short-form,
  Instagram-Reels-style content) captures qualitative pacing/cut/transition
  observations, honestly tagged via `review_method` ("live_playback_review" /
  "text_provenance_only" / "not_reviewed") -- see `schema.py`'s
  `EditorialStyle` dataclass. This is the "derived analysis... plus
  shot-length/cut/transition-style notes" the spec's Scope-in always
  described but the original schema never added a field for.

## YouTube Data API metadata refresh/expiry process (spec AC3.3)

Per the YouTube API Services Terms, metadata retrieved via the official
YouTube Data API must be refreshed or deleted within 30 calendar days of
retrieval. This project tracks that via each exemplar record's
`retrieval_date` field ("YYYY-MM-DD").

This process is currently **manual, not automated** (automating it is out of
scope for this spec -- see spec AC3.3 and Scope-out):

1. Before using any exemplar record's YouTube-Data-API-sourced fields
   (`title`, `creator`, `duration`, thumbnail/publish-date if later added) in
   any downstream comparison or report, check `retrieval_date` against
   today's date.
2. If more than 30 calendar days have elapsed:
   - Re-fetch the same fields via the YouTube Data API (or oEmbed, for the
     subset of fields oEmbed exposes) and update the record in place, bumping
     `retrieval_date` to the new retrieval date, **or**
   - If re-fetching is not done, delete the stale YouTube-API-sourced fields
     (or the whole record) rather than continuing to rely on data older than
     the Terms' 30-day window.
3. Fields sourced from oEmbed only (no API key, no quota) are not subject to
   the Data-API-specific 30-day clause, but `retrieval_date` should still be
   refreshed periodically as a matter of hygiene, since oEmbed responses can
   also go stale (e.g. a video is later removed or re-titled).

No cron job, scheduled task, or unattended API client exists for this
process today -- each check/refresh is a deliberate, human-reviewed action,
consistent with the spec's Scope-out constraint against automating the
"transient stream, analyze, discard" pattern beyond ad hoc, manual runs.
