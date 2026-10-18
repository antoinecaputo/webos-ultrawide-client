# Ultrawide implementation and device checks

This fork is based on [jellyfin-webos](https://github.com/jellyfin/jellyfin-webos) commit `ab47940`. Its app ID, `com.antoine.ultrawideclient`, allows installation alongside the official client. It loads the web client hosted by the user's Jellyfin server.

## Changes

- `resolution` is `3440x1440`, which filled the tested ultrawide panel.
- The hosted Jellyfin iframe occupies the full app viewport.
- Jellyfin's **Auto / Zoom / Stretch** menu remains active. Auto uses `contain`; Zoom uses `cover`; Stretch uses `fill`. The fork gives the menu priority over a server CSS rule that forced `cover`. No video transform is applied at 100% zoom.
- During video playback: **red** cycles between the menu choice, forced cover, and forced contain; **green** zooms out by 5%; **yellow** zooms in by 5%; **blue** resets zoom to 100%. Normal arrow-key navigation remains available.

The upstream webOS adapter still builds the device profile. This fork does not force codec, HDR, or Dolby Vision capability flags.

## Observed on a 3440×1440 webOS display

- webOS opened the app at **3440×1440**, and the hosted web client occupied the same viewport.
- A 16:9 episode displayed its full image with side bars in Auto mode. The menu produced `contain` for Auto, `cover` for Zoom, and `fill` for Stretch.
- A **3840×2160 HEVC 10-bit** MKV with Dolby Vision profile 8 and HDR10 fallback played directly; the screen's picture information indicated **HDR**. The webOS device API reported `hdr10: true` and `dolbyVision: false`. This confirms HDR10 fallback playback, not Dolby Vision output.
- A separate 21:9 test app showed that an app border and an H.264 SDR video could reach both side edges of the panel.
