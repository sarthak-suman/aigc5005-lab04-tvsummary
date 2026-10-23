# TV Summary

Summarizes TVMaze shows by genre and calculates average ratings by language.
This refactors the Lab 02 program while preserving its summary keys and calculations.

## Data source
https://api.tvmaze.com/shows?page=0

Each record represents one television show. The Lab 02 run processed 240 shows.

## Setup
```bash
conda env create -f environment.yml
conda activate tvsummary
pip install -r requirements.txt
pip install -e .
```
Run these commands from the repository root.

## Run
```bash
python main.py
```
Output: `data/processed/summary.json`.

## Test
```bash
python -m unittest discover -s tests
```
The tests use handmade records and need no network.

## Layout
- `main.py`: connects downloading, reporting and friendly error messages.
- `config.py`: keeps the source URL, timeout and relative output path together.
- `models.py`: cleans one show's values when constructing a Show.
- `sources.py`: downloads and validates data; the only module importing requests.
- `aggregations.py`: holds a shared calculation interface and its two subclasses.
- `report.py`: builds and writes the JSON summary.
- `__init__.py`: re-exports the public names for direct imports.
- `tests/test_models.py`: checks cleaning and calculations without network access.

## What moved where
| Lab 02 function | New location |
| --- | --- |
| fetch_records | TVMazeSource.fetch and TVMazeSource._download in sources.py |
| valid_genres | Show.__init__ in models.py |
| shows_per_genre | ShowsPerGenre.compute in aggregations.py |
| average_rating_by_language | Cleaning in Show.__init__; calculation in AverageRatingByLanguage.compute |
| build_summary | report.build_summary |
| write_summary | report.write_summary |
| main | main.main |

## Design choices
Show represents one record and centralizes cleaning so both calculations use the
same valid values. Its __str__ returns a readable show name. TVMazeSource has one
job: return cleaned shows or raise DownloadError.

Aggregation provides a summary key and an abstract compute interface.
ShowsPerGenre and AverageRatingByLanguage override compute. The report builder
loops over mixed aggregation objects and calls compute without checking their types.
To add a calculation, subclass Aggregation, supply a key, implement compute and
add an instance to the report builder's list.

## Known limitations
Only page 0 is fetched. Live ratings can change, so a fresh output may differ from
the supplied Lab 02 summary. The committed output was regenerated successfully with this package.
The program needs internet access and rejects responses with fewer than 50 records.
Run from the repository root because the output path is relative to that folder.

## Before submission
Clone into another folder, follow Setup, Run and Test, then disconnect Wi-Fi and
run again. A failed download should print a message without a traceback.
Submit the GitHub repository URL on Blackboard and ensure the instructor has access.
