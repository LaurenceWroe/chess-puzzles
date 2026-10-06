# Replication assumptions and limits

**Stockfish audit update:** Stockfish 19 is now installed locally and used for
an independent depth-18/depth-22 audit. It does not change the benchmark answer
key or either model run's grades. All additional engine-audit assumptions are
documented in [STOCKFISH.md](STOCKFISH.md); earlier notes saying Stockfish was not
installed describe the original setup.

This is a reproduction of the published task and the original 100-item dataset,
not a promise to reproduce a model's historical score. The following are every
material assumption, adaptation, and unresolved detail identified during setup.

**Requested rerun update:** The user selected GPT-5 with Gemini 3.1 Flash-Lite
as grader and authorized the OpenRouter credential in `FORTRESS/.env`.
`run_gpt5.py` uses `openrouter/openai/gpt-5`: OpenRouter's catalog reports its
canonical slug as `openai/gpt-5-2025-08-07`. The dated slug is not itself listed
as a callable model ID, so we rely on that published mapping (saved in
`reference/openrouter-models.json`). The grader is
`openrouter/google/gemini-3.1-flash-lite`, stable rather than preview, with
provider-default settings beyond `max_retries=8`. OpenRouter chat completions
and routing replace Epoch's direct OpenAI Responses API and direct Google API.
That transport and routing difference is additional to the requested grading
change. Solver routing requires support for the requested parameters; no
alternative model fallback is configured. The OpenAI SDK is pinned to 2.8.1
after the newer SDK failed a live preflight due to incompatible HTTP timeout
types with historical Inspect. The grader's live tool-call preflight passed.
Board diagrams show historical data and are never included in solver prompts.
The initial OpenRouter attempt used its adapter's default 10 concurrent samples
and was interrupted after approximately 3m21s with zero completed samples.
Its cancelled log is retained; provider-side charges for interrupted requests
are unknown. The full rerun explicitly permits 100 concurrent samples, matching
the near-simultaneous start timestamps of all 100 reference samples.
The current runner retains Inspect's default `fail_on_error=True`, while the
reference log recorded false. This affects whether execution stops on a sample
error, not grading of successfully completed samples; final reporting must
check that all 100 samples completed without errors.
Final outcome: all 100 samples completed without errors, and all solver stop
reasons were normal (`stop`). The score was 33/100 (standard error 0.04726).
The completed live log and its per-sample inputs, targets, no-tool solver calls,
and high-reasoning request parameters were checked against the original dataset.
The earlier numbered notes describe the initial setup; their statements about
unspecified models and no live calls are superseded by this completed-run update.

1. **Directory interpretation.** `/Chess/` means a `Chess` subdirectory of the
   shared workspace, not a new directory at the filesystem root.

2. **Dataset authority and version.** The gist omits `puzzles.csv`. We use the
   exact inputs, targets, IDs, and ordering from the 100-sample GPT-5 log linked
   in Epoch's methodology, dated 2025-12-08 and marked benchmark version 1.0.0.
   We assume this linked run represents the published benchmark. We have not
   verified that every point on Epoch's evolving graph uses the same dataset.
   CSV serialization is ours; the FEN and answer values are copied unchanged.
   We do not claim the reconstructed CSV is byte-identical to Epoch's missing CSV.

3. **Extractor identification.** The gist's internal `bench.model.default_grader_model`
   implementation is not supplied. Every extraction event in the linked run
   names `google/gemini-2.0-flash-001`, with `max_retries=8`. This is our historical
   default. We replace the missing helper with Inspect's public `get_model` using
   that identifier/configuration. Unlogged internal helper behavior is unknown.

4. **Extractor retirement.** Google's release notes state that Gemini 2.0 Flash
   models shut down on 2026-06-01. A fresh run through that API must use another
   available extractor. The user must select it explicitly; it is recorded in
   task arguments and metadata. A replacement may extract different answers,
   so its score is not an exact historical grading replication. No regex
   extractor, answer normalization, or alternate-move credit is substituted.

5. **Solver and generation configuration.** No target model was specified at
   setup. We provide a selectable solver rather than assuming which model the
   user wants to measure. The linked reference used `openai/gpt-5-2025-08-07`,
   `reasoning_effort=high`, and `max_retries=8`; its recorded request did not set
   a temperature, seed, or output-token cap. Those omissions defer to provider
   defaults. These are facts about this run, not settings we assume for all
   other models. `run.sh` forwards explicit settings and adds none of its own.

6. **Runtime versions.** Inspect is pinned to reference version 0.3.146. The
   original Python, SDK, and transitive dependency versions are not in the
   reference header. We use local system Python 3.11.4 and lock the dependencies
   that install and pass offline checks here. They are not asserted to be the
   historical dependency set. Provider implementations/defaults may differ.
   The machine's Anaconda Python 3.12.2 crashed importing `readline`, hence the
   explicit system-Python choice.
   `cryptography` is pinned to 46.0.5 because the newer release attempted a Rust
   build without the required target on this machine.

7. **Prompts, scoring, and aggregation.** Both prompts are preserved verbatim
   from the gist, including trailing whitespace. The solver sees only the FEN
   prompt and has no tools. A separate model must submit the extracted answer
   through `submit`. Comparison is case-sensitive exact string equality;
   an explicit null is `NOANSWER`, and a malformed extraction raises an error,
   following the gist. The historical log contains an empty extractor response
   followed by another extraction event on sample 26; we preserve Inspect's
   behavior rather than inventing a new local retry/fallback scorer. The task
   defaults to one epoch, the mean reducer, accuracy, and Inspect standard error.
   Limits, extra epochs, and token caps supplied by a user must be disclosed.

8. **Promotion notation.** The prompt requests four characters; UCI promotions
   normally need five. We preserve the published prompt and exact targets
   instead of silently changing this convention. Any future/custom dataset
   containing promotions needs this limitation considered separately.

9. **Puzzle generation is not rerun.** Reusing the actual 100 items removes the
   need to guess Stockfish version, random seed, hardware, or UCI defaults.
   Those original generation details are not published in the supplied code.
   A new `--chaos` generation run would use the same algorithm, not reproduce
   the original positions. Its time-limited searches also prevent a Python
   random seed alone from guaranteeing identical output. Stockfish is not
   installed because evaluation of the recovered fixed dataset does not use it.

10. **Code is authoritative for generator edge cases.** If generating new
    puzzles later, retain the gist's thresholds and exceptions, rather than
    substituting a literal reading of the prose: its game-length cap, analysis
    start point, capture-value margin, and checkmate exception matter. Engine
    strength limits must support the sampled Elo values. There is no claim that
    another engine/version would choose the same best moves. We validate target
    legality but do not rejudge or replace Epoch's answer key using another engine.

11. **Local adaptations.** The CSV path is relative to `chess_eval.py` rather
    than Epoch's private repository structure. Model selection is configurable;
    dataset hash and grading deviations are added to log metadata. The upstream
    `inspect-log-public` marker is set to false. These changes do not change
    puzzle content or scoring. No logs are uploaded by the setup.
    The launcher also places diagnostic trace output under local `logs/`.
    Inspect itself uses its standard macOS application-data directory for
    temporary log buffering; running the CLI in a restricted sandbox may
    require permission to write there.

12. **Validation versus a live benchmark.** Offline validation compares all
    inputs/targets with the source log and reproduces its 37/100 from recorded
    extractor submissions. Mock integration tests validate plumbing only.
    No real solver or grader request has been made, so credentials, endpoint
    access, and provider behavior remain unverified. Historical model snapshots
    may no longer be available; stochastic API outputs and service changes can
    change results even when configuration is held constant.

Evidence is retained in `reference/`. Primary sources:
[methodology](https://epoch.ai/benchmarks/chess-puzzles?view=graph&tab=release-date),
[gist](https://gist.github.com/greg-burnham/fc1c6f9ed32989073f58321b656b7b05),
[reference run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/6DcmBdRZz57U5cusZNBeGW.eval),
[Google retirement notice](https://ai.google.dev/gemini-api/docs/changelog).
