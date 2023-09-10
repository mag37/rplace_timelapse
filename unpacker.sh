#!/usr/bin/env bash
# Should be run from within the same directory as the images[2-5].tar
for file in *tar
do
  dir=$(basename "$file" .tar)
  mkdir "$dir"
  tar -xvf "$file" -C "$dir"
done
