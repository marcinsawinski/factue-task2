#!/bin/bash

# This script runs the lt_extract pipeline and passes any extra parameters to it

python -m factue.pipelines.lt_llm_process \
  --split dev \
  --max-iterations 5 \
  --seed -1 \
  "$@"