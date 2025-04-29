#!/bin/bash

# This script runs the lt_extract pipeline and passes any extra parameters to it

python -m factue.pipelines.lt_extract \
  --split dev \
  --lang eng \
  --part 0000 \
  --max-iterations 3 \
  --seed -1 \
  --force
  "$@"