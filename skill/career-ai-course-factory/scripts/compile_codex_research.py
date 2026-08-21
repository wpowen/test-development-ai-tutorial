#!/usr/bin/env python3
"""CLI compatibility wrapper for compiling Codex research traces."""

import sys

from codex_research_contract import main


if __name__ == "__main__":
    sys.argv.insert(1, "compile")
    raise SystemExit(main())
