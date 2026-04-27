# Publish 1.0.0

You need to run:

```bash
bash download.sh
uv run create.py
uv run convert_format.py
uv run add_turns.py
```

Validate the prompts:

```bash
uvx --index https://artifactory.audeering.com/artifactory/api/pypi/pypi/simple iva-prompt-format --num-workers 6 build/json/
```

and publish the data

```bash
uv run publish.py
```
