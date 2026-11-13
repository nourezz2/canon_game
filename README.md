# Cannon Game · Python & Kivy

A first-year university game project using Python and Kivy. Aim a cannon, launch a projectile, and intercept moving enemies while tracking score and level.

## Features

- Projectile motion with gravity and aiming controls
- Moving enemies and rectangle-based collision detection
- Score tracking and increasing levels
- Sound effects, help panel, and basic save/load controls

## Run locally

Use Python 3 and a graphical desktop. Run from the repository directory so the audio files can be found.

```bash
python -m pip install -r requirements.txt
python cano.py
```

| Control | Action |
| --- | --- |
| Left / Right arrows | Adjust aim before firing |
| Space | Fire |
| Help | Show instructions |
| Save / Load | Store or restore score, level, and game-over flag |
| reset | Reset score and level and clear enemies |

## Files

- [cano.py](cano.py): game implementation
- `missile.WAV`, `pop.wav`, `bullet.wav`: bundled audio assets
- `savegame.json`: basic saved state

## Known limitations

Save/load does not restore enemy positions or the projectile state. Reset/load after game over needs further work because the canvas is cleared when the game ends. Keyboard scan codes and audio support may differ by platform.
