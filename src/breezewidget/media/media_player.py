"""MediaPlayer — thin QMediaPlayer wrapper with paired QAudioOutput.

Wraps Qt's media stack so callers don't have to remember to attach an
audio output before playback.  Adds a ``hasMedia()`` helper and
forwards :meth:`setSource` / :meth:`play` / :meth:`pause` /
:meth:`stop` / :meth:`setPosition` / :meth:`setVolume`.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class MediaPlayer(QObject):
    """Audio/video player with built-in audio output."""

    sourceChanged = Signal(QUrl)
    positionChanged = Signal(int)  # ms
    durationChanged = Signal(int)  # ms
    playbackStateChanged = Signal(QMediaPlayer.PlaybackState)
    volumeChanged = Signal(float)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)

        # Forward through lambdas — `connect(self.signal)` rejects qint64
        # signals because PySide cannot reconcile the argument types
        # against `Signal(int)`.
        self._player.sourceChanged.connect(lambda url: self.sourceChanged.emit(url))
        self._player.positionChanged.connect(lambda ms: self.positionChanged.emit(int(ms)))
        self._player.durationChanged.connect(lambda ms: self.durationChanged.emit(int(ms)))
        self._player.playbackStateChanged.connect(
            lambda state: self.playbackStateChanged.emit(state)
        )
        self._audio.volumeChanged.connect(lambda v: self.volumeChanged.emit(float(v)))

    # --- forwarding API -------------------------------------------------

    def player(self) -> QMediaPlayer:
        """Return the wrapped :class:`QMediaPlayer` for advanced wiring."""
        return self._player

    def audioOutput(self) -> QAudioOutput:
        return self._audio

    def setSource(self, url: QUrl | str) -> None:
        self._player.setSource(QUrl(url) if isinstance(url, str) else url)

    def source(self) -> QUrl:
        return self._player.source()

    def hasMedia(self) -> bool:
        return not self._player.source().isEmpty()

    def play(self) -> None:
        self._player.play()

    def pause(self) -> None:
        self._player.pause()

    def stop(self) -> None:
        self._player.stop()

    def togglePlay(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()

    def position(self) -> int:
        return self._player.position()

    def setPosition(self, ms: int) -> None:
        self._player.setPosition(int(ms))

    def duration(self) -> int:
        return self._player.duration()

    def volume(self) -> float:
        return self._audio.volume()

    def setVolume(self, value: float) -> None:
        self._audio.setVolume(max(0.0, min(1.0, value)))

    def isMuted(self) -> bool:
        return self._audio.isMuted()

    def setMuted(self, muted: bool) -> None:
        self._audio.setMuted(muted)

    def playbackState(self) -> QMediaPlayer.PlaybackState:
        return self._player.playbackState()
