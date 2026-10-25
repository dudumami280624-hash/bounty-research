# Video Source Intake

This directory is the durable intake layer for public video research collected with yt-dlp.

## Required record

Each item must have:

- source URL and platform
- title, channel/author, publication date
- retrieval date and yt-dlp version
- subtitle language and type
- SHA-256 hashes for metadata and transcript
- evidence status: UNVERIFIED, REVIEWED, or VERIFIED
- independent sources used for confirmation

The repository stores research records and derived notes. The yt-dlp executable is installed in the runtime, not committed as a binary.
