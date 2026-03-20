#!/usr/bin/env python3
"""Update RST changelog files with new release entries.

This script is called by the GitLab CI pipeline to add changelog entries
to the aimms-how-to documentation repository.

Required environment variables:
    RST_FILE: Path to the RST file to update
    TAG: Version tag (e.g., "1.0.0")
    TODAY: Date string (e.g., "20/03/2026")
    COMMIT_LINE: Changelog description text
    GITHUB_RELEASE_URL: URL to the GitHub release download
"""

import os
import sys
from pathlib import Path


def main():
    # Read required environment variables
    required_vars = ["RST_FILE", "TAG", "TODAY", "COMMIT_LINE", "GITHUB_RELEASE_URL"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    rst_file = Path(os.environ["RST_FILE"])
    tag = os.environ["TAG"]
    today = os.environ["TODAY"]
    commit_line = os.environ["COMMIT_LINE"] or "No significant changes"
    url = os.environ["GITHUB_RELEASE_URL"]

    # Validate RST file exists
    if not rst_file.exists():
        print(f"ERROR: RST file not found: {rst_file}", file=sys.stderr)
        sys.exit(1)

    # Create new changelog entry
    new_entry = f"`v{tag} <{url}>`_ ({today})\n   {commit_line}.\n"

    # Read file content
    content = rst_file.read_text()
    lines = content.splitlines(keepends=True)

    # Find insertion point (after "Release Notes" section header)
    insert_pos = -1
    found_release_notes = False

    for i, line in enumerate(lines):
        if line.strip() == "Release Notes":
            found_release_notes = True
        if found_release_notes and "----" in line:
            insert_pos = i + 1
            break

    if insert_pos == -1:
        print("ERROR: 'Release Notes' section not found in RST file", file=sys.stderr)
        sys.exit(1)

    # Insert new entry
    lines.insert(insert_pos, "\n" + new_entry)

    # Write updated content
    rst_file.write_text("".join(lines))
    print(f"RST updated successfully: {rst_file}")
    print(f"Added entry for v{tag}")


if __name__ == "__main__":
    main()
