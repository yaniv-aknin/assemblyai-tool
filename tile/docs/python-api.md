# Python API Reference

Direct Python API for programmatic transcription without using the CLI. Provides functions for file upload, transcription, output formatting, and configuration management.

## Module Import

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
    process_single_file,
    version_callback,
    callback
)
```

## Capabilities

### Configuration Management

#### API Key Loading

Load the AssemblyAI API key from environment or configuration files.

```python { .api }
def load_api_key() -> str:
    """
    Load the AssemblyAI API key from environment or .env files.

    Search order:
    1. Environment variable: ASSEMBLY_AI_KEY
    2. .env file in current directory
    3. ~/.assemblyai-tool.env file

    Returns:
        str: The API key

    Raises:
        RuntimeError: If no API key is found in any of the locations
    """
```

**Example**:
```python
from assemblyai_tool import load_api_key
import assemblyai as aai

# Load and configure API key
api_key = load_api_key()
aai.settings.api_key = api_key

# Now ready to use AssemblyAI
```

#### Custom Spelling Parser

Parse custom spelling string format into dictionary mapping.

```python { .api }
def parse_custom_spelling(spelling_str: str) -> dict:
    """
    Parse custom spelling string format.

    Args:
        spelling_str (str): Format 'from1:to1,from2:to2'
                           Example: "AI:A.I.,CEO:C.E.O."

    Returns:
        dict: Mapping of {to_word: from_word}
              Example: {"A.I.": "AI", "C.E.O.": "CEO"}

    Notes:
        - Empty string returns empty dict
        - Pairs without ':' are skipped
        - Whitespace around words is stripped
    """
```

**Examples**:
```python
from assemblyai_tool import parse_custom_spelling

# Basic usage
mapping = parse_custom_spelling("AI:A.I.,CEO:C.E.O.")
# Returns: {"A.I.": "AI", "C.E.O.": "CEO"}

# Multiple mappings
mapping = parse_custom_spelling("API:A.P.I.,URL:U.R.L.,SQL:S.Q.L.")
# Returns: {"A.P.I.": "API", "U.R.L.": "URL", "S.Q.L.": "SQL"}

# Empty string
mapping = parse_custom_spelling("")
# Returns: {}
```

### File Upload

Upload audio files to AssemblyAI with progress tracking and rate limiting.

```python { .api }
def upload_file_with_progress(
    inpath: str,
    show_progress: bool,
    rate_limit_kbps: float = 0.0,
    rate_limit_ratio: Optional[float] = None,
    is_first_upload: bool = False,
    shared_rate_limiter: Optional[_RateLimiter] = None,
) -> Tuple[str, float]:
    """
    Upload a file to AssemblyAI with progress tracking and rate limiting.

    Args:
        inpath (str): Path to file to upload
        show_progress (bool): Whether to show tqdm progress bar
        rate_limit_kbps (float): Rate limit in kbps (0 = no limit)
        rate_limit_ratio (Optional[float]): Rate limit as ratio of first upload speed
        is_first_upload (bool): Whether this is the first upload in a batch
        shared_rate_limiter (Optional[_RateLimiter]): Shared rate limiter instance

    Returns:
        Tuple[str, float]: (upload_url, upload_speed_kbps)
            upload_url: URL where file was uploaded
            upload_speed_kbps: Measured upload speed in kbps

    Raises:
        RuntimeError: If upload fails (non-200 status code)

    Notes:
        - First upload is never rate-limited when using ratio-based limiting
        - Progress bar is thread-local for concurrent uploads
        - Rate limiter can be shared across multiple uploads
    """
```

**Examples**:
```python
from assemblyai_tool import upload_file_with_progress

# Basic upload with progress
url, speed = upload_file_with_progress("audio.mp3", show_progress=True)
print(f"Uploaded to: {url}, Speed: {speed:.2f} kbps")

# Upload without progress
url, speed = upload_file_with_progress("audio.mp3", show_progress=False)

# Upload with fixed rate limit
url, speed = upload_file_with_progress(
    "audio.mp3",
    show_progress=True,
    rate_limit_kbps=500.0  # 500 kbps limit
)

# First upload for ratio-based limiting
url, speed = upload_file_with_progress(
    "audio.mp3",
    show_progress=True,
    is_first_upload=True
)
```

### Transcription

Create transcripts with comprehensive configuration options.

```python { .api }
def make_transcript(
    inpath: str,
    speech_model: SpeechModelChoice,
    language_code: Optional[str],
    language_detection: bool,
    audio_start_from: Optional[int],
    audio_end_at: Optional[int],
    punctuate: bool,
    word_boost: Optional[list[str]],
    boost_param: BoostParam,
    custom_spelling: Optional[dict],
    speaker_labels: bool,
    speakers_expected: Optional[int],
    sentiment_analysis: bool,
    entity_detection: bool,
    auto_chapters: bool,
    auto_highlights: bool,
    show_progress: bool,
    rate_limit_kbps: float = 0.0,
    rate_limit_ratio: Optional[float] = None,
) -> aai.Transcript:
    """
    Create a transcript with specified configuration.

    Args:
        inpath (str): Path to audio file
        speech_model (SpeechModelChoice): Speech recognition model
        language_code (Optional[str]): Language code (e.g., 'en', 'es', 'fr')
        language_detection (bool): Enable automatic language detection
        audio_start_from (Optional[int]): Start time in milliseconds
        audio_end_at (Optional[int]): End time in milliseconds
        punctuate (bool): Enable automatic punctuation
        word_boost (Optional[list[str]]): List of words to boost
        boost_param (BoostParam): Boost parameter weight
        custom_spelling (Optional[dict]): Custom spelling mappings
        speaker_labels (bool): Enable speaker diarization
        speakers_expected (Optional[int]): Expected number of speakers (2-10)
        sentiment_analysis (bool): Enable sentiment analysis
        entity_detection (bool): Enable entity detection
        auto_chapters (bool): Enable auto chapters
        auto_highlights (bool): Enable auto highlights
        show_progress (bool): Show progress bars
        rate_limit_kbps (float): Upload rate limit in kbps
        rate_limit_ratio (Optional[float]): Rate limit ratio

    Returns:
        aai.Transcript: The completed or failed transcript object

    Notes:
        - Handles upload, submission, and polling for completion
        - If show_progress=True, displays upload and processing progress
        - Returns transcript regardless of success/error status
        - Check transcript.status for success (completed) or failure (error)
    """
```

**Examples**:
```python
from assemblyai_tool import make_transcript, SpeechModelChoice, BoostParam
import assemblyai as aai

# Initialize API key
aai.settings.api_key = "your_api_key"

# Basic transcription
transcript = make_transcript(
    inpath="audio.mp3",
    speech_model=SpeechModelChoice.best,
    language_code=None,
    language_detection=True,
    audio_start_from=None,
    audio_end_at=None,
    punctuate=True,
    word_boost=None,
    boost_param=BoostParam.default,
    custom_spelling=None,
    speaker_labels=False,
    speakers_expected=None,
    sentiment_analysis=False,
    entity_detection=False,
    auto_chapters=False,
    auto_highlights=False,
    show_progress=True
)

# With speaker diarization
transcript = make_transcript(
    inpath="interview.mp3",
    speech_model=SpeechModelChoice.best,
    language_code="en",
    language_detection=False,
    audio_start_from=None,
    audio_end_at=None,
    punctuate=True,
    word_boost=None,
    boost_param=BoostParam.default,
    custom_spelling=None,
    speaker_labels=True,
    speakers_expected=2,
    sentiment_analysis=False,
    entity_detection=False,
    auto_chapters=False,
    auto_highlights=False,
    show_progress=True
)

# With vocabulary boosting
transcript = make_transcript(
    inpath="technical.mp3",
    speech_model=SpeechModelChoice.best,
    language_code="en",
    language_detection=False,
    audio_start_from=None,
    audio_end_at=None,
    punctuate=True,
    word_boost=["Kubernetes", "Docker", "API"],
    boost_param=BoostParam.high,
    custom_spelling={"A.P.I.": "API"},
    speaker_labels=False,
    speakers_expected=None,
    sentiment_analysis=False,
    entity_detection=False,
    auto_chapters=False,
    auto_highlights=False,
    show_progress=False
)
```

### Output Formatting

Format transcripts into various output formats.

```python { .api }
def format_output(
    transcript: aai.Transcript,
    output_format: OutputFormat,
    speaker_labels: bool,
) -> str:
    """
    Format transcript based on output format choice.

    Args:
        transcript (aai.Transcript): The transcript to format
        output_format (OutputFormat): Desired output format
        speaker_labels (bool): Whether speaker labels were enabled

    Returns:
        str: Formatted transcript text

    Output Formats:
        text: Plain text of transcript
        paragraphs: Text split into paragraphs
        utterances: Text with speaker labels (if enabled)
        srt: SRT subtitle format
        vtt: WebVTT subtitle format
        json_format: JSON response from API

    Notes:
        - For utterances with speaker_labels=True, includes "Speaker X:" prefix
        - For utterances with speaker_labels=False, just the text
        - Paragraphs format groups text into logical paragraphs
        - SRT and VTT include timing information
        - JSON includes full API response data
    """
```

**Examples**:
```python
from assemblyai_tool import format_output, OutputFormat
import assemblyai as aai

# Assuming you have a transcript object
# transcript = ...

# Plain text
text = format_output(transcript, OutputFormat.text, speaker_labels=False)

# Paragraphs
paragraphs = format_output(transcript, OutputFormat.paragraphs, speaker_labels=False)

# Utterances with speaker labels
utterances = format_output(transcript, OutputFormat.utterances, speaker_labels=True)
# Output: "Speaker A: Hello there\nSpeaker B: Hi, how are you?\n..."

# SRT subtitles
srt = format_output(transcript, OutputFormat.srt, speaker_labels=False)

# VTT subtitles
vtt = format_output(transcript, OutputFormat.vtt, speaker_labels=False)

# Full JSON
import json
json_str = format_output(transcript, OutputFormat.json_format, speaker_labels=False)
data = json.loads(json_str)
```

### Complete File Processing

Process a single audio file end-to-end with all options.

```python { .api }
def process_single_file(
    inpath: Path,
    outpath: Path,
    opts: TranscribeOptions,
) -> None:
    """
    Process a single audio file with given options and write output.

    Args:
        inpath (Path): Input file path
        outpath (Path): Output file path
        opts (TranscribeOptions): Transcription options container

    Returns:
        None: Writes output to file

    Raises:
        typer.Exit(1): If transcription fails (status is error)

    Notes:
        - Complete workflow: upload, transcribe, format, write
        - Handles word_boost string-to-list conversion
        - Handles custom_spelling string-to-dict conversion
        - Prints error to stderr and exits on transcription failure
        - Saves output to specified path on success
    """
```

**Examples**:
```python
from assemblyai_tool import process_single_file, TranscribeOptions, OutputFormat, SpeechModelChoice, BoostParam
from pathlib import Path

# Create options
opts = TranscribeOptions(
    format=OutputFormat.text,
    speech_model=SpeechModelChoice.best,
    language_code="en",
    language_detection=False,
    audio_start_from=None,
    audio_end_at=None,
    punctuate=True,
    word_boost=None,
    boost_param=BoostParam.default,
    custom_spelling=None,
    speaker_labels=False,
    speakers_expected=None,
    sentiment_analysis=False,
    entity_detection=False,
    auto_chapters=False,
    auto_highlights=False,
    show_progress=True,
    rate_limit_kbps=0.0,
    rate_limit_ratio=None
)

# Process file
process_single_file(
    inpath=Path("audio.mp3"),
    outpath=Path("transcript.txt"),
    opts=opts
)
```

## Data Classes

### TranscribeOptions

Container for all transcription configuration options.

```python { .api }
@dataclass
class TranscribeOptions:
    """Shared transcription options."""

    format: OutputFormat
    speech_model: SpeechModelChoice
    language_code: Optional[str]
    language_detection: bool
    audio_start_from: Optional[int]
    audio_end_at: Optional[int]
    punctuate: bool
    word_boost: Optional[str]
    boost_param: BoostParam
    custom_spelling: Optional[str]
    speaker_labels: bool
    speakers_expected: Optional[int]
    sentiment_analysis: bool
    entity_detection: bool
    auto_chapters: bool
    auto_highlights: bool
    show_progress: bool
    rate_limit_kbps: float
    rate_limit_ratio: Optional[float]
```

**Example**:
```python
from assemblyai_tool import TranscribeOptions, OutputFormat, SpeechModelChoice, BoostParam

opts = TranscribeOptions(
    format=OutputFormat.utterances,
    speech_model=SpeechModelChoice.best,
    language_code=None,
    language_detection=True,
    audio_start_from=None,
    audio_end_at=None,
    punctuate=True,
    word_boost="API,GraphQL,React",
    boost_param=BoostParam.high,
    custom_spelling="API:A.P.I.",
    speaker_labels=True,
    speakers_expected=2,
    sentiment_analysis=True,
    entity_detection=True,
    auto_chapters=False,
    auto_highlights=False,
    show_progress=True,
    rate_limit_kbps=500.0,
    rate_limit_ratio=None
)
```

## Enumerations

### OutputFormat

```python { .api }
class OutputFormat(str, Enum):
    """Output format options."""
    utterances = "utterances"    # Text with speaker labels
    paragraphs = "paragraphs"    # Text split into paragraphs
    text = "text"                # Plain text
    srt = "srt"                  # SRT subtitle format
    vtt = "vtt"                  # WebVTT subtitle format
    json_format = "json"         # JSON response from API
```

### SpeechModelChoice

```python { .api }
class SpeechModelChoice(str, Enum):
    """Speech model options."""
    best = "best"                # Best available model
    nano = "nano"                # Nano model
    slam_1 = "slam-1"            # SLAM-1 model
    universal = "universal"      # Universal model
```

### BoostParam

```python { .api }
class BoostParam(str, Enum):
    """Word boost parameter options."""
    low = "low"                  # Low boost weight
    default = "default"          # Default boost weight
    high = "high"                # High boost weight
```

## Constants

### AUDIO_EXTENSIONS

```python { .api }
AUDIO_EXTENSIONS: set[str]
# Supported audio/video file extensions
# {".mp3", ".mp4", ".m4a", ".wav", ".flac", ".aac", ".ogg", ".opus", ".webm", ".wma"}
```

**Example**:
```python
from assemblyai_tool import AUDIO_EXTENSIONS
from pathlib import Path

def is_audio_file(filepath: Path) -> bool:
    return filepath.suffix.lower() in AUDIO_EXTENSIONS

# Usage
if is_audio_file(Path("audio.mp3")):
    print("Valid audio file")
```

## CLI Application

### Typer App

The main Typer application for CLI usage.

```python { .api }
app: typer.Typer
# Main CLI application with commands: convert, batch, list, load, delete
```

**Example**:
```python
from assemblyai_tool import app

# Run the CLI programmatically
if __name__ == "__main__":
    app()
```

### CLI Callbacks

Functions for managing CLI behavior and lifecycle.

#### Version Callback

Display version information and exit.

```python { .api }
def version_callback(value: bool) -> None:
    """
    Display version information and exit when --version flag is used.

    Args:
        value (bool): Flag value from Typer option

    Raises:
        typer.Exit: Always exits after displaying version

    Notes:
        - Automatically invoked by Typer when --version is passed
        - Prints version in format: "aait {version}"
        - Version is retrieved from package metadata
        - Prints "unknown" if package metadata unavailable
    """
```

**Example**:
```python
from assemblyai_tool import version_callback

# Used internally by Typer for --version flag
# Not typically called directly in user code
```

#### Main Callback

Initialize the AssemblyAI API key before any command execution.

```python { .api }
def callback(
    version_flag: Optional[bool] = None,
) -> None:
    """
    Main Typer callback that runs before any command.

    Initializes the AssemblyAI API key from environment or config files.

    Args:
        version_flag (Optional[bool]): Version flag handled by version_callback

    Raises:
        typer.Exit(1): If API key cannot be loaded

    Notes:
        - Automatically invoked by Typer before command execution
        - Loads API key using load_api_key()
        - Sets aai.settings.api_key for all commands
        - Prints error to stderr if key not found
    """
```

**Example**:
```python
from assemblyai_tool import app, callback
import typer

# The callback is registered with the Typer app
# and runs automatically before commands

# You can also use it directly to initialize the API
try:
    callback()
    # API key is now loaded
except typer.Exit:
    print("Failed to load API key")
```

## Complete Usage Example

```python
import assemblyai as aai
from assemblyai_tool import (
    load_api_key,
    make_transcript,
    format_output,
    OutputFormat,
    SpeechModelChoice,
    BoostParam,
    parse_custom_spelling
)

# Configure API key
aai.settings.api_key = load_api_key()

# Parse custom spelling
custom_spelling_dict = parse_custom_spelling("API:A.P.I.,CEO:C.E.O.")

# Create transcript
transcript = make_transcript(
    inpath="interview.mp3",
    speech_model=SpeechModelChoice.best,
    language_code="en",
    language_detection=False,
    audio_start_from=None,
    audio_end_at=None,
    punctuate=True,
    word_boost=["TechCorp", "CloudPlatform"],
    boost_param=BoostParam.high,
    custom_spelling=custom_spelling_dict,
    speaker_labels=True,
    speakers_expected=2,
    sentiment_analysis=True,
    entity_detection=True,
    auto_chapters=False,
    auto_highlights=False,
    show_progress=True,
    rate_limit_kbps=0.0,
    rate_limit_ratio=None
)

# Check status
if transcript.status == aai.TranscriptStatus.error:
    print(f"Error: {transcript.error}")
else:
    # Format output
    output = format_output(transcript, OutputFormat.utterances, speaker_labels=True)

    # Save to file
    with open("output.txt", "w") as f:
        f.write(output)

    print(f"Transcription complete: {transcript.audio_duration / 60:.1f} minutes")
```
