# Audio Transcription Batch Processor

Create a Python script that processes a directory of audio interview files for transcription. The script should use a transcription service to handle multiple files efficiently while managing bandwidth and improving accuracy with domain-specific vocabulary.

## Context

You have a directory containing podcast interview audio files that need to be transcribed. Each interview discusses technology topics and includes multiple speakers. The transcriptions should be optimized for:

1. **Concurrent processing** - Handle multiple files simultaneously with controlled resource usage
2. **Bandwidth management** - Limit upload speeds to avoid network congestion
3. **Accuracy** - Improve recognition of technical terminology
4. **Speaker identification** - Distinguish between different speakers in the interviews

## Requirements

### Basic Processing

- The script processes all audio files in a specified input directory [@test](../test/test_basic_processing.py)
- The script saves transcription results to a specified output directory [@test](../test/test_output_directory.py)
- The script uses plain text format for output files [@test](../test/test_text_format.py)

### Concurrent Operation

- The script processes files with controlled concurrency: 3 concurrent uploads and 8 concurrent transcription jobs [@test](../test/test_concurrency.py)

### Bandwidth Control

- The script limits upload bandwidth to 60% of the initial measured upload speed [@test](../test/test_bandwidth_ratio.py)

### Accuracy Enhancement

- The script boosts accuracy for the following technical terms: "Kubernetes", "Python", "Docker", "TypeScript" [@test](../test/test_vocabulary_boost.py)
- The script uses high-strength boosting for these vocabulary terms [@test](../test/test_boost_strength.py)

### Speaker Identification

- The script enables speaker labeling to distinguish between different speakers [@test](../test/test_speaker_labels.py)

### File Management

- The script skips files that have already been transcribed to avoid duplicate processing [@test](../test/test_skip_existing.py)

## Implementation

[@generates](./src/batch_transcribe.py)

## API

```python { #api }
"""
Audio transcription batch processor for interview files.

This script processes podcast interview audio files with optimized settings
for concurrent operation, bandwidth management, and technical vocabulary.
"""

import subprocess
import sys
from pathlib import Path

def process_interviews(input_dir: str, output_dir: str) -> None:
    """
    Process all audio interview files in the input directory.

    Args:
        input_dir: Path to directory containing audio files
        output_dir: Path to directory where transcriptions will be saved

    The function configures and executes batch transcription with:
    - 3 concurrent uploads
    - 8 concurrent transcription jobs
    - 60% bandwidth limit (ratio-based on initial upload speed)
    - Technical vocabulary boosting: Kubernetes, Python, Docker, TypeScript
    - High boost strength
    - Speaker label identification
    - Skip existing output files
    - Plain text output format
    """
    pass

def main():
    """Command-line entry point."""
    if len(sys.argv) != 3:
        print("Usage: python batch_transcribe.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    process_interviews(input_dir, output_dir)

if __name__ == "__main__":
    main()
```

## Dependencies { .dependencies }

### assemblyai-tool { .dependency }

Provides CLI tool for batch audio transcription with concurrent processing, rate limiting, and vocabulary customization.
