import argparse
import json
import logging
import sys

from src.logging_config import configure_logging
from src.mentor import MentorError, evaluate_idea

logger = logging.getLogger(__name__)


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(
        description="Evaluate a startup idea and print structured feedback as JSON."
    )
    parser.add_argument("--idea", required=True, help="Path to a text file containing the startup idea.")
    args = parser.parse_args()

    try:
        with open(args.idea, "r", encoding="utf-8") as f:
            idea_text = f.read()
    except OSError as exc:
        logger.error("Could not read idea file %s: %s", args.idea, exc)
        return 1

    try:
        feedback = evaluate_idea(idea_text)
    except MentorError as exc:
        logger.error("evaluate_idea failed: %s", exc)
        return 1

    print(json.dumps(feedback.model_dump(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
