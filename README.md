# file-organizer

Sort files into category folders by extension.

## Usage

```bash
python3 -c "from organizer import *; print(organize('.'))"
python3 -c "from organizer import *; moves=organize('.', dry_run=False); print(undo_moves(moves, '.'))"
python3 -c "from organizer import *; print(find_duplicates('.'))"
python3 -c "from organizer import *; print(largest_files('.'))"
python3 -c "from organizer import *; print(total_size('.'))"
```

## Features

- Dry-run planning of file moves
- Move files into Images, Documents, Audio, Video, Archives, Other
- Undo a run with undo_moves(moves, directory)
- Custom rules with load_mapping(path)
- Find identical files with find_duplicates(directory)
- Rank biggest files with largest_files(directory, limit=10)
- Sum top-level file sizes with total_size(directory)

## Tests

```bash
python3 -m unittest -q
```

## Additional API

- `category_summary(directory)` counts files and total bytes per category.

## License

MIT
