import sys
import random
import csv
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QRadioButton, QGroupBox,
    QSlider, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QLineEdit
)
from PyQt5.QtCore import QTimer, Qt, QTime
from PyQt5.QtGui import QIntValidator  # 꼭 import 추가

# 시나리오, SACRI, NASA-TLX 질문 구성
COMMON_OPTIONS = [
    "냉각 펌프 2번 수동 재시작", "냉각수 주입 밸브 A-14 수동 개방", "냉각계통 점검 없이 무시",
    "센서 점검 생략 후 무시", "자동 제어 중단 후 온도 480도 유지 수동 제어",
    "수동 냉각라인 개방 및 알람 기록", "보조 전력 모듈 2 사용 및 압력 120기압 유지",
    "출력 80%로 감압 운전", "수동 냉각계통 전환 및 누설량 분석", "비상 누설경보 무시",
    "제어봉 수동 삽입 후 출력 70% 유지", "모든 로그 자동 기록 후 수동 제어 전환",
    "주입 시스템 밸브 자동 닫기 및 온도 450도 유지", "방사선 차폐 강화",
    "모든 알람 무시 후 출력 유지", "냉각탱크 수위 센서 교체", "수동 제어 시스템 전환",
    "모든 제어봉 자동 복귀", "기록 생략 후 재가동", "작업자 대피 후 재점검"
]

scenarios = [
    {
        "alarm": "🚨 고압력 + 냉각수 부족 감지!",
        "options": COMMON_OPTIONS,
        "correct": 1
    },
    {
        "alarm": "⚠️ 센서 오류 + 급격한 온도 상승!",
        "options": COMMON_OPTIONS,
        "correct": 2
    },
    {
        "alarm": "🔥 방사선 수치 급상승 + 누설 경고 발생!",
        "options": COMMON_OPTIONS,
        "correct": 13  # 방사선 차폐 강화
    },
    {
        "alarm": "⚡ 외부 전력망 불안정 감지 → 비상 전원 전환 필요!",
        "options": COMMON_OPTIONS,
        "correct": 6  # 보조 전력 모듈 2 사용
    },
    {
        "alarm": "⚠️ 제어봉 작동 지연 발생!",
        "options": COMMON_OPTIONS,
        "correct": 10  # 제어봉 수동 삽입
    },
    {
        "alarm": "🔥 냉각탱크 수위 급격히 감소!",
        "options": COMMON_OPTIONS,
        "correct": 15  # 냉각탱크 수위 센서 교체
    },
    {
        "alarm": "🚨 출력 급상승 + 내부 온도 600도 초과!",
        "options": COMMON_OPTIONS,
        "correct": 4  # 온도 480도 수동 제어
    },
    {
        "alarm": "⚠️ 자동 제어 시스템 전체 다운 감지!",
        "options": COMMON_OPTIONS,
        "correct": 16  # 수동 제어 시스템 전환
    },
    {
        "alarm": "🚨 경보 시스템 다중 오류 → 알람 신뢰 불가!",
        "options": COMMON_OPTIONS,
        "correct": 19  # 기록 생략 후 재가동
    },
    {
        "alarm": "⚠️ 압력 완화 밸브 B-4 고착 → 압력 상승 지속!",
        "options": COMMON_OPTIONS,
        "correct": 8  # 수동 냉각계통 전환 및 누설량 분석

    }
]

sacri_questions = [
    ("압력과 온도 동시 상승 시 최우선 대응은?",
     ["압력 120기압 이하로 유지", "온도 500도 이하로 조절", "센서 전원 차단"],
     0),

    ("냉각수가 부족할 때 주의할 점은?",
     ["히터 정상 유지", "출력 그대로 유지", "주입 시스템 이상 여부 확인"],
     2),

    ("제어봉 작동 지연이 발생하면 우선적으로 해야 할 행동은?",
     ["출력 그대로 유지", "제어봉 수동 삽입", "제어봉 로그 삭제"],
     1),

    ("방사선 수치가 급상승했을 때 가장 적절한 대응은?",
     ["작업자 즉시 대피", "출력 증가", "센서 기록 중지"],
     0),

    ("센서 오류 발생 후 무작위 경보가 나타날 경우 조치는?",
     ["센서 리셋 후 상태 확인", "알람 무시", "출력 100% 유지"],
     0),

    ("자동 제어 시스템이 다운될 경우 적절한 조치는?",
     ["자동 재부팅 대기", "수동 제어로 전환", "출력 그대로 유지"],
     1)
]


nasa_tlx_questions = [
    "정신적으로 얼마나 힘들었나요?",
    "신체적으로 얼마나 힘들었나요?",
    "시간 압박을 얼마나 느꼈나요?",
    "얼마나 노력했나요?",
    "얼마나 좌절감을 느꼈나요?",
    "본인 성과에 얼마나 만족하나요?"
]

class SimulatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("원전 통합 제어실 시뮬레이터")
        self.resize(1200, 800)

        self.grid_layout = QGridLayout()
        self.room_labels = {}
        self.room_buttons = {}
        for i in range(4):
            room_id = i + 1
            btn = QPushButton(f"Room {room_id}\n(정상)")
            btn.setEnabled(False)
            btn.setFixedSize(300, 150)
            btn.clicked.connect(lambda checked, r=room_id: self.handle_room_click(r))
            self.room_labels[room_id] = btn
            self.grid_layout.addWidget(btn, i // 2, i % 2)

        self.status_label = QLabel("")
        self.start_button = QPushButton("Start Experiment")
        self.start_button.clicked.connect(self.start_experiment)

        layout = QVBoxLayout()
        layout.addLayout(self.grid_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        self.setLayout(layout)

        self.alarm_index = 0
        self.current_room = None
        self.scenario_sequence = []
        self.results = []
        self.room_assignments = []
        self.sacri_score = 0
        self.tlx_scores = []
        self.alarm_times = []         # 알림 뜬 시각
        self.reaction_times = []      # 알림 누른 시각


    def start_experiment(self):
        self.status_label.setText("🔹 실험이 시작되었습니다. 알람을 대기 중입니다...")
        self.scenario_sequence = random.sample(scenarios, len(scenarios))
        self.wait_and_trigger_alarm()

    def wait_and_trigger_alarm(self):
        delay = random.randint(5000, 20000)  # 알람까지 대기 시간 늘림
        QTimer.singleShot(delay, self.trigger_alarm)


    def trigger_alarm(self):
        if self.alarm_index >= len(self.scenario_sequence):
            self.run_sacri()
            return

        room = random.choice([1, 2, 3, 4])
        self.current_room = room
        sc = self.scenario_sequence[self.alarm_index]
        self.room_assignments.append(room)
        self.alarm_times.append(datetime.now().strftime("%H:%M:%S.%f")[:-3])  # 밀리초까지


        btn = self.room_labels[room]
        btn.setText(f"Room {room}\n⚠️ 문제 발생!")
        btn.setEnabled(True)
        btn.setStyleSheet("background-color: #ffe6e6; font-weight: bold;")

    def handle_room_click(self, room):
        if room != self.current_room:
            return

        self.reaction_times.append(datetime.now().strftime("%H:%M:%S.%f")[:-3])

        sc = self.scenario_sequence[self.alarm_index]
        dialog = QDialog(self)
        dialog.setWindowTitle(f"[Room {room}] 시나리오 {self.alarm_index + 1}")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"[Room {room}] {sc['alarm']}"))

        group = QGroupBox("정확한 조치 선택")
        group_layout = QVBoxLayout()
        buttons = []
        for i, opt in enumerate(sc["options"]):
            btn = QRadioButton(f"{i + 1}) {opt}")
            group_layout.addWidget(btn)
            buttons.append(btn)
        group.setLayout(group_layout)
        layout.addWidget(group)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        result = False
        reaction_time = 0.0
        t_start = QTime.currentTime()
        button_box.accepted.connect(dialog.accept)
        if dialog.exec_() == QDialog.Accepted:
            for idx, btn in enumerate(buttons):
                if btn.isChecked():
                    t_end = QTime.currentTime()
                    msec = t_start.msecsTo(t_end)
                    reaction_time = round(msec / 1000.0, 2)
                    result = (idx == sc["correct"])
                    break

        self.results.append((result, reaction_time))

        btn = self.room_labels[room]
        btn.setText(f"Room {room}\n(정상)")
        btn.setEnabled(False)
        btn.setStyleSheet("")

        self.alarm_index += 1
        self.wait_and_trigger_alarm()

    def run_sacri(self):
        for question, options, correct in sacri_questions:
            dialog = QDialog(self)
            dialog.setWindowTitle("SACRI 퀴즈")
            layout = QVBoxLayout()
            layout.addWidget(QLabel(question))
            buttons = []
            for i, opt in enumerate(options):
                btn = QRadioButton(f"{i + 1}) {opt}")
                layout.addWidget(btn)
                buttons.append(btn)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            layout.addWidget(button_box)
            dialog.setLayout(layout)
            button_box.accepted.connect(dialog.accept)
            if dialog.exec_() == QDialog.Accepted:
                for idx, btn in enumerate(buttons):
                    if btn.isChecked() and idx == correct:
                        self.sacri_score += 1
        self.run_nasa_tlx()

    def run_nasa_tlx(self):
        for q in nasa_tlx_questions:
            dialog = QDialog(self)
            dialog.setWindowTitle("NASA-TLX 설문")
            layout = QFormLayout()
            layout.addRow(QLabel(q))

            # 점수 입력 필드로 변경
            score_input = QLineEdit()
            score_input.setValidator(QIntValidator(0, 100))  # 0~100 숫자만 허용
            score_input.setPlaceholderText("0 ~ 100 사이 숫자를 입력하세요")
            layout.addRow("점수:", score_input)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            layout.addWidget(button_box)
            dialog.setLayout(layout)

            def on_accept():
                text = score_input.text()
                if not text.strip():
                    QMessageBox.warning(self, "입력 필요", "점수를 입력해야 다음으로 넘어갈 수 있습니다.")
                    return  # 입력 안 했으면 그냥 리턴 (창 안 닫힘)
                try:
                    score = int(text)
                    if 0 <= score <= 100:
                        self.tlx_scores.append(score)
                        dialog.accept()  # OK 처리
                    else:
                        QMessageBox.warning(self, "입력 오류", "0에서 100 사이의 숫자를 입력하세요.")
                except ValueError:
                    QMessageBox.warning(self, "입력 오류", "숫자를 입력해야 합니다.")

            button_box.accepted.connect(on_accept)
            dialog.exec_()



        # 설문 완료 후 결과 저장 호출!
        self.show_results()

    def show_results(self):
        score = sum(1 for correct, _ in self.results if correct)
        avg_time = round(sum(t for _, t in self.results) / max(1, len(self.results)), 2)
        avg_tlx = round(sum(self.tlx_scores) / len(self.tlx_scores), 2) if self.tlx_scores else 0
        self.status_label.setText("✅ 실험 종료. 결과를 확인하세요.")
        QMessageBox.information(self, "결과 요약",
            f"✔️ 정답 수: {score}/{len(self.scenario_sequence)}\n"
            f"⏱️ 평균 반응 시간: {avg_time} 초\n"
            f"🧠 SACRI 점수: {self.sacri_score}/{len(sacri_questions)}\n"
            f"📊 NASA-TLX 평균 점수: {avg_tlx}/100")
        self.save_results(score, avg_time, avg_tlx)

    def save_results(self, score, avg_time, avg_tlx):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"log/simulation_log_{timestamp}.csv"
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["시나리오#", "Room#", "정답 여부", "응답 시간", "알림 뜬 시각", "알림 누른 시각"])
                for i, ((correct, t), room, alarm_time, click_time) in enumerate(
                    zip(self.results, self.room_assignments, self.alarm_times, self.reaction_times)):
                    writer.writerow([i + 1, room, "정답" if correct else "오답", t, alarm_time, click_time])
                writer.writerow([])
                writer.writerow(["SACRI 점수", self.sacri_score])
                writer.writerow(["NASA-TLX 평균", avg_tlx])
                writer.writerow(["정답 수", score])
                writer.writerow(["평균 반응 시간", avg_time])
        except Exception as e:
            QMessageBox.critical(self, "CSV 저장 오류", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SimulatorApp()
    win.show()
    sys.exit(app.exec_())
