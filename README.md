# file-organizer

Sort files into category folders by extension.

## Usage

```bash
python3 -c "from organizer import *; print(organize('.'))"
```

## Features

- Dry-run planning of file moves
- Move files into Images, Documents, Audio, Video, Archives, Other
- Custom rules with load_mapping(path)

## Tests

```bash
python3 -m unittest -q
```

## License

MIT
