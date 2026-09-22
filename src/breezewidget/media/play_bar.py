"""PlayBar — transport controls (play/pause, slider, time, volume) for MediaPlayer."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget

from ..constants import PROP_PLAY_BAR
from ..icons import BreezeIcon
from ..icons._themed import ThemedIcon
from ..widgets.slider import ClickableSlider
from .media_player import MediaPlayer


def _format_ms(ms: int) -> str:
    """Format milliseconds as ``M:SS`` (or ``H:MM:SS`` for ≥1 h)."""
    if ms < 0:
        ms = 0
    seconds = ms // 1000
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class PlayBar(QWidget):
    """Transport controls bound to a :class:`MediaPlayer`.

    The bar shows: play/pause toggle, position slider with current and
    total time, mute toggle, and a volume slider.  Slider drags update
    the player's position; player position changes update the slider.
    Click :attr:`playButton`, :attr:`muteButton`, or drag
    :attr:`positionSlider` / :attr:`volumeSlider` to interact.
    """

    def __init__(
        self,
        media_player: MediaPlayer | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty(PROP_PLAY_BAR, True)
        self._player: MediaPlayer | None = None
        self._user_seeking = False

        self.playButton = QToolButton(self)
        self.playButton.setAutoRaise(True)
        self._playIcon = ThemedIcon(self.playButton.setIcon)
        self._playIcon.set(BreezeIcon.NEXT)
        self.playButton.clicked.connect(self._onPlayClicked)

        self.positionLabel = QLabel("0:00", self)
        self.durationLabel = QLabel("0:00", self)

        self.positionSlider = ClickableSlider(Qt.Orientation.Horizontal, self)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderPressed.connect(self._onSeekStart)
        self.positionSlider.sliderReleased.connect(self._onSeekEnd)
        self.positionSlider.valueChanged.connect(self._onPositionDragged)

        self.muteButton = QToolButton(self)
        self.muteButton.setAutoRaise(True)
        self.muteButton.setCheckable(True)
        self._muteIcon = ThemedIcon(self.muteButton.setIcon)
        self._muteIcon.set(BreezeIcon.INFO)  # placeholder; toggled below
        self.muteButton.toggled.connect(self._onMuteToggled)

        self.volumeSlider = ClickableSlider(Qt.Orientation.Horizontal, self)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setFixedWidth(100)
        self.volumeSlider.valueChanged.connect(self._onVolumeChanged)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        layout.addWidget(self.playButton)
        layout.addWidget(self.positionLabel)
        layout.addWidget(self.positionSlider, 1)
        layout.addWidget(self.durationLabel)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)

        if media_player is not None:
            self.setMediaPlayer(media_player)

    def refreshTheme(self) -> None:
        self._refreshPlayIcon()
        self._muteIcon.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setMediaPlayer(self, media_player: MediaPlayer) -> None:
        if self._player is not None:
            self._disconnect_player(self._player)
        self._player = media_player
        media_player.positionChanged.connect(self._onPlayerPositionChanged)
        media_player.durationChanged.connect(self._onPlayerDurationChanged)
        media_player.playbackStateChanged.connect(self._onPlayerStateChanged)
        media_player.volumeChanged.connect(self._onPlayerVolumeChanged)
        self.volumeSlider.setValue(int(media_player.volume() * 100))
        self._refreshPlayIcon()

    def mediaPlayer(self) -> MediaPlayer | None:
        return self._player

    # ------------------------------------------------------------------
    # Player → UI
    # ------------------------------------------------------------------

    def _onPlayerPositionChanged(self, ms: int) -> None:
        if self._user_seeking:
            return
        self.positionSlider.blockSignals(True)
        self.positionSlider.setValue(ms)
        self.positionSlider.blockSignals(False)
        self.positionLabel.setText(_format_ms(ms))

    def _onPlayerDurationChanged(self, ms: int) -> None:
        self.positionSlider.setRange(0, max(0, ms))
        self.durationLabel.setText(_format_ms(ms))

    def _onPlayerStateChanged(self, _state) -> None:
        self._refreshPlayIcon()

    def _onPlayerVolumeChanged(self, volume: float) -> None:
        self.volumeSlider.blockSignals(True)
        self.volumeSlider.setValue(int(volume * 100))
        self.volumeSlider.blockSignals(False)

    # ------------------------------------------------------------------
    # UI → Player
    # ------------------------------------------------------------------

    def _onPlayClicked(self) -> None:
        if self._player is not None:
            self._player.togglePlay()

    def _onSeekStart(self) -> None:
        self._user_seeking = True

    def _onSeekEnd(self) -> None:
        self._user_seeking = False
        if self._player is not None:
            self._player.setPosition(self.positionSlider.value())

    def _onPositionDragged(self, value: int) -> None:
        if self._user_seeking:
            self.positionLabel.setText(_format_ms(value))

    def _onMuteToggled(self, checked: bool) -> None:
        if self._player is not None:
            self._player.setMuted(checked)

    def _onVolumeChanged(self, value: int) -> None:
        if self._player is not None:
            self._player.setVolume(value / 100.0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refreshPlayIcon(self) -> None:
        playing = self._player is not None and (
            self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        )
        # Reuse the existing icon set: BACK arrow flipped vs forward as
        # a stand-in for pause vs play in clean-room style.  Apps are
        # expected to override the icons with their own pause glyph.
        self._playIcon.set(BreezeIcon.BACK if playing else BreezeIcon.NEXT)

    def _disconnect_player(self, player: MediaPlayer) -> None:
        try:
            player.positionChanged.disconnect(self._onPlayerPositionChanged)
            player.durationChanged.disconnect(self._onPlayerDurationChanged)
            player.playbackStateChanged.disconnect(self._onPlayerStateChanged)
            player.volumeChanged.disconnect(self._onPlayerVolumeChanged)
        except (RuntimeError, TypeError):
            pass
