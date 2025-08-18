# ChessRatingUpdater
Scrapes the web for uscf chess ratings, lichess ratings, and chesskid ratings given a sheet with names and IDs.

## Instructions

- Make copy of `vars-default` to `vars`
- Modify `vars` to update the value for `gsheets_api_key_file`
- Modify 'rss_url' to allow traversal through a chesskid rss
- 'source_sheet' should have a list of 4 columns, for full names, uscf ids, lichess usernames, and chesskid usernames
- 'target_sheet' can be empty outside of the header
- setup a venv by the name of .venv using requirements.txt
