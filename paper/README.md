# commensurability-paper

This directory contains the JOSS paper for the commensurability package.

## Contents

All of the text is in this directory, with figures in the subdirectory `figures`.  Contents are:

| File      | Description |
| ---       | ---         |
| paper.md  | The primary markdown text file |
| paper.bib | The bibliography file |
| paper.pdf | The compiled PDF file |


## Compile to PDF with Docker as follows

```
docker run --rm --volume $PWD/paper:/data --user $(id -u):$(id -g) --env JOURNAL=joss openjournals/inara
```
