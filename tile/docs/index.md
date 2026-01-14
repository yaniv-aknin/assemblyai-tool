# assemblyai-tool

A command-line interface tool for audio and video transcription using the AssemblyAI API. This package provides a comprehensive Python CLI wrapper around the AssemblyAI SDK, offering commands for single file conversion, batch processing, transcript management, and extensive transcription customization options.

## Package Information

- **Package Name**: assemblyai-tool
- **Language**: Python
- **Python Version**: >= 3.12
- **Installation**: `pip install assemblyai-tool`
- **CLI Command**: `aait`

## Core Imports

```python
from assemblyai_tool import (
    app,
    OutputFormat,
    SpeechModelChoice,
    BoostParam,
    TranscribeOptions,
    AUDIO_EXTENSIONS,
    load_api_key,
    parse_custom_spelling,
    upload_file_with_progress,
    make_transcript,
    format_output,
    process_single_file
)
```

## Configuration

The tool requires an AssemblyAI API key from one of these sources (in order of precedence):

1. Environment variable: `ASSEMBLY_AI_KEY`
2. `.env` file in current directory with `ASSEMBLY_AI_KEY=<key>`
3. `~/.assemblyai-tool.env` file with `ASSEMBLY_AI_KEY=<key>`

Example `.env` file:
```
ASSEMBLY_AI_KEY=your_api_key_here
```

## Architecture

The tool uses a Typer-based CLI with sophisticated concurrency control, rate limiting, and progress tracking. Key architectural components include a two-phase concurrency model (separate upload and processing pools), adaptive rate limiting (fixed or ratio-based), thread-safe progress tracking, and flexible output formatting.

[Architecture Details](./architecture.md)

## Basic Usage

Quick start guide with practical examples for single file transcription, batch processing, and transcript management. Includes common workflows, troubleshooting tips, and best practices for different use cases like interviews, podcasts, video subtitles, and lectures.

[Basic Usage Guide](./basic-usage.md)

## CLI Commands

### convert - Single File Transcription

Convert a single audio/video file to text with extensive transcription options including speaker diarization, sentiment analysis, entity detection, and multiple output formats.

```bash { .api }
aait convert <inpath> <outpath> [OPTIONS]

Arguments:
  inpath    Path to input audio/video file (required)
  outpath   Path to output file (required)

Options:
  --format                  Output format (default: utterances)
  --speech-model           Speech model to use (default: best)
  --language-code          Language code (e.g., en, es, fr)
  --language-detection     Enable automatic language detection
  --audio-start-from       Start transcription from millisecond
  --audio-end-at          End transcription at millisecond
  --punctuate             Enable automatic punctuation (default: True)
  --word-boost            Comma-separated words to boost accuracy
  --boost-param           Weight for boosted words (default: default)
  --custom-spelling       Custom spelling mappings
  --speaker-labels        Enable speaker diarization
  --speakers-expected     Expected number of speakers (2-10)
  --sentiment-analysis    Enable sentiment analysis
  --entity-detection      Enable entity detection
  --auto-chapters         Enable auto chapters
  --auto-highlights       Enable auto highlights
  --show-progress         Show progress messages (default: True)
  --rate-limit-kbps       Rate limit in kbps (default: 0.0)
```

[Convert Command Details](./commands/convert.md)

### batch - Batch File Processing

Process multiple audio files from an input directory with configurable concurrency, rate limiting, and automatic file skipping for efficient bulk transcription.

```bash { .api }
aait batch <input_dir> <output_dir> [OPTIONS]

Arguments:
  input_dir     Input directory with audio files (required)
  output_dir    Output directory for transcripts (required)

Options:
  --upload-concurrency      Number of concurrent uploads (default: 1)
  --processing-concurrency  Number of concurrent processing jobs (default: 8)
  --force / -f             Overwrite existing output files
  --rate-limit-ratio       Rate limit ratio of first upload (0.0-1.0, default: 1.0)
  ... (all convert options supported)
```

[Batch Command Details](./commands/batch.md)

### list - List Transcripts

List all transcripts from your AssemblyAI account.

```bash { .api }
aait list
```

### load - Load Transcript

Load a transcript by ID or negative index and open an interactive Python REPL with the transcript object available.

```bash { .api }
aait load <transcript_id>

Arguments:
  transcript_id    Transcript ID or negative integer index from `aait list`
```

### delete - Delete Transcript

Delete a transcript from AssemblyAI servers with optional confirmation prompt.

```bash { .api }
aait delete <transcript_id> [OPTIONS]

Arguments:
  transcript_id    Transcript ID or negative integer index from `aait list`

Options:
  --force / -f    Skip confirmation prompt
```

## Python API

### Enumerations

Output format, speech model, and boost parameter enumerations for transcription configuration.

```python { .api }
class OutputFormat(str, Enum):
    utterances = "utterances"    # Text with speaker labels
    paragraphs = "paragraphs"    # Text split into paragraphs
    text = "text"                # Plain text
    srt = "srt"                  # SRT subtitle format
    vtt = "vtt"                  # WebVTT subtitle format
    json_format = "json"         # JSON response from API

class SpeechModelChoice(str, Enum):
    best = "best"                # Best available model
    nano = "nano"                # Nano model
    slam_1 = "slam-1"            # SLAM-1 model
    universal = "universal"      # Universal model

class BoostParam(str, Enum):
    low = "low"                  # Low boost weight
    default = "default"          # Default boost weight
    high = "high"                # High boost weight
```

### Constants

```python { .api }
AUDIO_EXTENSIONS: set[str]
# Supported audio/video file extensions
# {".mp3", ".mp4", ".m4a", ".wav", ".flac", ".aac", ".ogg", ".opus", ".webm", ".wma"}
```

### Configuration Functions

API key loading and custom spelling parsing utilities.

```python { .api }
def load_api_key() -> str:
    """
    Load the AssemblyAI API key from environment or .env files.

    Search order:
    1. Environment variable ASSEMBLY_AI_KEY
    2. .env file in current directory
    3. ~/.assemblyai-tool.env file

    Returns:
        str: The API key

    Raises:
        RuntimeError: If no API key is found
    """

def parse_custom_spelling(spelling_str: str) -> dict:
    """
    Parse custom spelling string format.

    Args:
        spelling_str: Format 'from1:to1,from2:to2'
                     Example: "AI:A.I.,CEO:C.E.O."

    Returns:
        dict: Mapping of {to_word: from_word}
              Example: {"A.I.": "AI", "C.E.O.": "CEO"}
    """
```

[Python API Reference](./python-api.md)

## Supported Audio/Video Formats

The following file extensions are supported:
- Audio: `.mp3`, `.m4a`, `.wav`, `.flac`, `.aac`, `.ogg`, `.opus`, `.wma`
- Video: `.mp4`, `.webm`

## Key Features

### Output Formats
- **text**: Plain text transcript
- **paragraphs**: Text split into paragraphs
- **utterances**: Text with speaker labels (default)
- **srt**: SubRip subtitle format
- **vtt**: WebVTT subtitle format
- **json**: Full JSON response from API

### Speech Models
- **best**: Best available model (default)
- **nano**: Fast, lightweight model
- **slam-1**: SLAM-1 model
- **universal**: Universal model for all languages

### Advanced Audio Processing
- **Speaker Diarization**: Identify and label different speakers (2-10 speakers)
- **Sentiment Analysis**: Analyze sentiment of speech
- **Entity Detection**: Detect named entities in speech
- **Auto Chapters**: Automatically generate chapter markers
- **Auto Highlights**: Automatically identify key highlights

### Language Support
- **Language Detection**: Automatic language detection
- **Language Code**: Specify language explicitly (en, es, fr, etc.)

### Transcription Control
- **Audio Slicing**: Transcribe specific time ranges (start/end milliseconds)
- **Punctuation**: Enable/disable automatic punctuation
- **Word Boost**: Boost accuracy for specific words/phrases with adjustable weights
- **Custom Spelling**: Define custom spelling for specific words

### Batch Processing Features
- **Concurrent Uploads**: Configure upload parallelism
- **Concurrent Processing**: Configure transcription parallelism
- **Rate Limiting**: Fixed kbps or ratio-based rate limiting
- **Progress Tracking**: Real-time progress with upload and processing counts
- **Smart Skipping**: Skip existing files unless --force is specified

## Common Usage Patterns

### Speaker Diarization
```bash
# With expected speaker count
aait convert interview.mp3 transcript.txt \
  --speaker-labels \
  --speakers-expected 2

# Output format: utterances automatically includes speaker labels
```

### Content Analysis
```bash
# Full analysis suite
aait convert podcast.mp3 analysis.txt \
  --sentiment-analysis \
  --entity-detection \
  --auto-chapters \
  --auto-highlights
```

### Custom Vocabulary
```bash
# Boost technical terms
aait convert technical.mp3 output.txt \
  --word-boost "Kubernetes,API,GraphQL,React" \
  --boost-param high

# Custom spelling for acronyms
aait convert business.mp3 output.txt \
  --custom-spelling "AI:A.I.,CEO:C.E.O.,API:A.P.I."
```

### Rate Limited Batch Processing
```bash
# Fixed rate limit
aait batch ./audio ./output \
  --upload-concurrency 3 \
  --rate-limit-kbps 500

# Ratio-based rate limit (50% of first upload speed)
aait batch ./audio ./output \
  --upload-concurrency 3 \
  --rate-limit-ratio 0.5
```

### Subtitle Generation
```bash
# Generate SRT subtitles
aait convert video.mp4 subtitles.srt --format srt

# Generate VTT subtitles
aait convert video.mp4 subtitles.vtt --format vtt
```

## Error Handling

- Missing API key raises `RuntimeError` with helpful message
- Invalid file paths raise appropriate errors
- Failed transcriptions report error and exit with code 1
- Upload failures raise `RuntimeError` with details
- Invalid rate limit ratios (not in 0.0-1.0) exit with error message

## Progress Indicators

Progress tracking uses `tqdm` progress bars:
- **Upload Progress**: Shows file size and upload speed
- **Processing Progress**: Shows transcription completion percentage
- **Batch Progress**: Shows concurrent upload/processing counts
- Disable with `--no-show-progress` flag
