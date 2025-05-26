# ChessRatingUpdater
Scrapes the web for uscf chess ratings, lichess ratings, and chesskid ratings given a sheet with names and IDs.

## Instructions

- Make copy of `vars-default` to `vars`
- Modify `vars` to update the value for `gsheets_api_key_file`
- 'source_sheet' should have a list of 4 columns, for full names, uscf ids, lichess usernames, and chesskid usernames
- 'target_sheet' can be empty outside of the header
