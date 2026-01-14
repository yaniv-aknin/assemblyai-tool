# Batch Command

Process multiple audio files from an input directory to an output directory with configurable concurrency, rate limiting, and automatic file skipping. Ideal for bulk transcription workflows.

## Command Signature

```bash { .api }
aait batch <input_dir> <output_dir> [OPTIONS]

Arguments:
  input_dir     Input directory containing audio files (required, must exist)
  output_dir    Output directory for transcripts (required, created if doesn't exist)
```

## Capabilities

### Concurrency Control

Configure parallel upload and processing to optimize throughput.

```bash { .api }
--upload-concurrency <count>
  Number of concurrent file uploads
  Default: 1

--processing-concurrency <count>
  Number of concurrent transcription jobs
  Default: 8
```

**Examples**:
```bash
# Conservative: 1 upload, 8 processing
aait batch ./audio ./output

# Moderate: 3 uploads, 10 processing
aait batch ./audio ./output \
  --upload-concurrency 3 \
  --processing-concurrency 10

# Aggressive: 5 uploads, 15 processing
aait batch ./audio ./output \
  --upload-concurrency 5 \
  --processing-concurrency 15
```

**Notes**:
- Upload concurrency controls how many files are uploaded to AssemblyAI simultaneously
- Processing concurrency controls how many transcriptions are processed in parallel
- Total thread count = upload_concurrency + processing_concurrency
- Higher concurrency = faster completion but more resource usage

### File Overwrite Control

Control whether to skip or overwrite existing output files.

```bash { .api }
--force / -f
  Overwrite existing output files
  Default: False (skip existing files)
```

**Examples**:
```bash
# Skip existing files (default)
aait batch ./audio ./output

# Overwrite all files
aait batch ./audio ./output --force

# Short form
aait batch ./audio ./output -f
```

**Behavior**:
- Without `--force`: Existing output files are skipped with a summary message
- With `--force`: All files are reprocessed and outputs overwritten
- Skipped file count is displayed when progress is enabled

### Rate Limiting

Control upload speed with fixed or ratio-based rate limiting to manage bandwidth usage.

```bash { .api }
--rate-limit-kbps <kbps>
  Fixed rate limit in kbps (0 = no limit)
  Default: 0.0 (no limit)

--rate-limit-ratio <ratio>
  Rate limit as ratio of first upload speed (0.0-1.0)
  1.0 = no limit (full speed)
  Default: 1.0 (no limit)
```

**Fixed Rate Limiting**:
```bash
# Limit all uploads to 500 kbps
aait batch ./audio ./output --rate-limit-kbps 500

# Limit to 1 Mbps (1024 kbps)
aait batch ./audio ./output --rate-limit-kbps 1024

# Limit to 2 Mbps
aait batch ./audio ./output --rate-limit-kbps 2048
```

**Ratio-Based Rate Limiting**:
```bash
# Limit subsequent uploads to 50% of first upload speed
aait batch ./audio ./output --rate-limit-ratio 0.5

# Limit to 75% of first upload speed
aait batch ./audio ./output --rate-limit-ratio 0.75

# Limit to 25% of first upload speed
aait batch ./audio ./output --rate-limit-ratio 0.25
```

**Combined Usage**:
```bash
# Use ratio limiting with fallback to fixed rate
aait batch ./audio ./output \
  --rate-limit-kbps 500 \
  --rate-limit-ratio 0.5
```

**Notes**:
- Ratio-based limiting measures the first upload speed and applies the ratio to subsequent uploads
- If ratio is 1.0 (default), no ratio limiting is applied
- Rate limiter is shared across all concurrent uploads
- First upload is never rate-limited (used as baseline for ratio)

### Transcription Options

All transcription options from the `convert` command are supported:

```bash { .api }
# Output format
--format <format>
  Values: utterances, paragraphs, text, srt, vtt, json
  Default: utterances

# Speech model
--speech-model <model>
  Values: best, nano, slam-1, universal
  Default: best

# Language
--language-code <code>
  Language code (e.g., en, es, fr)
--language-detection
  Enable automatic language detection

# Audio slicing
--audio-start-from <ms>
--audio-end-at <ms>

# Text formatting
--punctuate / --no-punctuate
  Default: --punctuate

# Custom vocabulary
--word-boost <words>
--boost-param <param>
--custom-spelling <mappings>

# Speaker diarization
--speaker-labels / --no-speaker-labels
--speakers-expected <count>

# Content analysis
--sentiment-analysis / --no-sentiment-analysis
--entity-detection / --no-entity-detection
--auto-chapters / --no-auto-chapters
--auto-highlights / --no-auto-highlights

# UI options
--show-progress / --no-show-progress
  Default: --show-progress
```

## File Processing

### Supported File Extensions

The batch command automatically filters for supported audio/video files:
- Audio: `.mp3`, `.m4a`, `.wav`, `.flac`, `.aac`, `.ogg`, `.opus`, `.wma`
- Video: `.mp4`, `.webm`

All other files in the input directory are ignored.

### Output File Naming

Output files are created in the output directory with the same stem as input files but with extension determined by format:

| Format | Extension |
|--------|-----------|
| text, paragraphs, utterances | .txt |
| srt | .srt |
| vtt | .vtt |
| json | .json |

**Example**:
```
Input:  ./audio/meeting.mp3
Output: ./output/meeting.txt  (format: utterances)

Input:  ./audio/video.mp4
Output: ./output/video.srt    (format: srt)

Input:  ./audio/podcast.wav
Output: ./output/podcast.json (format: json)
```

## Progress Tracking

When `--show-progress` is enabled (default), a comprehensive progress display is shown:

```
{uploading_count} u/l; {processing_count} asr | ██████████ | 45/100 files
```

Components:
- `u/l`: Number of files currently uploading
- `asr`: Number of files currently processing (automatic speech recognition)
- Progress bar: Overall completion
- File count: Completed / Total files

### Progress Output
- Skipped files are reported at the start
- Errors are logged as they occur (file name + error message)
- Final summary shows completed and failed counts

## Complete Examples

### Basic Batch Processing
```bash
# Process all audio files with defaults
aait batch ./audio_files ./transcripts
```

### High-Throughput Batch
```bash
# Maximum concurrency for fast processing
aait batch ./audio ./output \
  --upload-concurrency 5 \
  --processing-concurrency 15
```

### Batch with Speaker Diarization
```bash
# All files with speaker labels
aait batch ./interviews ./transcripts \
  --speaker-labels \
  --speakers-expected 2 \
  --format utterances
```

### Batch Subtitle Generation
```bash
# Generate SRT subtitles for all videos
aait batch ./videos ./subtitles \
  --format srt \
  --upload-concurrency 3
```

### Controlled Bandwidth Usage
```bash
# Limit bandwidth to 50% of measured speed
aait batch ./audio ./output \
  --upload-concurrency 2 \
  --rate-limit-ratio 0.5
```

### Technical Content Batch
```bash
# Batch with vocabulary boosting
aait batch ./tech-talks ./transcripts \
  --upload-concurrency 2 \
  --processing-concurrency 10 \
  --word-boost "Kubernetes,Docker,API,GraphQL" \
  --boost-param high
```

### Complete Analysis Batch
```bash
# Full AI analysis for all files
aait batch ./podcasts ./analyzed \
  --upload-concurrency 3 \
  --processing-concurrency 12 \
  --speaker-labels \
  --sentiment-analysis \
  --entity-detection \
  --auto-chapters \
  --auto-highlights
```

### Reprocess with Force
```bash
# Reprocess all files even if outputs exist
aait batch ./audio ./output \
  --force \
  --format text
```

### Rate-Limited Batch
```bash
# Fixed 500 kbps rate limit
aait batch ./large-files ./output \
  --upload-concurrency 1 \
  --rate-limit-kbps 500
```

### Silent Batch Processing
```bash
# No progress output
aait batch ./audio ./output \
  --no-show-progress \
  --upload-concurrency 2
```

## Output Behavior

### Success
- Creates output directory if it doesn't exist
- Processes all audio files found in input directory
- Displays progress (if enabled)
- Reports final counts: completed and failed
- Exit code: 0

### Errors
- Individual file errors are logged but don't stop batch processing
- Files that fail are counted in the failed count
- Progress display continues showing other files processing
- Exit code: 0 (batch completes even with some failures)

### No Files
If no audio files are found in the input directory:
- Prints: "No audio files found in input directory"
- Exit code: 0

If all files are skipped (already exist without --force):
- Prints: "No files to process"
- Exit code: 0

## Performance Considerations

### Optimal Concurrency Settings

**Small files (< 5 MB)**:
- Upload concurrency: 3-5
- Processing concurrency: 10-15

**Medium files (5-50 MB)**:
- Upload concurrency: 2-3
- Processing concurrency: 8-12

**Large files (> 50 MB)**:
- Upload concurrency: 1-2
- Processing concurrency: 6-10

### Rate Limiting Strategy

**Fast network, limited API quota**:
```bash
--rate-limit-ratio 0.5  # Use 50% of available bandwidth
```

**Shared network**:
```bash
--rate-limit-kbps 1000  # Fixed 1 Mbps limit
```

**Background processing**:
```bash
--rate-limit-ratio 0.25  # Use only 25% to minimize impact
```

### Thread Safety

- Progress tracking is thread-safe using locks
- Upload and processing use separate semaphores
- Rate limiter is shared and thread-safe
- First upload detection is protected by locks
