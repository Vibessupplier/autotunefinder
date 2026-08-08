# 🚀 Audio Tool Roadmap

## Version 0.1
- [x] Upload audio
- [x] Audio player
- [x] Key detection
- [x] BPM detection
- [x] Camelot conversion
- [x] Alternative key detection
- [x] Multipage navigation
- [x] Initial dark UI
- [x] Neon logo

---

## Version 0.2
- [x] Reusable FFmpeg audio engine
- [x] Speed Changer page
- [x] Exact target BPM control
- [x] Nightcore-style speed up (covered by Speed Changer)
- [x] Slowed-style speed down (covered by Speed Changer)
- [x] Pitch follows speed mode
- [x] Preserve original pitch mode
- [x] Independent Pitch Shifter (-12 to +12 semitones)
- [x] Independent Tempo Changer
- [x] MP3 export and download
- [x] 20-second processed preview
- [x] Invalidate preview when speed or pitch changes
- [x] Improve Speed Changer controls and player UI

---

## Version 0.3
- [x] Local Vocal Split prototype
- [x] Acapella and instrumental players and downloads
- [x] Validate Demucs separation quality with a full track
- [x] Select the start point for a free 20-second Vocal Split preview
- [x] Process only the selected preview segment
- [ ] Compare clean and natural acapella separation modes
- [x] Run Vocal Split processing on Modal GPU
- [ ] Re-enable the public preview after access and cost controls are ready
- [ ] Add background processing and temporary result delivery

---

## Version 0.4
- [x] Privacy-conscious PostHog page and product-event analytics
- [ ] Producer accounts
- [ ] Monthly subscription with processing credits
- [ ] Free Vocal Split previews
- [ ] Premium full-track Vocal Split
- [ ] Stripe subscription checkout and billing management
- [ ] Usage limits and cost monitoring
- [ ] Free users: MP3 export only
- [ ] Premium users: WAV, FLAC, and additional high-quality export formats
- [ ] Apply the free and Premium format policy consistently across audio tools

---

## Future Vocal Tools
- [ ] Vocal Mode
- [ ] Vocal Range Detector
- [ ] Pitch Correction Preset Generator

---

## Future Analyze Tools
- [x] Mastering Analyzer page
- [x] Integrated LUFS measurement
- [ ] Short-term and momentary LUFS measurements
- [x] Peak and true-peak level measurements in dBFS/dBTP
- [x] Loudness range and RMS level indicators
- [ ] Additional dynamic-range indicators
- [x] Static stereo balance, width, phase correlation, and mono compatibility
- [x] Clear mastering-oriented result summaries and measurement explanations
- [x] A/B mastering comparison against a user-selected reference track
- [x] Optional non-destructive Volume Match for reference listening
- [ ] Configurable mastering reference ranges
- [x] Static spectral balance visualization and A/B comparison
- [ ] Custom synchronized audio player for the Mastering Analyzer
- [ ] Interactive waveform and spectrogram with clickable playhead
- [ ] Live peak, RMS, momentary LUFS, and short-term LUFS meters
- [ ] Live frequency spectrum, stereo balance, and phase correlation meters
- [ ] Highlight clipping and notable loudness sections on the timeline

---

## Future Ideas
- [x] Audio Chopper Beta page
- [x] Static waveform with zoom, pan, and precise start/end controls
- [x] Automatic selected-fragment player and optional preview
- [x] Export user-selected samples in MP3
- [ ] JavaScript/Web Audio waveform component with direct drag selection
- [ ] Mouse-wheel waveform zoom, drag-to-pan, and synchronized playhead
- [ ] Premium WAV and FLAC sample export
- [ ] Multi-stem separation (vocals, drums, bass, and other)
- [ ] Spectrogram
- [ ] AI Mix Assistant
- [ ] AI Mastering
