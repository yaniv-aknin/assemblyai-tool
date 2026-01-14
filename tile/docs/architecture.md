# Architecture

This document describes the key architectural components and design patterns used in assemblyai-tool to help understand its internal structure and design decisions.

## CLI Application Structure

The tool is built using the Typer framework, which provides a decorator-based approach to defining CLI commands.

### Application Lifecycle

```
User invokes CLI → callback() loads API key → Command executes → Exit
                           ↓
                    aai.settings.api_key set
```

**Components**:
- **app**: Main Typer application instance
- **callback()**: Pre-command initialization (loads API key)
- **Commands**: Individual command functions decorated with `@app.command()`
- **version_callback()**: Handles `--version` flag

### Command Organization

The CLI provides 5 commands organized into functional groups:

**Transcription Commands**:
- `convert`: Single file transcription
- `batch`: Multi-file batch processing

**Management Commands**:
- `list`: List all transcripts
- `load`: Load transcript by ID (opens REPL)
- `delete`: Delete transcript from server

## Rate Limiting Architecture

The rate limiting system supports both fixed and adaptive bandwidth control for batch uploads.

### Rate Limiter Design

```
_RateLimiter
├── Fixed mode: rate_limit_kbps > 0
├── Ratio mode: rate_limit_ratio < 1.0
└── Combined mode: Both specified (ratio takes precedence after first upload)
```

**Key Components**:
- **_RateLimiter**: Thread-safe rate limiter with dual modes
- **first_upload_speed_kbps**: Baseline speed for ratio calculations
- **effective_limit_kbps**: Computed limit based on ratio
- **Lock**: Thread synchronization for concurrent access

### Rate Limiting Flow

1. **First Upload**: No rate limiting, measures baseline speed
2. **Subsequent Uploads**: Apply limit based on:
   - Fixed limit: `rate_limit_kbps` (if > 0)
   - Ratio limit: `first_upload_speed * rate_limit_ratio` (if ratio < 1.0)
3. **Delay Calculation**: `delay = bytes / (limit_kbps * 1024)`

**Thread Safety**: Single shared rate limiter instance across all uploads with lock-protected state.

## Concurrency Model

The batch command implements a two-phase concurrency model with separate semaphores for uploads and processing.

### Concurrency Architecture

```
Input Files
    ↓
Upload Pool (upload_concurrency)
    ↓
Upload URLs
    ↓
Processing Pool (processing_concurrency)
    ↓
Completed Transcripts
```

### Semaphore Controls

**Upload Semaphore**:
- Limits concurrent file uploads to AssemblyAI
- Default: 1 (sequential uploads)
- Controls network bandwidth usage

**Processing Semaphore**:
- Limits concurrent transcription jobs
- Default: 8 (parallel processing)
- Controls API rate limits and concurrency

**Total Threads**: `upload_concurrency + processing_concurrency`

### State Tracking

Thread-safe counters with locks:
- `uploading_count`: Files currently uploading
- `processing_count`: Files currently being transcribed
- `completed_count`: Successfully completed files
- `failed_count`: Failed transcriptions
- `first_upload_done`: Flag for rate limiter initialization

## Progress Tracking System

Multi-level progress tracking with thread-local storage for concurrent operations.

### Progress Components

**Upload Progress** (_ProgressFileReader):
- Wraps file objects to track read operations
- Thread-local progress bars (`_upload_progress_bars`)
- Displays: file size, upload speed, rate limit info

**Processing Progress** (make_transcript):
- Polls transcript status during transcription
- Shows: completion percentage (0-100%)
- Updates incrementally: queued → processing → completed

**Batch Progress** (batch command):
- Overall progress bar for entire batch
- Postfix display: `{uploading} u/l; {processing} asr`
- Updates: after each file completion or failure

### Thread-Local Storage

```python
_upload_progress_bars = threading.local()
```

Ensures each upload thread has its own progress bar without conflicts.

## File Upload Pipeline

Sophisticated upload system with progress tracking and rate limiting integration.

### Upload Flow

1. **Create ProgressFileReader**: Wraps file with progress/rate tracking
2. **HTTP Client**: Uses custom httpx client with AssemblyAI credentials
3. **Streaming Upload**: POST to `/v2/upload` endpoint
4. **Speed Measurement**: Track bytes/time for rate limiter
5. **Response Handling**: Extract upload_url from JSON response

**Key Class**: `_ProgressFileReader`
- Implements file-like interface with `read()` method
- Intercepts reads to update progress and apply rate limiting
- Calculates upload speed for ratio-based limiting
- Iterator support for chunked streaming

## Transcription Configuration

Unified configuration management through dataclasses and enums.

### Configuration Layers

**Data Class**: `TranscribeOptions`
- 19 fields covering all transcription parameters
- Shared between convert and batch commands
- Single source of truth for configuration

**Enumerations**:
- `OutputFormat`: 6 output format choices
- `SpeechModelChoice`: 4 speech model options
- `BoostParam`: 3 word boost weight levels

**Mapping Layer**:
- Converts tool enums to AssemblyAI SDK enums
- Example: `SpeechModelChoice.best` → `aai.SpeechModel.best`

### Configuration Flow

```
CLI Options → TranscribeOptions → Config Dict → aai.TranscriptionConfig
```

## Error Handling Strategy

### Command-Level Errors

**convert command**:
- Transcript error: Print to stderr, exit code 1
- Upload failure: Raise RuntimeError
- API key missing: Exit in callback

**batch command**:
- Individual file errors: Log and continue
- Track failed count, report at end
- Exit code 0 (batch completes even with failures)

**Management commands**:
- list: No special error handling
- load: Opens REPL (errors handled by Python)
- delete: Print error to stderr, exit code 1

### Progress Bar Error Handling

All progress bars include try/finally blocks to ensure cleanup:
```python
try:
    # Upload/process with progress
finally:
    if progress_bar:
        progress_bar.close()
```

## API Key Management

Multi-source API key loading with precedence order.

### Key Loading Strategy

1. **Environment Variable**: `ASSEMBLY_AI_KEY`
2. **Current Directory**: `.env` file
3. **Home Directory**: `~/.assemblyai-tool.env` file

**Implementation**: `load_api_key()` function
- Uses python-dotenv for `.env` parsing
- Returns API key string
- Raises RuntimeError if not found

### Initialization

The `callback()` function sets the global API key:
```python
aai.settings.api_key = load_api_key()
```

This runs before every command, ensuring the SDK is configured.

## Output Formatting

Flexible output formatting with format-specific handling.

### Format Implementations

**text**: Direct transcript text (`transcript.text`)

**paragraphs**: Uses `transcript.get_paragraphs()`
- Groups text into logical paragraphs
- Preserves paragraph structure

**utterances**: Individual utterances
- With speaker_labels: `"Speaker A: text"`
- Without: Just text

**srt/vtt**: Subtitle formats
- `transcript.export_subtitles_srt()`
- `transcript.export_subtitles_vtt()`
- Include timing information

**json**: Full API response
- `transcript.json_response`
- Includes all metadata

### Format-Extension Mapping

```python
output_ext_map = {
    OutputFormat.text: ".txt",
    OutputFormat.paragraphs: ".txt",
    OutputFormat.utterances: ".txt",
    OutputFormat.srt: ".srt",
    OutputFormat.vtt: ".vtt",
    OutputFormat.json_format: ".json",
}
```

## Design Decisions

### Why Two-Phase Concurrency?

**Separation of Concerns**:
- Upload is network-bound (bandwidth limited)
- Processing is API-bound (service capacity limited)
- Different optimal concurrency levels for each phase

**Resource Optimization**:
- Low upload concurrency conserves bandwidth
- High processing concurrency maximizes throughput
- Rate limiter prevents bandwidth saturation

### Why Thread-Local Progress Bars?

**Concurrency Safety**:
- Multiple concurrent uploads each need their own progress bar
- Thread-local storage prevents conflicts
- Each thread updates only its own bar

### Why Shared Rate Limiter?

**Consistent Rate Limiting**:
- Single limiter ensures aggregate rate control
- First upload establishes baseline for all
- Thread-safe design allows safe concurrent access

### Why Ratio-Based Limiting?

**Adaptive Bandwidth Control**:
- Network speeds vary by environment
- Fixed limits may be too high or too low
- Ratio adapts to measured baseline speed
- Provides predictable bandwidth usage (e.g., "use 50% of available")
