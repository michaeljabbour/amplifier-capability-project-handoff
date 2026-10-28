# HANDOFF

## Project Overview
This project is an offline list reader that currently uses CSV files as its data source. The decision has been made to retain the CSV format to maintain compatibility with existing workflows.

## Current Status
- The reader continues to use CSV files; no migration to a database will be performed.
- The next development task is to implement support for parsing quoted commas within CSV entries.
- Testing for the quoted-comma parser case is still pending.

## Next Steps
- Implement the quoted-comma parser case to handle CSV entries with commas inside quotes correctly.
- Develop and run tests to verify the new parser functionality.

## Notes
- Avoid switching to a database as it conflicts with the current compatibility requirements.
- Keep the CSV format as the primary data source.

Please refer to PROJECT.md for additional project context.