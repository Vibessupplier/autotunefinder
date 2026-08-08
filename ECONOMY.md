# Vibes Supplier — Economy

This document tracks infrastructure costs, product economics, and the
assumptions behind pricing decisions. Estimates must be replaced with real
measurements as production usage becomes available.

## Modal Vocal Split

### Current configuration

- GPU: NVIDIA L4
- Maximum containers: 1
- Scale to zero after 60 seconds of inactivity
- Preview duration: 20 seconds
- Separation: acapella and instrumental
- Modal Starter included compute: $30 per month
- Workspace spending limit: $5

### Price reference

- NVIDIA L4: $0.000222 per second as of August 8, 2026
- CPU and memory add a small additional cost
- Modal bills serverless compute by usage

Official references:

- https://modal.com/pricing
- https://modal.com/docs/guide/billing

### Measurements from development

- Real 20-second preview request:
  - Total request duration: 18.6 seconds
  - Execution time: 13.6 seconds
- Estimated GPU processing cost without idle retention:
  - Approximately $0.003 to $0.004 per preview
- Estimated isolated-session cost with the current 60-second idle window:
  - Approximately $0.017 to $0.020 per preview session
- Total Modal usage during the development and deployment session:
  - Approximately $0.104
  - This includes previews, health checks, failed server attempts, tests, image
    builds, and deployments; it is not the cost of one preview.

## Estimated capacity per $1

These figures are preliminary estimates, not production measurements.

| Processing | Sporadic requests | Consecutive requests |
| --- | ---: | ---: |
| 20-second preview | 50–60 previews | 250–330 previews |
| Full 3-minute track | 35–45 tracks | 70–90 tracks |

### Why traffic pattern changes the cost

- Sporadic usage can start a new GPU container for each user and leave it idle
  during the 60-second scale-down window.
- Consecutive requests share an already-running container, reducing the average
  cost per request.
- The scale-down window can be reduced after reliability and cold-start UX have
  been measured in production.

## MP3 versus WAV

- A 320 kbps MP3 and a WAV of the same duration require nearly the same neural
  separation work.
- WAV files are considerably larger, so upload, download, memory, and export
  overhead may be slightly higher.
- The current full-track estimates of 35–45 sporadic tracks per $1 are being
  used provisionally for both formats.
- A real three-minute MP3 benchmark and a real three-minute WAV benchmark are
  required before setting subscription limits.

## Estimated monthly capacity with $30 included compute

Assuming sporadic traffic and the current 60-second idle window:

- Approximately 1,500–1,800 previews of 20 seconds
- Approximately 1,050–1,350 full tracks of about 3 minutes

Consecutive traffic could support substantially more processing within the same
budget.

## Before launching subscriptions

- [ ] Benchmark a real three-minute 320 kbps MP3
- [ ] Benchmark a real three-minute WAV
- [ ] Record total request time and billable GPU, CPU, and memory cost
- [ ] Test a shorter scale-down window
- [ ] Measure cold-start frequency and user waiting time
- [ ] Decide the number of previews allowed for free users
- [ ] Decide monthly full-track limits for each paid plan
- [ ] Include a safety margin for retries, failed jobs, and unusually long tracks
- [ ] Add cost monitoring and alerts before enabling public full-track processing
