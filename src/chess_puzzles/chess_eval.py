from pathlib import Path
import hashlib

from inspect_ai import Task, task, Epochs
from inspect_ai.dataset import Sample, csv_dataset
from inspect_ai.scorer import (
    scorer,
    Score,
    Target,
    CORRECT,
    INCORRECT,
    NOANSWER,
    accuracy,
    stderr,
)
from inspect_ai.solver import generate, prompt_template, TaskState
from inspect_ai.tool import ToolDef, ToolFunction

from inspect_ai.model import GenerateConfig, get_model

ROOT = Path(__file__).resolve().parent
HISTORICAL_GRADER = "google/gemini-2.0-flash-001"

SOLUTION_PROMPT_TEMPLATE = """Below is a FEN string representing the state of a chess game. Please analyze the position and determine the best next move for the player whose turn it is. You may think as much as you would like, but please conclude your response with the move expressed as a four-character string stating the starting and ending square of the piece to be moved, using the format "MOVE: b1c3" (without quotes).

{prompt}

"""

EXTRACTION_PROMPT_TEMPLATE = """**Task: Extract a student's answer to a single-move chess puzzle and submit the move that is their final answer.**

Instructions:
- Read the student's entire solution carefully to identify their final answer.
- The student is supposed to have concluded their solution with "MOVE: [answer]" where [answer] is given as a four-character string stating the starting and ending square of the piece to be moved, e.g. b1c3.
- If the solution appears in that format, extract the move and submit it as the final answer.
- Otherwise, do your best to identify the final answer.
- Use the tool provided to submit the extracted answer.
- If there are multiple moves in the solution, extract the one that represents the main answer to the puzzle.
- If no clear final answer can be identified, submit `None` instead.

Solution to extract from:

<student_solution>

{student_solution}

</student_solution>"""


@scorer(metrics=[accuracy(), stderr()])
def model_extracted_exact_match(grader_model: str = HISTORICAL_GRADER):
    async def score(state: TaskState, target: Target) -> Score:
        student_solution = state.output.completion

        extraction_prompt = EXTRACTION_PROMPT_TEMPLATE.format(student_solution=student_solution)

        def submit(answer: str | None):
            pass

        submission_tool = ToolDef(
            tool=submit,
            name="submit",
            description="Submit the answer",
            parameters={"answer": "The answer"},
        )
        extraction_output = await get_model(grader_model, config=GenerateConfig(max_retries=8)).generate(
            extraction_prompt,
            tools=[submission_tool],
            tool_choice=ToolFunction(name="submit"),
        )

        if (
            not extraction_output.message.tool_calls
            or "answer" not in extraction_output.message.tool_calls[0].arguments
        ):
            raise RuntimeError("Grader model did not correctly extract an answer")

        extracted_answer = extraction_output.message.tool_calls[0].arguments["answer"]

        if extracted_answer is None:
            return Score(
                value=NOANSWER,
                explanation="No clear answer was given",
            )

        is_correct = extracted_answer == target.text
        explanation = (
            f"The model answered {extracted_answer}, which is correct."
            if is_correct
            else f"The model answered {extracted_answer}, but the correct answer is {target.text}."
        )

        return Score(
            value=CORRECT if is_correct else INCORRECT,
            answer=str(extracted_answer),
            explanation=explanation,
        )

    return score


@task(name="Chess Puzzles")
def chess_puzzles(
    epochs: int = 1,
    grader_model: str = HISTORICAL_GRADER,
    dataset_path: str = "",
) -> Task:
    if epochs < 1:
        raise ValueError("epochs must be positive")
    path = Path(dataset_path).resolve() if dataset_path else ROOT / "data/puzzles.csv"
    dataset = csv_dataset(str(path))

    plan = [prompt_template(SOLUTION_PROMPT_TEMPLATE), generate()]

    reducers = ["mean"]

    return Task(
        dataset=dataset,
        plan=plan,
        scorer=model_extracted_exact_match(grader_model),
        epochs=Epochs(epochs, reducers),
        metadata={
            "epochai-benchmark-version": "1.0.0",
            "inspect-log-public": False,
            "dataset-sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "dataset-source": "Epoch public GPT-5 log" if not dataset_path else str(path),
            "extractor-model": grader_model,
            "extractor-changed-from-reference": grader_model != HISTORICAL_GRADER,
            "replication-note": "See ASSUMPTIONS.md; no tools provided to solver",
        },
    )