"""Run ``physicalai fit`` without loading the robot CLI, which imports POSIX-only ``fcntl``.

The ``physicalai`` console script imports every subcommand host, including ``physicalai.cli.robot``, whose
transport lock uses ``fcntl`` and fails on Windows. This launcher builds only the ``fit`` parser from
``physicalai.cli.fit`` (the same parser and dispatch the console script uses) and runs it. Use it in the Studio
backend environment with the ``config.json`` written by ``defect_sorter.training run``::

	uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen \
		python scripts/offline_pipeline/fit_without_robot_cli.py --config artifacts/training/<run>/config.json
"""

import sys

from physicalai.cli.fit import build_parser, run


def main(argv: list[str] | None = None) -> int:
	"""Parse ``fit`` arguments and dispatch to ``Trainer.fit``."""
	parser = build_parser()
	return run(parser, parser.parse_args(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
	raise SystemExit(main())
