# Basic Usage

Quick start guide with practical examples for common transcription workflows. This guide covers single file transcription, batch processing, and transcript management operations.

## Prerequisites

Before using assemblyai-tool, ensure you have an API key configured. The tool searches for the key in this order:

1. Environment variable: `ASSEMBLY_AI_KEY`
2. `.env` file in current directory
3. `~/.assemblyai-tool.env` file in home directory

**Setup Example**:
```bash
# Option 1: Environment variable
export ASSEMBLY_AI_KEY=your_api_key_here

# Option 2: Create .env file
echo "ASSEMBLY_AI_KEY=your_api_key_here" > .env

# Option 3: Home directory config
echo "ASSEMBLY_AI_KEY=your_api_key_here" > ~/.assemblyai-tool.env
```

## Single File Transcription

Convert individual audio or video files to text using the `convert` command.

### Basic Transcription

```bash
# Simplest usage - default settings
aait convert input.mp3 output.txt

# The default settings are:
# - Format: utterances (text with speaker labels)
# - Model: best (highest accuracy)
# - Punctuation: enabled
# - Progress: shown
```

**Output**: Plain text file with transcribed speech

### With Speaker Labels

Identify and label different speakers in the audio.

```bash
# Enable speaker diarization
aait convert interview.mp3 transcript.txt --speaker-labels

# Specify expected number of speakers for better accuracy
aait convert panel.mp3 transcript.txt \
  --speaker-labels \
  --speakers-expected 4
```

**Output Format** (utterances):
```
Speaker A: Hello, welcome to the show.
Speaker B: Thanks for having me.
Speaker A: Let's get started.
```

### Different Output Formats

Choose the format that best suits your needs.

```bash
# Plain text (no speaker labels)
aait convert audio.mp3 output.txt --format text

# Paragraphs (grouped text)
aait convert audio.mp3 output.txt --format paragraphs

# SRT subtitles for video
aait convert video.mp4 subtitles.srt --format srt

# VTT subtitles (WebVTT)
aait convert video.mp4 subtitles.vtt --format vtt

# Full JSON response (all metadata)
aait convert audio.mp3 data.json --format json
```

### Advanced Transcription Options

Combine multiple features for sophisticated transcription.

```bash
# Full content analysis
aait convert podcast.mp3 analysis.txt \
  --speaker-labels \
  --sentiment-analysis \
  --entity-detection \
  --auto-chapters \
  --auto-highlights

# Technical content with vocabulary boosting
aait convert tech-talk.mp3 transcript.txt \
  --word-boost "Kubernetes,Docker,API,GraphQL,React" \
  --boost-param high \
  --custom-spelling "API:A.P.I.,CEO:C.E.O."

# Partial transcription (specific time range)
aait convert long-audio.wav excerpt.txt \
  --audio-start-from 60000 \
  --audio-end-at 180000
```

**Time ranges** are in milliseconds:
- 60000 ms = 1 minute
- 180000 ms = 3 minutes

## Batch Processing

Process multiple audio files efficiently with concurrent uploads and transcriptions.

### Basic Batch Conversion

```bash
# Process all audio files in a directory
aait batch ./audio_files ./transcripts

# This will:
# - Find all supported audio/video files in ./audio_files
# - Create ./transcripts directory if it doesn't exist
# - Transcribe each file with default settings
# - Save outputs with same name but .txt extension
```

**Supported Formats**: .mp3, .mp4, .m4a, .wav, .flac, .aac, .ogg, .opus, .webm, .wma

### Batch with Custom Settings

Apply the same transcription options to all files.

```bash
# Generate SRT subtitles for all videos
aait batch ./videos ./subtitles \
  --format srt \
  --upload-concurrency 3

# Interview transcription with speaker labels
aait batch ./interviews ./transcripts \
  --speaker-labels \
  --speakers-expected 2 \
  --format utterances

# Technical content batch
aait batch ./tech-talks ./transcripts \
  --word-boost "Kubernetes,Docker,API" \
  --boost-param high \
  --upload-concurrency 2
```

### Concurrency Control

Optimize throughput by adjusting concurrent operations.

```bash
# Conservative (default): 1 upload, 8 processing
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

**Guidelines**:
- **Upload concurrency**: Controls simultaneous file uploads (affects bandwidth)
- **Processing concurrency**: Controls parallel transcriptions (affects API usage)
- Higher = faster, but more resource-intensive

### Rate Limiting

Control bandwidth usage during batch uploads.

```bash
# Fixed rate limit (500 kbps)
aait batch ./audio ./output --rate-limit-kbps 500

# Ratio-based (use 50% of measured speed)
aait batch ./audio ./output --rate-limit-ratio 0.5

# Combined (ratio with fixed fallback)
aait batch ./audio ./output \
  --rate-limit-kbps 500 \
  --rate-limit-ratio 0.5
```

**When to use**:
- Fixed rate: Shared networks, known bandwidth limits
- Ratio-based: Adaptive limiting, background processing

### File Management

Control which files are processed.

```bash
# Skip existing files (default)
aait batch ./audio ./output

# Overwrite all files
aait batch ./audio ./output --force

# Short form
aait batch ./audio ./output -f
```

**Behavior**:
- Without `--force`: Skips files that already have output
- With `--force`: Reprocesses and overwrites all files

### Progress Tracking

Monitor batch processing in real-time.

```bash
# With progress (default)
aait batch ./audio ./output

# Silent mode
aait batch ./audio ./output --no-show-progress
```

**Progress Display**:
```
3 u/l; 8 asr | ████████░░ | 45/100 files
```

- `u/l`: Files currently uploading
- `asr`: Files being transcribed
- Progress bar with completion count

## Transcript Management

Manage previously created transcripts on AssemblyAI servers.

### List All Transcripts

View all transcripts in your account.

```bash
aait list
```

**Output**:
```
abc123def456 completed
ghi789jkl012 completed
mno345pqr678 error
```

Each line shows: `transcript_id status`

### Load Transcript

Open an interactive Python shell with a transcript object loaded.

```bash
# Load by ID
aait load abc123def456

# Load by negative index (from list output)
aait load -1  # Most recent
aait load -2  # Second most recent
```

**Interactive Shell**:
```python
>>> transcript.text
'Hello, welcome to the show...'

>>> transcript.audio_duration
125430  # milliseconds

>>> transcript.utterances
[...]
```

**Exit**: Type `exit()` or press Ctrl-D

### Delete Transcript

Remove a transcript from AssemblyAI servers.

```bash
# Delete with confirmation prompt
aait delete abc123def456

# Skip confirmation
aait delete abc123def456 --force
aait delete abc123def456 -f

# Delete by index
aait delete -1 --force
```

**Confirmation Prompt**:
```
Delete transcript abc123def456? [y/N]:
```

## Common Workflows

### Workflow 1: Interview Transcription

Complete workflow for interview transcription with speakers.

```bash
# Step 1: Transcribe with speaker labels
aait convert interview.mp3 transcript.txt \
  --speaker-labels \
  --speakers-expected 2 \
  --format utterances

# Step 2: Review output
cat transcript.txt

# Step 3: If needed, regenerate with adjustments
aait convert interview.mp3 transcript-v2.txt \
  --speaker-labels \
  --speakers-expected 3 \
  --word-boost "specific,terms,to,boost"
```

### Workflow 2: Video Subtitle Generation

Generate subtitles for video content.

```bash
# Step 1: Generate SRT subtitles
aait convert video.mp4 subtitles.srt \
  --format srt \
  --language-code en

# Step 2: For international content
aait convert multilingual.mp4 subtitles.vtt \
  --format vtt \
  --language-detection

# Step 3: Batch process multiple videos
aait batch ./videos ./subtitles \
  --format srt \
  --upload-concurrency 3
```

### Workflow 3: Podcast Analysis

Comprehensive analysis of podcast episodes.

```bash
# Full analysis batch
aait batch ./episodes ./analyzed \
  --upload-concurrency 2 \
  --processing-concurrency 10 \
  --speaker-labels \
  --sentiment-analysis \
  --entity-detection \
  --auto-chapters \
  --auto-highlights \
  --format json

# Extract specific episode as text
aait convert ./episodes/ep001.mp3 ep001.txt \
  --format paragraphs
```

### Workflow 4: Lecture Transcription

Educational content with chapters and technical terms.

```bash
# Single lecture
aait convert lecture-01.mp3 lecture-01.txt \
  --auto-chapters \
  --word-boost "algorithm,database,neural network" \
  --boost-param high \
  --format paragraphs

# Batch lectures
aait batch ./lectures ./transcripts \
  --auto-chapters \
  --word-boost "algorithm,database,neural network" \
  --boost-param high \
  --upload-concurrency 2
```

### Workflow 5: Meeting Notes

Quick meeting transcription with time slicing.

```bash
# Transcribe specific agenda item (10-20 minutes)
aait convert meeting.mp3 agenda-item-2.txt \
  --audio-start-from 600000 \
  --audio-end-at 1200000 \
  --speaker-labels \
  --format utterances

# Full meeting with chapters
aait convert meeting.mp3 full-meeting.txt \
  --speaker-labels \
  --auto-chapters \
  --format paragraphs
```

## Troubleshooting

### API Key Not Found

**Error**: `No API key found`

**Solution**:
```bash
# Set environment variable
export ASSEMBLY_AI_KEY=your_key_here

# Or create .env file
echo "ASSEMBLY_AI_KEY=your_key_here" > .env
```

### File Not Supported

**Error**: No files found or file skipped

**Solution**: Ensure file has supported extension:
- Audio: .mp3, .m4a, .wav, .flac, .aac, .ogg, .opus, .wma
- Video: .mp4, .webm

### Slow Upload

**Issue**: Upload taking too long

**Solution**: Check network speed or use rate limiting:
```bash
# Don't rate limit (max speed)
aait convert audio.mp3 output.txt --rate-limit-kbps 0

# For batch, increase upload concurrency
aait batch ./audio ./output --upload-concurrency 3
```

### Transcription Errors

**Issue**: Individual files failing in batch

**Solution**: Check batch output for error messages. Failed files are logged:
```
Error processing audio.mp3: [error details]
```

Review failed files and retry individually with adjusted settings.

## Version Information

Check the installed version:

```bash
aait --version
```

Output: `aait 0.3.2` (or current version)

## Next Steps

- **Detailed Options**: See [Convert Command](./commands/convert.md) for all transcription options
- **Batch Features**: See [Batch Command](./commands/batch.md) for advanced batch processing
- **Python API**: See [Python API Reference](./python-api.md) for programmatic usage
- **Architecture**: See [Architecture](./architecture.md) for design details
