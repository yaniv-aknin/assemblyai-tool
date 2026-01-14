# Convert Command

Convert a single audio or video file to text with comprehensive transcription options including speaker diarization, sentiment analysis, entity detection, and multiple output formats.

## Command Signature

```bash { .api }
aait convert <inpath> <outpath> [OPTIONS]

Arguments:
  inpath    Path to input audio/video file (required, must exist)
  outpath   Path to output file (required)
```

## Capabilities

### Output Format Options

Control the format of the transcription output.

```bash { .api }
--format <format>

Values:
  utterances    Text with speaker labels (default)
  paragraphs    Text split into paragraphs
  text          Plain text
  srt           SRT subtitle format
  vtt           WebVTT subtitle format
  json          Full JSON response from API

Default: utterances
```

**Examples**:
```bash
# Plain text output
aait convert audio.mp3 output.txt --format text

# SRT subtitles
aait convert video.mp4 subtitles.srt --format srt

# Full JSON response
aait convert audio.mp3 data.json --format json
```

### Speech Model Selection

Choose which speech recognition model to use for transcription.

```bash { .api }
--speech-model <model>

Values:
  best        Best available model (highest accuracy)
  nano        Fast, lightweight model
  slam-1      SLAM-1 model
  universal   Universal model for all languages

Default: best
```

**Examples**:
```bash
# Use best model (default)
aait convert audio.mp3 output.txt --speech-model best

# Use nano model for faster processing
aait convert audio.mp3 output.txt --speech-model nano
```

### Language Configuration

Configure language detection or specify a language explicitly.

```bash { .api }
--language-code <code>
  Language code (e.g., en, es, fr, de, it, pt, nl)
  Overrides --language-detection when specified
  Optional

--language-detection
  Enable automatic language detection
  Default: False (disabled)
```

**Examples**:
```bash
# Explicit language specification
aait convert audio.mp3 output.txt --language-code en
aait convert audio.mp3 output.txt --language-code es

# Automatic language detection
aait convert audio.mp3 output.txt --language-detection
```

### Audio Slicing

Transcribe only a specific portion of the audio file by specifying start and end times in milliseconds.

```bash { .api }
--audio-start-from <milliseconds>
  Start transcription from this millisecond
  Optional (transcribes from beginning if not specified)

--audio-end-at <milliseconds>
  End transcription at this millisecond
  Optional (transcribes to end if not specified)
```

**Examples**:
```bash
# Transcribe from 1 minute to 3 minutes
aait convert audio.mp3 output.txt \
  --audio-start-from 60000 \
  --audio-end-at 180000

# Transcribe only the first 30 seconds
aait convert audio.mp3 output.txt --audio-end-at 30000

# Transcribe from 2 minutes onward
aait convert audio.mp3 output.txt --audio-start-from 120000
```

### Text Formatting

Control automatic punctuation and formatting of the transcription.

```bash { .api }
--punctuate / --no-punctuate
  Enable or disable automatic punctuation
  Default: --punctuate (enabled)
```

**Examples**:
```bash
# With punctuation (default)
aait convert audio.mp3 output.txt --punctuate

# Without punctuation
aait convert audio.mp3 output.txt --no-punctuate
```

### Custom Vocabulary Boosting

Improve accuracy for specific words or phrases by boosting their recognition weight.

```bash { .api }
--word-boost <words>
  Comma-separated list of words/phrases to boost accuracy
  Optional

--boost-param <param>
  Weight to apply to boosted words
  Values: low, default, high
  Default: default
```

**Examples**:
```bash
# Boost technical terms with default weight
aait convert meeting.mp3 output.txt \
  --word-boost "Kubernetes,Docker,API,GraphQL"

# Boost company/product names with high weight
aait convert earnings.mp3 output.txt \
  --word-boost "TechCorp,CloudPlatform,DataSync" \
  --boost-param high

# Boost with low weight
aait convert audio.mp3 output.txt \
  --word-boost "specialized,terminology" \
  --boost-param low
```

### Custom Spelling

Define custom spellings for specific words in the transcription output.

```bash { .api }
--custom-spelling <mappings>
  Custom spelling mappings in format: 'from1:to1,from2:to2'
  Optional
```

**Examples**:
```bash
# Format acronyms with periods
aait convert audio.mp3 output.txt \
  --custom-spelling "AI:A.I.,CEO:C.E.O.,API:A.P.I."

# Brand-specific spellings
aait convert audio.mp3 output.txt \
  --custom-spelling "iphone:iPhone,macbook:MacBook"
```

### Speaker Diarization

Identify and label different speakers in the audio.

```bash { .api }
--speaker-labels / --no-speaker-labels
  Enable or disable speaker diarization
  Default: --no-speaker-labels (disabled)

--speakers-expected <count>
  Expected number of speakers (2-10)
  Optional (auto-detect if not specified)
```

**Examples**:
```bash
# Enable speaker labels with auto-detection
aait convert interview.mp3 output.txt --speaker-labels

# Specify expected number of speakers
aait convert panel.mp3 output.txt \
  --speaker-labels \
  --speakers-expected 4

# 2-person interview
aait convert conversation.mp3 output.txt \
  --speaker-labels \
  --speakers-expected 2
```

### Content Analysis Features

Enable advanced AI-powered analysis features for the transcription.

```bash { .api }
--sentiment-analysis / --no-sentiment-analysis
  Enable sentiment analysis of the speech
  Default: --no-sentiment-analysis (disabled)

--entity-detection / --no-entity-detection
  Enable named entity detection
  Default: --no-entity-detection (disabled)

--auto-chapters / --no-auto-chapters
  Enable automatic chapter generation
  Default: --no-auto-chapters (disabled)

--auto-highlights / --no-auto-highlights
  Enable automatic highlight identification
  Default: --no-auto-highlights (disabled)
```

**Examples**:
```bash
# Full content analysis
aait convert podcast.mp3 analysis.txt \
  --sentiment-analysis \
  --entity-detection \
  --auto-chapters \
  --auto-highlights

# Just sentiment and entities
aait convert interview.mp3 output.txt \
  --sentiment-analysis \
  --entity-detection

# Just chapters for long-form content
aait convert audiobook.mp3 output.txt --auto-chapters
```

### UI and Performance Options

Control progress display and upload rate limiting.

```bash { .api }
--show-progress / --no-show-progress
  Show or hide progress messages and indicators
  Default: --show-progress (enabled)

--rate-limit-kbps <kbps>
  Rate limit for upload in kbps (0 = no limit)
  Default: 0.0 (no limit)
```

**Examples**:
```bash
# Hide progress output
aait convert audio.mp3 output.txt --no-show-progress

# Limit upload to 500 kbps
aait convert large-file.wav output.txt --rate-limit-kbps 500

# Limit upload to 1 Mbps (1024 kbps)
aait convert video.mp4 output.txt --rate-limit-kbps 1024
```

## Complete Examples

### Basic Transcription
```bash
# Simplest usage
aait convert meeting.mp3 transcript.txt
```

### Interview with Speakers
```bash
aait convert interview.mp3 transcript.txt \
  --speaker-labels \
  --speakers-expected 2 \
  --format utterances
```

### Technical Content with Custom Vocabulary
```bash
aait convert tech-talk.mp3 transcript.txt \
  --word-boost "Kubernetes,Docker,API,GraphQL,React,TypeScript" \
  --boost-param high \
  --custom-spelling "API:A.P.I.,CEO:C.E.O."
```

### Podcast with Full Analysis
```bash
aait convert podcast.mp3 full-analysis.txt \
  --speaker-labels \
  --sentiment-analysis \
  --entity-detection \
  --auto-chapters \
  --auto-highlights
```

### Subtitle Generation for Video
```bash
aait convert video.mp4 subtitles.srt \
  --format srt \
  --language-code en
```

### Partial Transcription with Rate Limiting
```bash
aait convert long-audio.wav excerpt.txt \
  --audio-start-from 600000 \
  --audio-end-at 900000 \
  --rate-limit-kbps 500
```

### Multilingual Audio
```bash
aait convert multilingual.mp3 transcript.txt \
  --language-detection \
  --speaker-labels
```

## Output Behavior

### Success
- Creates output file at specified path
- Prints completion message with audio duration (if progress enabled)
- Exit code: 0

### Error
- Prints error message to stderr
- Exit code: 1

### Progress Output
When `--show-progress` is enabled (default):
1. Upload progress bar with file size and speed
2. Processing progress bar showing completion percentage
3. Completion message: `✓ Transcription complete (X.X minutes)`
4. File save message: `Saving to <outpath>`
