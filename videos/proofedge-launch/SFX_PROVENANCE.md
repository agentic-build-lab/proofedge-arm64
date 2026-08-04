# Sound-effect provenance

The launch film uses twelve files from the bundled HyperFrames media-use sound-effect library.
That library records the files as Pixabay sound effects used under the
[Pixabay Content License](https://pixabay.com/service/license-summary/). The sound effects are
mixed under narration at 0.35 gain and embedded in the edited 168.767-second film; they are not
published as standalone audio assets.

The license summary permits free use, attribution-free use, and modification into new works. It
prohibits standalone distribution, so the individual MP3 files remain ignored by Git. The
rendered film and its source cues are public, while the installed media library remains the source
for reproduction.

The local files used for the final render matched the bundled library byte for byte:

| File | SHA-256 |
| --- | --- |
| `chime.mp3` | `74823b1b27703c56e0652db838f503c150ce9c2442d47d27430af3d5121d6d12` |
| `click-soft.mp3` | `075e17bdac5c13662a1c9530050e0046f81d4138e00eb3bf30427a7b4404103d` |
| `click.mp3` | `075e17bdac5c13662a1c9530050e0046f81d4138e00eb3bf30427a7b4404103d` |
| `error.mp3` | `b4882e3941ca496b5038e7c7d64318419da9f69d3da9540a1c693adc639cf121` |
| `impact-bass-1.mp3` | `634d5eda5eb7b501aca98393a64f3815eccf24157cd1d95df55aaec1b5000bd7` |
| `impact-bass-2.mp3` | `fb832995477784f44ba8533359d20caf706195b52117ecc2a33b3e63e3c1307b` |
| `key-press.mp3` | `bcc892df0898bf466162f14233c3e92a8c1ea351f6affd8a3a7e56c9a760bb72` |
| `riser.mp3` | `d2f29d49f27dee7d3b25af22ffe5bebc39390cc5d5fb3b3e1c433499c77f3d1d` |
| `typing.mp3` | `944160652faeb7b32acc9341ede4d735a5c9a4ce3fe8509ef7eab91efb430487` |
| `whoosh-cinematic.mp3` | `0a0f3505856fdfa84ac6b86b3c55ccd0ef1eb4ff0907d7b6934002218a73404e` |
| `whoosh-short.mp3` | `c2efd9d902a59bf9ec5019035d7deadd17762136896b6e3cb6dd99ea50997a30` |
| `whoosh.mp3` | `c2efd9d902a59bf9ec5019035d7deadd17762136896b6e3cb6dd99ea50997a30` |

Cue placement and duration are frozen in `audio_meta.json`; `audio_request.json` records the
semantic cue names. The final MP4 SHA-256 is
`581b9bc2286933a76aa52d9d5360d1f9e3f4596e7856e673e813e21e7239c269`.
