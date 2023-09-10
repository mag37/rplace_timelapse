#!/usr/bin/env bash
for file in *tar
do
  dir=$(basename "$file" .tar)
  mkdir "$dir"
  tar -xvf "$file" -C "$dir"
done
