# Generic Web Scraper

Config-driven scraper for arbitrary websites. Add new targets by writing YAML configs—no code changes required.

## Quick Start

```bash
# From project root
pip install -r generic_scraper/requirements.txt
python -m generic_scraper.run --all
# Output: generic_master.csv

# Or run specific targets
python -m generic_scraper.run generic_scraper/targets/cmu.yaml generic_scraper/targets/example_quotes.yaml -o out.csv
```

## Architecture

### Schema

All extractors produce `Record` objects with:

| Field | Required | Description |
|-------|----------|-------------|
| source | ✓ | Target id (e.g. oxford, cmu) |
| name | ✓ | Primary identifier (person name, etc.) |
| url | | Profile/page URL |
| email | | Contact email |
| raw | | Source-specific key-value data |

Output CSV: `source`, `name`, `url`, `email` + `{source}_{key}` for each raw field.

### Source Types

| Type | Use Case | Config Keys |
|------|----------|-------------|
| `html_listing` | Listing page → item links → detail pages | `listing.url`, `listing.link_selector`, `detail.extract` |
| `json_api` | Single JSON endpoint | `api.url`, `api.data_path`, `field_mapping`, `transforms` |
| `html_attrs` | Page with `data-*` attributes | `url`, `container_selector`, `attribute_map`, `transforms` |
| `css_select` | Arbitrary HTML with repeating structure | `url`, `item_selector`, `field_selectors`, `field_attributes` |

### Adding a New Target

1. Create `targets/my_site.yaml`
2. Choose source type by data shape:
   - JSON API? → `json_api`
   - `data-mail`, `data-name` etc.? → `html_attrs`
   - Listing → detail pages? → `html_listing`
   - Generic list/table? → `css_select`
3. Fill config (see examples in `targets/`)
4. Run: `python -m generic_scraper.run targets/my_site.yaml -o out.csv`

### Example: Generic CSS Select (Any Site)

```yaml
id: my_site
base_url: https://example.com
source_type: css_select

url: https://example.com/people
item_selector: .person-card

field_selectors:
  name: .name
  email: .email
  bio: .bio
  profile_url: a.profile

field_attributes:
  profile_url: href

link_fields:
  - profile_url
```

Change `url`, `item_selector`, and `field_selectors` to target a different site.

## Existing Targets

- **oxford** – OATML members (html_listing)
- **cmu** – PhD students via JSON (json_api)
- **iitm** – CSE faculty via data attrs (html_attrs)
- **quotes** – quotes.toscrape.com demo (css_select)

## Design Notes

- **Schema-first**: All sources normalize to `Record`; CSV columns are derived at runtime.
- **Config over code**: New targets = new YAML; extractors are reusable.
- **Transforms**: Built-in (`deobfuscate_email`, `andrew_email`, `list_join`, `absolute_url`) handle common cases; extend in extractor classes for more.
- **Raw preservation**: Source-specific data kept in raw; no premature normalization.
