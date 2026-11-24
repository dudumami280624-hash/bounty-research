# Wallstreet Explainer integration
Upstream: https://github.com/HeyChengC/wallstreet-explainer (MIT code/docs; third-party media excluded).
Persistent project decision: use as an optional downstream English educational video renderer, never as OCR or fact verification. No automatic publication. Use original charts and verified claims only. Keep upstream checkout outside the research repository.
## Bootstrap
Run `bash knowledge/trading-education/integration/bootstrap-wallstreet.sh /tmp/wallstreet-explainer` in a Linux environment with git, Node, Python and ffmpeg. The script records the actual upstream revision and runs the upstream demo structural check. Demo assets are not publication assets. A structural check is not a rendered-video acceptance test.
## Continuity
Resume by running bootstrap, recording actual exit status and upstream revision, then rendering a short original English lesson fixture and inspecting frames and ffprobe output. Keep this independent of OCR. Do not claim deployment or render success until observed.
