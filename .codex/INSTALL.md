# Installing Forgeloop for Codex

Forgeloop now targets Codex only. Installation is just a repository clone plus a Codex skills symlink.

## Prerequisites

- Git

## Install

Preferred path:

1. Clone the repository:
   ```bash
   git clone https://github.com/jiumem/forgeloop.git ~/.codex/forgeloop
   ```

2. Run the installer:
   ```bash
   bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop
   ```

3. Restart Codex.

## Manual fallback

If the installer fails, do the link step directly:

```bash
mkdir -p ~/.codex/skills
ln -sfn ~/.codex/forgeloop/skills ~/.codex/skills/forgeloop
```

## Verify

```bash
bash ~/.codex/forgeloop/scripts/install.sh --doctor --source ~/.codex/forgeloop
find ~/.codex/skills/forgeloop -maxdepth 2 -name SKILL.md
```

You should see the symlink plus the packaged skill directories.

## Update

```bash
cd ~/.codex/forgeloop && git pull
```

The symlink keeps Codex pointed at the current checkout.

## Uninstall

```bash
rm ~/.codex/skills/forgeloop
rm -rf ~/.codex/forgeloop
```
