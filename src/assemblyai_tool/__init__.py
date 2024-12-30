from pathlib import Path
import typing as t
import typer
import dotenv
import assemblyai as aai
import os
import sys
import code

app = typer.Typer()


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


def make_transcript(
    inpath: str, speaker_labels: bool, language_detection: bool
) -> aai.Transcript:
    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.best,
        speaker_labels=speaker_labels,
        language_detection=language_detection,
    )
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(str(inpath))
    return transcript


@app.command()
def convert(
    inpath: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=False)
    ],
    outpath: t.Annotated[
        Path, typer.Argument(exists=False, dir_okay=False)
    ],
    speaker_labels: t.Annotated[
        bool, typer.Option(help="Include speaker labels")
    ] = True,
    language_detection: t.Annotated[
        bool, typer.Option(help="Include language detection")
    ] = True,
) -> None:
    """Convert a media file to a text file with speaker labels"""
    print("Uploading and transcribing", inpath)
    transcript = make_transcript(inpath, speaker_labels, language_detection)
    print("Saving to", outpath)
    with open(outpath, "w") as f:
        for utterance in transcript.utterances:
            if speaker_labels:
                f.write(f"Speaker {utterance.speaker}: {utterance.text}\n\n")
            else:
                f.write(utterance.text + "\n\n")


@app.command()
def list() -> None:
    """List all transcripts"""
    for transcript in aai.Transcriber().list_transcripts():
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


@app.callback()
def callback() -> None:
    """CLI tool for AssemblyAI"""
    try:
        aai.settings.api_key = load_api_key()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        raise typer.Exit(1)
