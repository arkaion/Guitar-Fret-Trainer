from __future__ import annotations

import random
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QComboBox, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QRadioButton, QSpinBox, QStackedWidget,
    QVBoxLayout, QWidget,
)


FRET_COUNT = 15
FRET_MARKERS = (3, 5, 7, 9, 12)
STRINGS = ("E", "A", "D", "G", "B", "E")
OPEN_PITCHES = {"E": 4, "A": 9}
PITCH_NAMES = (
    ("E",), ("F",), ("F#", "Gb"), ("G",), ("G#", "Ab"), ("A",),
    ("A#", "Bb"), ("B",), ("C",), ("C#", "Db"), ("D",), ("D#", "Eb"),
)


@dataclass(frozen=True)
class Exercise:
    key: str
    title: str
    root_string: str
    root_fret: int
    kind: str
    chord_type: str | None = None


class ResultStore:
    def __init__(self) -> None:
        self.connection = sqlite3.connect(Path(__file__).with_name("results.sqlite3"))
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY, exercise_key TEXT NOT NULL, correct INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"""
        )
        self.connection.commit()

    def record(self, exercise: Exercise, correct: bool) -> None:
        self.connection.execute(
            "INSERT INTO attempts(exercise_key, correct) VALUES (?, ?)",
            (exercise.key, int(correct)),
        )
        self.connection.commit()

    def weight(self, exercise: Exercise) -> float:
        total, incorrect = self.connection.execute(
            "SELECT COUNT(*), COALESCE(SUM(CASE WHEN correct = 0 THEN 1 ELSE 0 END), 0) "
            "FROM attempts WHERE exercise_key = ?", (exercise.key,)
        ).fetchone()
        return 1 + (incorrect / total * 4 if total else 0)


class Fretboard(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(580, 650)
        self.exercise: Exercise | None = None
        self.revealed = False
        self.marker_style = "numbers"
        self.setStyleSheet("background: #090b0d;")

    def set_exercise(self, exercise: Exercise, revealed: bool, marker_style="numbers") -> None:
        self.exercise = exercise
        self.revealed = revealed
        self.marker_style = marker_style
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#090b0d"))
        left, top, width, height = 88, 82, self.width() - 132, self.height() - 125
        string_gap = width / 5
        fret_gap = height / FRET_COUNT
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        painter.setPen(QColor("#e9edf0"))
        for index, name in enumerate(STRINGS):
            x = left + index * string_gap
            painter.drawText(int(x - 5), 45, name)
        for fret in range(FRET_COUNT + 1):
            y = top + fret * fret_gap
            painter.setPen(QPen(QColor("#6d747c"), 2 if fret == 0 else 1))
            painter.drawLine(left - 17, int(y), left + width + 17, int(y))
            if self.marker_style == "numbers" and fret in FRET_MARKERS:
                painter.setPen(QColor("#b5bdc5"))
                painter.drawText(38, int(y - fret_gap / 2 + 5), str(fret))
            elif self.marker_style == "dots" and fret in FRET_MARKERS:
                marker_y = y - fret_gap / 2
                painter.setBrush(QColor("#b5bdc5"))
                painter.setPen(Qt.PenStyle.NoPen)
                if fret == 12:
                    painter.drawEllipse(32, int(marker_y - 10), 12, 12)
                    painter.drawEllipse(48, int(marker_y - 10), 12, 12)
                else:
                    painter.drawEllipse(38, int(marker_y - 6), 12, 12)
        for index in range(6):
            x = left + index * string_gap
            painter.setPen(QPen(QColor("#eef2f4"), 2 + (5 - index) // 2))
            painter.drawLine(int(x), top, int(x), top + height)
        if self.exercise and self.revealed:
            if self.exercise.kind == "note":
                self._draw_note(painter, left, top, width, height, string_gap, fret_gap)
            else:
                self._draw_chord(painter, left, top, width, height, string_gap, fret_gap)

    def _dot(self, painter, x: float, y: float, label: str, color="#f0f3f5") -> None:
        painter.setBrush(QColor(color))
        painter.setPen(QPen(QColor("#090b0d"), 2))
        painter.drawEllipse(int(x - 18), int(y - 18), 36, 36)
        painter.setPen(QColor("#090b0d"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(int(x - 4), int(y + 5), label)

    def _draw_note(self, painter, left, top, width, height, string_gap, fret_gap) -> None:
        assert self.exercise
        string_index = 0 if self.exercise.root_string == "E" else 1
        x = left + string_index * string_gap
        if self.exercise.root_fret == 0:
            painter.setPen(QPen(QColor("#60d7ff"), 8))
            painter.drawLine(int(x), top, int(x), top + height)
            return
        y = top + (self.exercise.root_fret - 0.5) * fret_gap
        self._dot(painter, x, y, "R", "#60d7ff")

    def _draw_chord(self, painter, left, top, width, height, string_gap, fret_gap) -> None:
        assert self.exercise
        root = self.exercise.root_fret
        positions, fingers = chord_shape(self.exercise.root_string, self.exercise.chord_type or "M")
        start = 0 if self.exercise.root_string == "E" else 1
        if root > 0:
            first, last = (0, 5) if start == 0 else (1, 5)
            y = top + (root - 0.5) * fret_gap
            painter.setPen(QPen(QColor("#60d7ff"), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(left + first * string_gap), int(y), int(left + last * string_gap), int(y))
        for string_index, offset in enumerate(positions):
            if offset is None or (root > 0 and offset == 0):
                continue
            fret = root + offset
            if not 0 <= fret <= FRET_COUNT:
                continue
            x = left + string_index * string_gap
            y = top + (fret - 0.5) * fret_gap
            self._dot(painter, x, y, str(fingers[string_index]))


def chord_shape(root_string: str, chord_type: str) -> tuple[tuple[int | None, ...], tuple[int, ...]]:
    e_shapes = {
        "M": ((0, 2, 2, 1, 0, 0), (1, 3, 4, 2, 1, 1)),
        "7": ((0, 2, 0, 1, 0, 0), (1, 3, 1, 2, 1, 1)),
        "m": ((0, 2, 2, 0, 0, 0), (1, 3, 4, 1, 1, 1)),
        "m7": ((0, 2, 0, 0, 0, 0), (1, 3, 1, 1, 1, 1)),
        "sus4": ((0, 2, 2, 2, 0, 0), (1, 3, 4, 2, 1, 1)),
    }
    a_shapes = {
        "M": ((None, 0, 2, 2, 2, 0), (0, 1, 2, 3, 4, 1)),
        "7": ((None, 0, 2, 0, 2, 0), (0, 1, 3, 1, 4, 1)),
        "m": ((None, 0, 2, 2, 1, 0), (0, 1, 3, 4, 2, 1)),
        "m7": ((None, 0, 2, 0, 1, 0), (0, 1, 3, 1, 2, 1)),
        "sus4": ((None, 0, 2, 2, 3, 0), (0, 1, 2, 3, 4, 1)),
    }
    return (e_shapes if root_string == "E" else a_shapes)[chord_type]


class SetupPage(QWidget):
    def __init__(self, start_session) -> None:
        super().__init__()
        self.start_session = start_session
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 55, 80, 55)
        layout.setSpacing(18)
        title = QLabel("Guitar Fret Trainer")
        title.setObjectName("title")
        subtitle = QLabel("Retrouve les notes et les formes d'accords sur le manche.")
        subtitle.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.content = self._combo("Exercice", ["Notes", "Accords"])
        self.string = self._combo("Corde de fondamentale", ["Mi grave", "La", "Mi grave et La"])
        self.accidentals = self._combo("Notes", ["Naturelles et alterations", "Naturelles uniquement"])
        self.fret_markers = self._combo("Reperes de frettes", ["Numeros (3, 5, 7, 9, 12)", "Points de manche"])
        self.timing = self._combo("Revelation", ["Avec delai", "A l'appui d'une touche"])
        self.seconds = QSpinBox()
        self.seconds.setRange(1, 30)
        self.seconds.setValue(5)
        self.seconds.setSuffix(" secondes")
        layout.addWidget(self._row("Temps de reflexion", self.seconds))
        self.timing.currentIndexChanged.connect(lambda: self.seconds.setEnabled(self.timing.currentIndex() == 0))
        layout.addStretch()
        start = QPushButton("Commencer la session")
        start.setObjectName("primary")
        start.clicked.connect(self._start)
        layout.addWidget(start)

    def _combo(self, label: str, items: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.addItems(items)
        self.layout().addWidget(self._row(label, combo))
        return combo

    def _row(self, label: str, widget: QWidget) -> QWidget:
        row = QFrame()
        row.setObjectName("setting")
        layout = QHBoxLayout(row)
        layout.addWidget(QLabel(label))
        layout.addStretch()
        layout.addWidget(widget)
        return row

    def _start(self) -> None:
        self.start_session({
            "kind": "note" if self.content.currentIndex() == 0 else "chord",
            "strings": ("E",) if self.string.currentIndex() == 0 else ("A",) if self.string.currentIndex() == 1 else ("E", "A"),
            "accidentals": self.accidentals.currentIndex() == 0,
            "timed": self.timing.currentIndex() == 0,
            "seconds": self.seconds.value(),
            "marker_style": "numbers" if self.fret_markers.currentIndex() == 0 else "dots",
        })


class TrainingPage(QWidget):
    def __init__(self, store: ResultStore, leave_session) -> None:
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.store, self.leave_session = store, leave_session
        self.settings: dict = {}
        self.current: Exercise | None = None
        self.last_key: str | None = None
        self.phase = "question"
        self.remaining = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        top = QHBoxLayout()
        self.question = QLabel()
        self.question.setObjectName("question")
        self.timer_label = QLabel()
        self.timer_label.setObjectName("timer")
        exit_button = QPushButton("Quitter")
        exit_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        exit_button.clicked.connect(self.leave_session)
        top.addWidget(self.question)
        top.addStretch()
        top.addWidget(self.timer_label)
        top.addWidget(exit_button)
        layout.addLayout(top)
        self.board = Fretboard()
        layout.addWidget(self.board, 1)
        self.hint = QLabel()
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setObjectName("muted")
        layout.addWidget(self.hint)
        answers = QHBoxLayout()
        answers.addStretch()
        self.correct = QPushButton("Juste  [V]")
        self.correct.setObjectName("correct")
        self.correct.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.correct.clicked.connect(lambda: self.answer(True))
        self.wrong = QPushButton("Faux  [F]")
        self.wrong.setObjectName("wrong")
        self.wrong.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.wrong.clicked.connect(lambda: self.answer(False))
        answers.addWidget(self.correct)
        answers.addWidget(self.wrong)
        answers.addStretch()
        layout.addLayout(answers)

    def begin(self, settings: dict) -> None:
        self.settings = settings
        self.next_question()

    def next_question(self) -> None:
        self.timer.stop()
        self.phase = "question"
        self.current = self._choose_exercise()
        self.board.set_exercise(self.current, False, self.settings["marker_style"])
        self.correct.hide()
        self.wrong.hide()
        root_name = "Mi grave" if self.current.root_string == "E" else "La"
        self.question.setText(f"{self.current.title}  |  Corde de {root_name}")
        self.hint.setText("Observe la question, puis attends la revelation.")
        self._wait()

    def _choose_exercise(self) -> Exercise:
        options = []
        for root_string in self.settings["strings"]:
            if self.settings["kind"] == "note":
                for fret in range(FRET_COUNT + 1):
                    pitch = (OPEN_PITCHES[root_string] + fret) % 12
                    if not self.settings["accidentals"] and len(PITCH_NAMES[pitch]) > 1:
                        continue
                    title = random.choice(PITCH_NAMES[pitch])
                    options.append(Exercise(f"note:{root_string}:{fret}", title, root_string, fret, "note"))
            else:
                for fret in range(0, 13):
                    pitch = (OPEN_PITCHES[root_string] + fret) % 12
                    for chord_type, suffix in (("M", ""), ("7", "7"), ("m", "m"), ("m7", "m7"), ("sus4", "4")):
                        options.append(Exercise(f"chord:{root_string}:{fret}:{chord_type}", random.choice(PITCH_NAMES[pitch]) + suffix, root_string, fret, "chord", chord_type))
        candidates = [item for item in options if item.key != self.last_key] or options
        selected = random.choices(candidates, weights=[self.store.weight(item) for item in candidates], k=1)[0]
        self.last_key = selected.key
        return selected

    def _wait(self) -> None:
        if self.settings["timed"]:
            self.remaining = self.settings["seconds"]
            self.timer_label.setText(f"{self.remaining}s")
            self.timer.start(1000)
        else:
            self.timer_label.setText("Appuie sur une touche")

    def _tick(self) -> None:
        self.remaining -= 1
        self.timer_label.setText(f"{self.remaining}s")
        if self.remaining <= 0:
            self.timer.stop()
            if self.phase == "question":
                self.reveal()
            else:
                self.next_question()

    def reveal(self) -> None:
        self.phase = "answer"
        self.board.set_exercise(self.current, True, self.settings["marker_style"])
        self.timer_label.setText("")
        self.hint.setText("Avais-tu trouve ?")
        self.correct.show()
        self.wrong.show()

    def answer(self, correct: bool) -> None:
        if self.phase != "answer" or not self.current:
            return
        self.store.record(self.current, correct)
        self.next_question()

    def keyPressEvent(self, event) -> None:
        if self.phase == "answer" and event.key() in (Qt.Key.Key_V, Qt.Key.Key_F):
            self.answer(event.key() == Qt.Key.Key_V)
            return
        if self.phase in ("question", "observation") and not self.settings.get("timed", True):
            if self.phase == "question":
                self.reveal()
            else:
                self.next_question()
            return
        super().keyPressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Guitar Fret Trainer")
        self.resize(920, 820)
        self.store = ResultStore()
        self.pages = QStackedWidget()
        self.setup = SetupPage(self.start_session)
        self.training = TrainingPage(self.store, self.show_setup)
        self.pages.addWidget(self.setup)
        self.pages.addWidget(self.training)
        self.setCentralWidget(self.pages)

    def start_session(self, settings: dict) -> None:
        self.pages.setCurrentWidget(self.training)
        self.training.setFocus()
        self.training.begin(settings)

    def show_setup(self) -> None:
        self.training.timer.stop()
        self.pages.setCurrentWidget(self.setup)


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget { background: #090b0d; color: #eef2f4; font: 15px 'Segoe UI'; }
        QLabel#title { font-size: 32px; font-weight: 700; }
        QLabel#question { font-size: 32px; font-weight: 800; }
        QLabel#timer { font-size: 20px; font-weight: 700; color: #60d7ff; }
        QLabel#muted { color: #aab4bc; }
        QFrame#setting { border: 1px solid #2b333a; border-radius: 6px; padding: 8px; }
        QPushButton, QComboBox, QSpinBox { background: #151a1f; border: 1px solid #3b4650; border-radius: 5px; padding: 8px 14px; }
        QPushButton:hover { border-color: #e9edf0; }
        QPushButton#primary { background: #e9edf0; color: #090b0d; font-weight: 700; padding: 12px; }
        QPushButton#correct { background: #146c43; font-weight: 700; min-width: 150px; }
        QPushButton#wrong { background: #9c2929; font-weight: 700; min-width: 150px; }
        QComboBox QAbstractItemView { background: #151a1f; selection-background-color: #33424e; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()