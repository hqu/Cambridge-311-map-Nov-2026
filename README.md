# Cambridge 311 Map, Nov 2026

An interactive map of the 1,127 service requests that were still open in Cambridge, MA on 9 November 2026. The requests come from Commonwealth Connect, the city's SeeClickFix-based 311 system.

Open `index.html` to use the map:

- **Date filter.** Use the preset buttons (last 7, 30 or 90 days, 2026, all time), pick start and end dates, or drag across the monthly bar chart. Tickets outside the range stay on the map as faint dots.
- **Categories.** The 146 issue types are sorted into seven groups (bike, parks, streets and sidewalks, traffic and parking, trash and rodents, noise and construction, other). You can turn each group on or off.
- **Tickets.** Hover over a dot to see its type, date, address and photo. Click a dot to see the full ticket in the side panel, with a link to it on SeeClickFix.

The photos load from `photos.json`, which browsers won't fetch from a page opened straight from disk (`file://`). To see them locally, serve the folder:

```bash
python -m http.server 8000
```

Then open http://localhost:8000. GitHub Pages serves the page with its photos as is.

## Files

| Path | What it is |
|---|---|
| `index.html` | The map. The ticket data, streets and neighborhoods are embedded in it. |
| `photos.json` | Thumbnails (260 × 195 px at most) of 741 ticket photos, stored as data URIs. |
| `data/Commonwealth_Connect_Service_Requests_-_Open_Tickets_20261109.csv` | The source export of open tickets. |
| `data/gis/` | Street centerlines and neighborhood boundaries from [City of Cambridge GIS](https://github.com/cambridgegis/cambridgegis_data). |
| `scripts/template.html` | The page source, before data is embedded. |
| `scripts/build.py` | Builds `index.html` from the CSV, the GIS layers and the template. |
| `scripts/thumbnails.py` | Downloads the ticket photos and writes `photos.json`. Needs Pillow. |

To rebuild after editing the template or the data:

```bash
python scripts/build.py
```

## Notes on the data

- Categories come from keyword matching on issue-type names, so a few unusual types may be in the wrong group. The rules are at the top of `scripts/build.py`.
- 12 tickets list a photo that SeeClickFix no longer serves; the map says so for those tickets.
- 36 tickets have a closed date but are still marked open, probably because they were reopened.
- Descriptions and photos were submitted by residents and are shown as published by SeeClickFix.

## Sources

- Ticket data: Commonwealth Connect service requests, open tickets, exported 9 Nov 2026.
- Photos: SeeClickFix, linked from each ticket.
- Streets and neighborhoods: City of Cambridge GIS, [cambridgegis/cambridgegis_data](https://github.com/cambridgegis/cambridgegis_data).
