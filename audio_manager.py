"""Safe audio manager for Stone Age Survival.

The manager loads sounds lazily so importing the module does not require
an active audio device. Missing files or mixer failures are handled
gracefully and do not crash the game.
"""

from __future__ import annotations

from pathlib import Path

import pygame


AUDIO_DIR = Path(__file__).resolve().parent / "assets" / "audio"

SFX_FILES = {
    "click": "click1.WAV",
    "click1": "click1.WAV",
    "chop": "chop.WAV",
    "fire": "fire.WAV",
    "wolf_howl": "wolf_howl.WAV",
}

# Reserved for future BGM files.
MUSIC_FILES: dict[str, str] = {}


class AudioManager:
    def __init__(
        self,
        sfx_volume: float = 0.65,
        music_volume: float = 0.45,
    ) -> None:
        self.sfx_volume = self._clamp_volume(sfx_volume)
        self.music_volume = self._clamp_volume(music_volume)
        self.enabled = True
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._mixer_failed = False

    @staticmethod
    def _clamp_volume(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _ensure_mixer(self) -> bool:
        if not self.enabled or self._mixer_failed:
            return False

        if pygame.mixer.get_init():
            return True

        try:
            pygame.mixer.init()
            return True
        except pygame.error:
            self._mixer_failed = True
            return False

    def _get_sound(self, name: str) -> pygame.mixer.Sound | None:
        if name in self._sounds:
            return self._sounds[name]

        filename = SFX_FILES.get(name)

        if filename is None:
            return None

        path = AUDIO_DIR / filename

        if not path.is_file():
            return None

        if not self._ensure_mixer():
            return None

        try:
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(self.sfx_volume)
        except (pygame.error, OSError):
            return None

        self._sounds[name] = sound
        return sound

    def play_sfx(self, name: str, loops: int = 0) -> bool:
        """Play one sound effect.

        loops=0 plays once.
        loops=-1 loops forever, which is useful for the fire ambience.
        """
        sound = self._get_sound(name)

        if sound is None:
            return False

        try:
            sound.play(loops=loops)
            return True
        except pygame.error:
            return False

    def stop_sfx(self, name: str) -> None:
        sound = self._sounds.get(name)

        if sound is not None:
            sound.stop()

    def play_music(self, name: str, loops: int = -1) -> bool:
        """Play a future BGM track by name.

        MUSIC_FILES is currently empty because no BGM files have been added.
        """
        filename = MUSIC_FILES.get(name)

        if filename is None:
            return False

        path = AUDIO_DIR / filename

        if not path.is_file() or not self._ensure_mixer():
            return False

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=loops)
            return True
        except (pygame.error, OSError):
            return False

    def stop_music(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def set_sfx_volume(self, value: float) -> None:
        self.sfx_volume = self._clamp_volume(value)

        for sound in self._sounds.values():
            sound.set_volume(self.sfx_volume)

    def set_music_volume(self, value: float) -> None:
        self.music_volume = self._clamp_volume(value)

        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.music_volume)

    def stop_all(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.music.stop()


audio = AudioManager()