# Forgeloop for Codex

Forgeloop is distributed here as a Codex-only skill pack. There are no plugin manifests, marketplace hooks, or secondary platform adapters left in this repository.

## Install

```bash
git clone https://github.com/jiumem/forgeloop.git ~/.codex/forgeloop
bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop
```

If you're already inside a checkout of this repository, `bash scripts/install.sh --yes` is enough.

## How Discovery Works

Codex loads skills from `~/.codex/skills/`. This repository exposes its bundled skills through:

```text
~/.codex/skills/forgeloop -> ~/.codex/forgeloop/skills
```

That keeps the working copy updateable with `git pull` while making the skills visible to Codex.

## Updating

```bash
cd ~/.codex/forgeloop && git pull
bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop
```

## Uninstalling

```bash
rm ~/.codex/skills/forgeloop
rm -rf ~/.codex/forgeloop
```

## Troubleshooting

If the skills do not show up:

1. Check the symlink: `ls -la ~/.codex/skills/forgeloop`
2. Run the installer in doctor mode: `bash ~/.codex/forgeloop/scripts/install.sh --doctor --source ~/.codex/forgeloop`
3. Check skill files exist: `find ~/.codex/skills/forgeloop -maxdepth 2 -name SKILL.md`
4. Restart Codex
