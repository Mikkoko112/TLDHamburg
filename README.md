## Data files

Large datasets are excluded from this Git repository because they exceed GitHub's file size limits. They are stored externally on Proton Drive.

**Download the required files:** https://drive.proton.me/urls/WKK7NN0EG0#rYvFKk6F6VIM

After downloading, place each file at the corresponding path below, relative to the repository root:

| File | Required location |
|---|---|
| `hamburg.gml` | `data/hamburg.gml` |
| `hamburg.gml` | `tldhamburg/control/data/hamburg.gml` |
| `shHamburg.gml` | `Control/data/shHamburg.gml` |
| `shHamburg.gml` | `tldhamburg/control/data/shHamburg.gml` |
| `shHamburgCopy.gml` | `tldhamburg/control/data/shHamburgCopy.gml` |
| `observations_all_datastreams.json.gz` | `signal_observations/observations_all_datastreams.json.gz` |

**Important:** The paths above are distinct locations. If the project uses the files at multiple locations, place a copy at each required path. Preserve the exact directory names and capitalization.

The archive `cis-projekt-2024.zip`, if needed, belongs in the repository root. It is not required if you download and place the individual data files instead.

These files are not tracked by Git. The project may not run correctly until all datasets required by the relevant scripts are downloaded and placed in their expected locations.