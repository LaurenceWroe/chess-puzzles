# Chess Puzzles — a reproduction

An independent reproduction of the *Chess Puzzles* benchmark published by
[Epoch AI](https://epoch.ai/benchmarks/chess-puzzles), packaged as an
[Inspect AI](https://inspect.aisi.org.uk) task so it can be run, re-graded and
audited (for example with [inspect_audit](https://github.com/Generality-Labs/inspect_audit)).
It is not affiliated with or endorsed by Epoch AI.

The benchmark gives a model a chess position as a FEN string and asks for the best
move. An extractor model reads the final answer out of the response, and the task
is scored by exact match against the reference move.

## What is reproduced, and from where

- **Task and prompts**: `src/chess_puzzles/chess_eval.py`. The solution and extraction
  prompts are verbatim from the generator and task code Epoch published in a
  [public gist](https://gist.github.com/greg-burnham/fc1c6f9ed32989073f58321b656b7b05);
  scoring is model-extracted exact match, as there.
- **Dataset**: `src/chess_puzzles/data/puzzles.csv`, the 100 FEN/answer pairs
  recovered from the public GPT-5 evaluation log Epoch links (benchmark version 1.0.0;
  sha256 `b4dad44b…`). The gist omits the CSV, so this file is reconstructed, not copied.
- **Generator**: `upstream/puzzle_generator.py`, Epoch's puzzle generator from the same
  gist, kept for reference. It is not run; the published 100 items are used as-is.
- **Assumptions**: `ASSUMPTIONS.md` lists every adaptation, unresolved detail and
  deviation from the original setup.

## Differences from the original

- The historical extractor, `google/gemini-2.0-flash-001`, is retired. Pass a live
  extractor with `-T grader_model=...`; the task records which one was used.
- The task registers as `chess_puzzles/Chess Puzzles`, keeping the display name the
  original logs record so attempts can be joined across runs.

## Run

```sh
pip install git+https://github.com/LaurenceWroe/chess-puzzles
inspect eval "chess_puzzles/Chess Puzzles" --model openrouter/openai/gpt-5 \
  -T grader_model=openrouter/google/gemini-3.1-flash-lite --reasoning-effort high
```
