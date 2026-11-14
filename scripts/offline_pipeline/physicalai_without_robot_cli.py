"""Run ``physicalai fit`` or ``physicalai export`` without loading the robot CLI, which imports POSIX-only ``fcntl``.

The ``physicalai`` console script imports every subcommand host, including ``physicalai.cli.robot``, whose
transport lock uses ``fcntl`` and fails on Windows. This launcher builds only the requested subcommand's parser
(the same parser and dispatch the console script uses) and runs it, in the Studio backend environment::

	uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen \
		python scripts/offline_pipeline/physicalai_without_robot_cli.py fit --config artifacts/training/<run>/config.json
	uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen \
		python scripts/offline_pipeline/physicalai_without_robot_cli.py export --policy physicalai.policies.SmolVLA \
		--ckpt_path artifacts/training/<run>/checkpoints/best.ckpt --backend openvino --output_dir artifacts/export/<run>
"""

import importlib
import sys

SUBCOMMANDS = ("fit", "export")


def main(argv: list[str] | None = None) -> int:
	"""Dispatch ``fit`` or ``export``; the subcommand name comes first, as with the console script."""
	args = sys.argv[1:] if argv is None else argv
	if not args or args[0] not in SUBCOMMANDS:
		sys.stderr.write(f"usage: {sys.argv[0]} {{{','.join(SUBCOMMANDS)}}} [options]\n")
		return 2
	module = importlib.import_module(f"physicalai.cli.{args[0]}")
	parser = module.build_parser()
	return module.run(parser, parser.parse_args(args[1:]))


if __name__ == "__main__":
	raise SystemExit(main())
