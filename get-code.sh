#!/bin/bash

[ -d code ] && { echo "code/ already exists" ; exit 1; }

set -e

mkdir code
cd code

git clone git@github.com:encode/httpx.git
git clone git@github.com:AssemblyAI/assemblyai-python-sdk.git
