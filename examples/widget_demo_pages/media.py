"""Media (6) - MediaPlayer + PlayBar + VideoWidget."""
from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from breezewidget import BodyLabel, MediaPlayer, PlayBar, PushButton, VideoWidget

from ._gallery import GalleryPage


class MediaDemoPage(GalleryPage):
    """Phase 6 - MediaPlayer + PlayBar + VideoWidget."""

    def __init__(self):
        super().__init__("Media", "breezewidget.media", "media")
        self._player = MediaPlayer(self)

        video_host = QWidget(self)
        video_layout = QVBoxLayout(video_host)
        video_layout.setContentsMargins(0, 0, 0, 0)

        self._videoPlaceholder = QWidget(video_host)
        self._videoPlaceholder.setMinimumHeight(220)
        self._videoPlaceholder.setStyleSheet("background: #000000;")
        self._videoPlaceholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        video_layout.addWidget(self._videoPlaceholder)

        video = VideoWidget(video_host)
        video.setMinimumHeight(220)
        video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        video.hide()
        video_layout.addWidget(video)
        self._player.player().setVideoOutput(video)
        self.addExample("VideoWidget - bound to MediaPlayer's video output", video_host)

        bar = PlayBar(self._player)
        self.addExample("PlayBar - transport controls (play/pause, seek, mute, volume)", bar)

        load_row = QWidget()
        load_layout = QHBoxLayout(load_row)
        load_layout.setContentsMargins(0, 0, 0, 0)
        load_button = PushButton("Load file...")
        load_button.clicked.connect(self._loadFile)
        self._sourceLabel = BodyLabel("No source")
        load_layout.addWidget(load_button)
        load_layout.addWidget(self._sourceLabel, 1)
        self._player.sourceChanged.connect(self._onSourceChanged)
        self.addExample("Load - pick an audio/video file via QFileDialog", load_row)

        self.finish()

    def _loadFile(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(self, "Open media")
        if path:
            self._player.setSource(QUrl.fromLocalFile(path))
            self._player.play()

    def _onSourceChanged(self, url: QUrl) -> None:
        has_source = not url.isEmpty()
        self._sourceLabel.setText(url.toString() or "No source")
        self._videoPlaceholder.setVisible(not has_source)
        video = self.findChild(VideoWidget)
        if video is not None:
            video.setVisible(has_source)
