from pathlib import Path
import typing as t
import typer
import dotenv
import assemblyai as aai
import os
import sys
import code
import json
from enum import Enum
from importlib.metadata import version, PackageNotFoundError
import threading
import time
import httpx
from tqdm import tqdm

app = typer.Typer()


class OutputFormat(str, Enum):
    """Output format options"""

    utterances = "utterances"
    paragraphs = "paragraphs"
    text = "text"
    srt = "srt"
    vtt = "vtt"
    json_format = "json"


class SpeechModelChoice(str, Enum):
    """Speech model options"""

    best = "best"
    nano = "nano"
    slam_1 = "slam-1"
    universal = "universal"


class BoostParam(str, Enum):
    """Word boost parameter options"""

    low = "low"
    default = "default"
    high = "high"


def load_api_key() -> None:
    if os.environ.get("ASSEMBLY_AI_KEY"):
        return os.environ["ASSEMBLY_AI_KEY"]
    vars = dotenv.dotenv_values()
    if vars.get("ASSEMBLY_AI_KEY"):
        return vars["ASSEMBLY_AI_KEY"]
    default_env = Path.home() / ".assemblyai-tool.env"
    if default_env.exists():
        vars = dotenv.dotenv_values(default_env)
        if vars.get("ASSEMBLY_AI_KEY"):
            return vars["ASSEMBLY_AI_KEY"]
    raise RuntimeError("No API key found")


def estimate_cost(audio_duration_seconds: float, features: dict) -> float:
    """Estimate the cost of transcription in USD.

    Base rates (as of 2024):
    - Standard transcription: $0.00025/second ($0.015/minute)
    - Additional features add to base cost
    """
    base_cost = audio_duration_seconds * 0.00025

    # Features that add cost (rough estimates)
    additional_cost = 0.0
    if features.get("speaker_labels"):
        additional_cost += audio_duration_seconds * 0.00006
    if features.get("sentiment_analysis"):
        additional_cost += audio_duration_seconds * 0.00003
    if features.get("entity_detection"):
        additional_cost += audio_duration_seconds * 0.00003
    if features.get("auto_chapters"):
        additional_cost += audio_duration_seconds * 0.00003
    if features.get("auto_highlights"):
        additional_cost += audio_duration_seconds * 0.00003
    if features.get("summarization"):
        additional_cost += audio_duration_seconds * 0.00003

    return base_cost + additional_cost


def parse_custom_spelling(spelling_str: str) -> dict:
    """Parse custom spelling string format: 'from1:to1,from2:to2'"""
    result = {}
    if not spelling_str:
        return result

    for pair in spelling_str.split(","):
        if ":" not in pair:
            continue
        from_word, to_word = pair.split(":", 1)
        result[to_word.strip()] = from_word.strip()

    return result


_upload_progress_bars = threading.local()


def _get_upload_progress_bar() -> t.Optional[tqdm]:
    """Get the thread-local upload progress bar."""
    return getattr(_upload_progress_bars, "bar", None)


def _set_upload_progress_bar(bar: t.Optional[tqdm]) -> None:
    """Set the thread-local upload progress bar."""
    _upload_progress_bars.bar = bar


class _ProgressFileReader:
    """Wrapper that tracks read progress for file uploads."""

    def __init__(self, file_path: str, progress_bar: t.Optional[tqdm]):
        self.file = open(file_path, "rb")
        self.progress_bar = progress_bar
        self.size = os.path.getsize(file_path)

    def read(self, size: int = -1) -> bytes:
        data = self.file.read(size)
        if self.progress_bar and data:
            self.progress_bar.update(len(data))
        return data

    def __iter__(self):
        chunk_size = 8192
        while True:
            chunk = self.read(chunk_size)
            if not chunk:
                break
            yield chunk

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def upload_file_with_progress(inpath: str, show_progress: bool) -> str:
    """Upload a file to AssemblyAI with progress tracking."""
    file_size = os.path.getsize(inpath)

    progress_bar = None
    if show_progress:
        progress_bar = tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="Uploading",
        )
        _set_upload_progress_bar(progress_bar)

    try:
        client = aai.Client.get_default()
        http_client = client.http_client

        custom_client = httpx.Client(
            base_url=str(http_client.base_url),
            headers=http_client.headers,
            timeout=http_client.timeout,
        )

        with _ProgressFileReader(inpath, progress_bar) as f:
            response = custom_client.post("/v2/upload", content=f)

        if response.status_code != httpx.codes.OK:
            raise RuntimeError(f"Upload failed: {response.text}")

        upload_url = response.json()["upload_url"]

        if progress_bar:
            progress_bar.close()
            _set_upload_progress_bar(None)

        return upload_url

    except Exception:
        if progress_bar:
            progress_bar.close()
            _set_upload_progress_bar(None)
        raise


def make_transcript(
    inpath: str,
    speech_model: SpeechModelChoice,
    language_code: t.Optional[str],
    language_detection: bool,
    audio_start_from: t.Optional[int],
    audio_end_at: t.Optional[int],
    punctuate: bool,
    word_boost: t.Optional[list[str]],
    boost_param: BoostParam,
    custom_spelling: t.Optional[dict],
    speaker_labels: bool,
    speakers_expected: t.Optional[int],
    sentiment_analysis: bool,
    entity_detection: bool,
    auto_chapters: bool,
    auto_highlights: bool,
    show_progress: bool,
) -> aai.Transcript:
    """Create a transcript with the specified configuration."""

    speech_model_map = {
        SpeechModelChoice.best: aai.SpeechModel.best,
        SpeechModelChoice.nano: aai.SpeechModel.nano,
        SpeechModelChoice.slam_1: aai.SpeechModel.slam_1,
        SpeechModelChoice.universal: aai.SpeechModel.universal,
    }

    config_params = {
        "speech_model": speech_model_map[speech_model],
        "punctuate": punctuate,
        "speaker_labels": speaker_labels,
        "sentiment_analysis": sentiment_analysis,
        "entity_detection": entity_detection,
        "auto_chapters": auto_chapters,
        "auto_highlights": auto_highlights,
    }

    if language_code:
        config_params["language_code"] = language_code
    else:
        config_params["language_detection"] = language_detection

    if audio_start_from is not None:
        config_params["audio_start_from"] = audio_start_from
    if audio_end_at is not None:
        config_params["audio_end_at"] = audio_end_at

    if word_boost:
        config_params["word_boost"] = word_boost
        config_params["boost_param"] = getattr(aai.types.WordBoost, boost_param.value)

    if custom_spelling:
        config_params["custom_spelling"] = custom_spelling

    if speakers_expected is not None:
        config_params["speakers_expected"] = speakers_expected

    config = aai.TranscriptionConfig(**config_params)
    transcriber = aai.Transcriber(config=config)

    upload_url = upload_file_with_progress(str(inpath), show_progress)

    processing_bar = None
    if show_progress:
        processing_bar = tqdm(
            total=100,
            unit="%",
            desc="Processing",
            bar_format="{l_bar}{bar}| {n:.0f}/{total:.0f}%",
        )

    transcript = transcriber.submit(upload_url)

    if show_progress:
        polling_interval = aai.settings.polling_interval
        started_processing = False

        while transcript.status not in (
            aai.TranscriptStatus.completed,
            aai.TranscriptStatus.error,
        ):
            time.sleep(polling_interval)

            client = aai.Client.get_default()
            response = client.http_client.get(f"/v2/transcript/{transcript.id}")
            if response.status_code == 200:
                transcript_data = response.json()
                transcript = aai.Transcript.from_response(
                    client=client,
                    response=aai.types.TranscriptResponse.parse_obj(transcript_data),
                )

            if transcript.status == aai.TranscriptStatus.processing:
                if not started_processing:
                    started_processing = True
                    if processing_bar:
                        processing_bar.update(30)
                elif processing_bar and processing_bar.n < 90:
                    processing_bar.update(10)

        if transcript.status == aai.TranscriptStatus.completed and processing_bar:
            processing_bar.n = 100
            processing_bar.refresh()

        if processing_bar:
            processing_bar.close()

        if transcript.status == aai.TranscriptStatus.completed:
            duration_mins = (
                transcript.audio_duration / 60 if transcript.audio_duration else 0
            )
            print(f"✓ Transcription complete ({duration_mins:.1f} minutes)")
    else:
        transcript = transcript.wait_for_completion()

    return transcript


def format_output(
    transcript: aai.Transcript,
    output_format: OutputFormat,
    speaker_labels: bool,
) -> str:
    """Format transcript based on output format choice."""

    if output_format == OutputFormat.text:
        return transcript.text

    elif output_format == OutputFormat.paragraphs:
        paragraphs = transcript.get_paragraphs()
        if speaker_labels and transcript.utterances:
            # Group paragraphs by speaker
            output = []
            for para in paragraphs:
                output.append(f"{para.text}\n")
            return "\n".join(output)
        else:
            return "\n\n".join(p.text for p in paragraphs)

    elif output_format == OutputFormat.srt:
        return transcript.export_subtitles_srt()

    elif output_format == OutputFormat.vtt:
        return transcript.export_subtitles_vtt()

    elif output_format == OutputFormat.json_format:
        return json.dumps(transcript.json_response, indent=2)

    elif transcript.utterances:
        output = []
        for utterance in transcript.utterances:
            if speaker_labels:
                output.append(f"Speaker {utterance.speaker}: {utterance.text}\n")
            else:
                output.append(f"{utterance.text}\n")
        return "\n".join(output)

    else:
        return transcript.text


@app.command()
def convert(
    inpath: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, help="Input audio/video file")
    ],
    outpath: t.Annotated[Path, typer.Argument(dir_okay=False, help="Output file path")],
    # Output format
    format: t.Annotated[
        OutputFormat, typer.Option(help="Output format")
    ] = OutputFormat.utterances,
    # Model and language
    speech_model: t.Annotated[
        SpeechModelChoice, typer.Option(help="Speech model to use")
    ] = SpeechModelChoice.best,
    language_code: t.Annotated[
        t.Optional[str],
        typer.Option(
            help="Language code (e.g., en, es, fr). Overrides language-detection"
        ),
    ] = None,
    language_detection: t.Annotated[
        bool, typer.Option(help="Enable automatic language detection")
    ] = False,
    # Audio slicing
    audio_start_from: t.Annotated[
        t.Optional[int], typer.Option(help="Start transcription from this millisecond")
    ] = None,
    audio_end_at: t.Annotated[
        t.Optional[int], typer.Option(help="End transcription at this millisecond")
    ] = None,
    # Text formatting
    punctuate: t.Annotated[
        bool, typer.Option(help="Enable automatic punctuation")
    ] = True,
    # Custom vocabulary
    word_boost: t.Annotated[
        t.Optional[str],
        typer.Option(help="Comma-separated list of words/phrases to boost accuracy"),
    ] = None,
    boost_param: t.Annotated[
        BoostParam, typer.Option(help="Weight to apply to boosted words")
    ] = BoostParam.default,
    custom_spelling: t.Annotated[
        t.Optional[str],
        typer.Option(help="Custom spelling mappings (format: 'from1:to1,from2:to2')"),
    ] = None,
    # Speaker diarization
    speaker_labels: t.Annotated[
        bool, typer.Option(help="Enable speaker diarization")
    ] = False,
    speakers_expected: t.Annotated[
        t.Optional[int], typer.Option(help="Expected number of speakers (2-10)")
    ] = None,
    # Content analysis
    sentiment_analysis: t.Annotated[
        bool, typer.Option(help="Enable sentiment analysis")
    ] = False,
    entity_detection: t.Annotated[
        bool, typer.Option(help="Enable entity detection")
    ] = False,
    auto_chapters: t.Annotated[bool, typer.Option(help="Enable auto chapters")] = False,
    auto_highlights: t.Annotated[
        bool, typer.Option(help="Enable auto highlights")
    ] = False,
    # UI options
    show_progress: t.Annotated[
        bool, typer.Option(help="Show progress messages")
    ] = True,
    estimate_cost_only: t.Annotated[
        bool, typer.Option("--estimate-cost", help="Estimate cost without transcribing")
    ] = False,
) -> None:
    """Convert a media file to text with various transcription options."""

    # Parse word boost
    word_boost_list = None
    if word_boost:
        word_boost_list = [w.strip() for w in word_boost.split(",")]

    # Parse custom spelling
    custom_spelling_dict = None
    if custom_spelling:
        custom_spelling_dict = parse_custom_spelling(custom_spelling)

    # Cost estimation
    if estimate_cost_only:
        # Get file info for rough estimate
        # For audio files, we'd need to actually probe the duration
        # For now, provide a message
        print("Cost estimation requires file duration. Typical rates:")
        print("  Base transcription: $0.015/minute")
        print("  Speaker labels: +$0.004/minute")
        print("  Content analysis features: +$0.002/minute each")
        features = {
            "speaker_labels": speaker_labels,
            "sentiment_analysis": sentiment_analysis,
            "entity_detection": entity_detection,
            "auto_chapters": auto_chapters,
            "auto_highlights": auto_highlights,
        }
        enabled_features = [k for k, v in features.items() if v]
        if enabled_features:
            print(f"  Enabled features: {', '.join(enabled_features)}")
        return

    # Create transcript
    transcript = make_transcript(
        inpath=str(inpath),
        speech_model=speech_model,
        language_code=language_code,
        language_detection=language_detection,
        audio_start_from=audio_start_from,
        audio_end_at=audio_end_at,
        punctuate=punctuate,
        word_boost=word_boost_list,
        boost_param=boost_param,
        custom_spelling=custom_spelling_dict,
        speaker_labels=speaker_labels,
        speakers_expected=speakers_expected,
        sentiment_analysis=sentiment_analysis,
        entity_detection=entity_detection,
        auto_chapters=auto_chapters,
        auto_highlights=auto_highlights,
        show_progress=show_progress,
    )

    # Check for errors
    if transcript.status == aai.TranscriptStatus.error:
        print(f"Error: {transcript.error}", file=sys.stderr)
        raise typer.Exit(1)

    # Show actual cost estimate
    if show_progress and transcript.audio_duration:
        features = {
            "speaker_labels": speaker_labels,
            "sentiment_analysis": sentiment_analysis,
            "entity_detection": entity_detection,
            "auto_chapters": auto_chapters,
            "auto_highlights": auto_highlights,
        }
        estimated_cost = estimate_cost(transcript.audio_duration, features)
        print(f"Estimated cost: ${estimated_cost:.4f}")

    # Format and save output
    output_text = format_output(transcript, format, speaker_labels)

    if show_progress:
        print(f"Saving to {outpath}")

    with open(outpath, "w") as f:
        f.write(output_text)


@app.command()
def list() -> None:
    """List all transcripts"""
    result = aai.Transcriber().list_transcripts()
    for transcript in result.transcripts:
        print(transcript.id, transcript.status)


@app.command()
def load(
    transcript_id: t.Annotated[
        str,
        typer.Argument(help="Transcript ID or negative integer index from `aait list`"),
    ],
) -> None:
    """Load a transcript by ID or index from `aait list`"""
    if transcript_id.startswith("-") and transcript_id[1:].isdigit():
        index = int(transcript_id[1:])
        transcript_id = aai.Transcriber().list_transcripts().transcripts[index].id
    transcript = aai.Transcript.get_by_id(transcript_id)
    code.interact(local=locals(), banner=f"Loaded transcript {transcript_id}")


@app.command()
def delete(
    transcript_id: t.Annotated[
        str,
        typer.Argument(help="Transcript ID or negative integer index from `aait list`"),
    ],
    force: t.Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Delete a transcript from AssemblyAI servers"""
    if transcript_id.startswith("-") and transcript_id[1:].isdigit():
        index = int(transcript_id[1:])
        transcript_id = aai.Transcriber().list_transcripts().transcripts[index].id

    if not force:
        confirm = typer.confirm(f"Delete transcript {transcript_id}?")
        if not confirm:
            print("Cancelled")
            return

    try:
        aai.Transcript.delete_by_id(transcript_id)
        print(f"✓ Deleted transcript {transcript_id}")
    except Exception as e:
        print(f"Error deleting transcript: {e}", file=sys.stderr)
        raise typer.Exit(1)


def version_callback(value: bool) -> None:
    if value:
        try:
            pkg_version = version("assemblyai-tool")
        except PackageNotFoundError:
            pkg_version = "unknown"
        print(f"aait {pkg_version}")
        raise typer.Exit()


@app.callback()
def callback(
    version_flag: t.Annotated[
        t.Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """CLI tool for AssemblyAI"""
    try:
        aai.settings.api_key = load_api_key()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        raise typer.Exit(1)
