# Epoch Chess Puzzles — Inspect task

A pip-installable reproduction of Epoch AI's
[Chess Puzzles](https://epoch.ai/benchmarks/chess-puzzles) benchmark as an
[Inspect AI](https://inspect.aisi.org.uk) task, for auditing with
[inspect_audit](https://github.com/Generality-Labs/inspect_audit).

- `src/epoch_chess_puzzles/chess_eval.py` — the task. Prompts are verbatim from Epoch's
  [public gist](https://gist.github.com/greg-burnham/fc1c6f9ed32989073f58321b656b7b05);
  the scorer is a model-extracted exact match, as in the gist.
- `src/epoch_chess_puzzles/data/puzzles.csv` — the 100 FEN/answer pairs, recovered from the
  public GPT-5 log Epoch links (benchmark version 1.0.0; sha256 `b4dad44b…`).
- `upstream/puzzle_generator.py` — Epoch's puzzle generator, copied from the gist for reference.
- `ASSUMPTIONS.md` — every adaptation and unresolved detail of the reproduction.

The task registers as `epoch_chess_puzzles/Chess Puzzles` (the display name Epoch's logs record).

```sh
pip install git+https://github.com/LaurenceWroe/epoch-chess-puzzles
inspect eval "epoch_chess_puzzles/Chess Puzzles" --model openrouter/openai/gpt-5 \
  -T grader_model=openrouter/google/gemini-3.1-flash-lite --reasoning-effort high
```

`grader_model` defaults to Epoch's historical extractor `google/gemini-2.0-flash-001`,
which is retired; pass a live extractor explicitly.
