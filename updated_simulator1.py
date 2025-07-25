# -*- coding: utf-8 -*-
"""Untitled20.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GSMjE0l8K7BkUznB1TH35NKtGqCsKkfh
"""

# -*- coding: utf-8 -*-
"""Revised Multi-SMR Monitoring System with Pump Fault Simulation Scenario

시나리오:
- SMR 운전 중, 자동화 시스템이 냉각계통 순환펌프의 유량 저하 감지
- 1단계: 자동 감지 및 초기 대응 → 순환펌프 유량 급감 (예비 펌프 기동 시도)
- 2단계: 예비 펌프 기동 성공으로 유량 회복 시도, 그러나 온도 상승 지속 → 자동 안전 조치 적용
- 3단계: 자동화 실패 후 고온 경보 발생 및 원자로 출력 자동 80% 저감
- 4단계: 운영자 개입(수동 모드 전환) → 수동 조작(밸브 전환)으로 냉각수 유량 증가
- 5단계: 온도 정상 범위 복구 후 복구 완료 및 실험 종료
"""

import sys
import os
import csv
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QSlider, QProgressBar, QFrame, QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer

# 전역 오류 플래그 (하나의 SMR에서 오류 발생 시 True)
GLOBAL_ERROR_ACTIVE = False

# 로그 파일 경로 (로그 기록은 운영 이벤트에 대해 남김)
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE_PATH = f"logs/{current_time}.log"

def init_log_file():
    if not os.path.exists(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Room", "오류내용", "오류 발생 시각", "대기 시간(초)", "조치 완료 시각"])
        except Exception as e:
            print(f"로그 파일 초기화 실패: {e}")

class SMRWidget(QWidget):
    def start_error_sequence(self):
        if self.error_stage == 0:
            self.current_error_time = datetime.now()
            self.error_stage = 1
            self.selected_scenario = random.choice([
    "밸브 개방 고착",
    "급수 펌프 정지",
    "격납건물 증기 누설",
    "콘덴서 누설",
    "수위 제어 실패"
            ])
            if self.selected_scenario == "밸브 개방 고착":
                self.primary_coolant_slider.setValue(30)
                self.secondary_coolant_slider.setValue(30)
                QMessageBox.information(self, "오류 감지", "냉각수 흐름 감소 감지.\n예비 펌프 기동 시도 중...")
            elif self.selected_scenario == "급수 펌프 정지":
                self.water_level = 85
                self.water_level_bar.setValue(int(self.water_level))
                QMessageBox.information(self, "오류 감지", "급수 펌프 정지 및 수위 저하 감지.\n예비 펌프 가동 시도 중...")
            elif self.selected_scenario == "격납건물 증기 누설":
                self.reactor_temp = 335
                self.lbl_reactor_temp.setText(f"{self.reactor_temp:.1f}")
                QMessageBox.information(self, "오류 감지", "압력·온도 상승 감지.\n스팀 누설 의심 경보 발생.")
            QTimer.singleShot(3000, self.step1_complete)

    def step1_complete(self):
        if self.error_stage == 1:
            if self.selected_scenario == "밸브 개방 고착":
                self.primary_coolant_slider.setValue(70)
                self.secondary_coolant_slider.setValue(70)
                self.reactor_temp = 330
                QMessageBox.information(self, "초기 대응 완료", "예비 펌프 기동 성공: 유량 회복됨.\n그러나 온도는 계속 상승 중...")
            elif self.selected_scenario == "급수 펌프 정지":
                self.water_level = 75
                self.water_level_bar.setValue(int(self.water_level))
                QMessageBox.information(self, "초기 대응 완료", "예비 펌프 가동됨.\n수위는 계속 저하 중...")
            elif self.selected_scenario == "격납건물 증기 누설":
                QMessageBox.information(self, "초기 대응 완료", "누설 감지 지속.\n압력 상승 지속.")
            QTimer.singleShot(5000, self.start_step2)

    def start_step2(self):
        if self.error_stage in [1, 2]:
            self.error_stage = 2
            if self.selected_scenario == "밸브 개방 고착":
                QMessageBox.warning(self, "경보 발생", "고온 경보 발생!\n출력 80% 자동 저감")
            elif self.selected_scenario == "급수 펌프 정지":
                QMessageBox.warning(self, "경보 발생", "수위 저하 알람 발생!\n예비 펌프 성능 저하 감지")
            elif self.selected_scenario == "격납건물 증기 누설":
                QMessageBox.warning(self, "누설 경보", "격납건물 압력 이상 지속\n스팀 밸브 점검 필요")
            self.control_rod_slider.setValue(min(100, self.control_rod_slider.value() + 10))
            QTimer.singleShot(5000, self.start_step3)

    def start_step3(self):
        if self.error_stage == 2:
            self.error_stage = 3
            if self.selected_scenario == "밸브 개방 고착":
                msg = "주·예비 펌프 및 밸브 이상 진단. 복합 냉각 계통 문제."
            elif self.selected_scenario == "급수 펌프 정지":
                msg = "메인 및 예비 펌프 성능 저하 진단. 수위 위험."
            elif self.selected_scenario == "격납건물 증기 누설":
                msg = "격납건물 내부 스팀 밸브 및 환기 시스템 이상 진단."
            QMessageBox.information(self, "진단 결과", msg)
            QTimer.singleShot(3000, self.start_step4)

    def start_step4(self):
        if self.error_stage == 3:
            self.error_stage = 4
            self.manual_mode = True
            self.manual_override_button.setVisible(True)
            if self.selected_scenario == "밸브 개방 고착":
                msg = "수동 조작: 밸브 수동 조절로 냉각 회복 시도."
            elif self.selected_scenario == "급수 펌프 정지":
                msg = "수동 개입: 펌프 재기동 필요. 수위를 80% 이상으로 복구하세요."
            elif self.selected_scenario == "격납건물 증기 누설":
                msg = "수동 폐쇄 및 환기 전환 필요. 압력을 335°C 미만으로 낮추세요."
            QMessageBox.information(self, "수동 개입", msg)

    def manual_recovery(self):
        if self.error_stage == 4:
            valid = False
            if self.selected_scenario == "밸브 개방 고착" and self.reactor_temp < 335:
                valid = True
            elif self.selected_scenario == "급수 펌프 정지" and self.water_level >= 90:
                valid = True
            elif self.selected_scenario == "격납건물 증기 누설" and self.reactor_temp < 335:
                valid = True
            if valid:
                self.start_step5()
            else:
                QMessageBox.warning(self, "복구 실패", "복구 조건 미달: 조치를 계속하세요.")

    def start_step5(self):
        self.error_stage = 5
        action_time = datetime.now()
        waiting_time = (action_time - self.current_error_time).total_seconds() if self.current_error_time else 0
        self.log_error_event(self.selected_scenario + " 복구", self.current_error_time, waiting_time, action_time)
        QMessageBox.information(self, "복구 완료", "정상 복구 완료. 자동 제어 복귀.")
        self.manual_mode = False
        self.manual_override_button.setVisible(False)
        self.alarm_triggered = False
        self.error_stage = 0


    def __init__(self, room_number, parent=None):
        super().__init__(parent)
        self.room = room_number  # Room 번호
        self.setStyleSheet("border: 1px solid black;")

        # NuScale SMR 참고값으로 초기화
        self.ambient_temp = 25.0
        self.reactor_temp = 320.0           # 목표 온도: 320°C
        self.heat_exchanger_temp = 310.0      # 원자로보다 약 10°C 낮음
        self.cooling_tower_temp = self.ambient_temp + (self.heat_exchanger_temp - self.ambient_temp) * 0.3
        self.water_level = 100.0
        self.total_energy = 0.0
        self.total_time = 0.0
        self.simulation_dt = 1.0            # 시뮬레이션 단위 시간(초)
        self.current_day = 1
        self.manual_mode = False

        # 오류 단계 정의
        # 0: 정상, 1: 펌프 유량 저하 감지 (초기 대응), 2: 예비 펌프 기동 및 자동 안전 조치,
        # 3: 고온 경보 및 출력 80% 저감, 4: 운영자 개입(수동 모드), 5: 복구 완료
        self.error_stage = 0
        self.current_error_time = None

        # PID 제어 변수 (Room 2~4에 적용)
        self.pid_integral = 0.0
        self.pid_prev_error = 0.0
        self.Kp = 0.1
        self.Ki = 0.005
        self.Kd = 0.02

        self.init_ui()

        # 시뮬레이션 타이머 (3초마다 업데이트)
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_simulation)
        self.simulation_timer.start(3000)

        # DAY 업데이트 타이머 (30초마다)
        self.day_timer = QTimer()
        self.day_timer.timeout.connect(self.update_day)
        self.day_timer.start(30000)



    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 상단 영역: Room 번호, 상태, DAY, 제어봉 상태, 연료 정보
        top_bar = self.create_top_bar()
        main_layout.addLayout(top_bar)

        # 중앙 패널: 좌측(수치 정보) + 우측(게이지 및 제어 슬라이더)
        center_layout = QHBoxLayout()
        main_layout.addLayout(center_layout)
        left_panel = self.create_left_panel()
        center_layout.addWidget(left_panel)
        right_panel = self.create_right_panel()
        center_layout.addWidget(right_panel)

        # 하단: 수동 복구 버튼 및 수위 표시
        bottom_bar = self.create_bottom_bar()
        main_layout.addLayout(bottom_bar)

    def create_top_bar(self):
        layout = QHBoxLayout()
        room_label = QLabel(f"Room {self.room}")
        room_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(room_label)

        demo_label = QLabel("REALISTIC SIMULATOR")
        demo_label.setStyleSheet("font-weight: bold; color: darkgreen; font-size: 16px; margin-left: 10px;")
        layout.addWidget(demo_label)

        self.day_label = QLabel(f"DAY {self.current_day}")
        self.day_label.setStyleSheet("font-size: 16px; margin-left: 15px;")
        layout.addWidget(self.day_label)

        self.rod_status_label = QLabel("Control Rod Position: 50%")
        self.rod_status_label.setStyleSheet("font-size: 16px; margin-left: 15px;")
        layout.addWidget(self.rod_status_label)

        fuel_label = QLabel("Fuel: 100%")
        fuel_label.setStyleSheet("font-size: 16px; margin-left: 15px;")
        layout.addWidget(fuel_label)

        layout.addStretch()
        return layout

    def create_left_panel(self):
        container = QFrame()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # 온도 정보 그룹박스
        temp_group = QGroupBox("TEMPERATURES (°C)")
        temp_layout = QGridLayout()
        lbl_reactor = QLabel("Reactor:")
        self.lbl_reactor_temp = QLabel(f"{self.reactor_temp:.1f}")
        lbl_hex = QLabel("Heat Exchanger:")
        self.lbl_hex_temp = QLabel(f"{self.heat_exchanger_temp:.1f}")
        lbl_tower = QLabel("Cooling Tower:")
        self.lbl_cool_temp = QLabel(f"{self.cooling_tower_temp:.1f}")
        temp_layout.addWidget(lbl_reactor, 0, 0)
        temp_layout.addWidget(self.lbl_reactor_temp, 0, 1)
        temp_layout.addWidget(lbl_hex, 1, 0)
        temp_layout.addWidget(self.lbl_hex_temp, 1, 1)
        temp_layout.addWidget(lbl_tower, 2, 0)
        temp_layout.addWidget(self.lbl_cool_temp, 2, 1)
        temp_group.setLayout(temp_layout)
        container_layout.addWidget(temp_group)

        # 발전 출력 그룹박스
        power_group = QGroupBox("POWER OUTPUT")
        power_layout = QGridLayout()
        lbl_power = QLabel("Power Output (kW):")
        self.lbl_power = QLabel("0")
        lbl_avg_power = QLabel("Average Power (kW):")
        self.lbl_avg_power = QLabel("0")
        lbl_energy = QLabel("Total Energy Produced:")
        self.lbl_energy_val = QLabel("0")
        power_layout.addWidget(lbl_power, 0, 0)
        power_layout.addWidget(self.lbl_power, 0, 1)
        power_layout.addWidget(lbl_avg_power, 1, 0)
        power_layout.addWidget(self.lbl_avg_power, 1, 1)
        power_layout.addWidget(lbl_energy, 2, 0)
        power_layout.addWidget(self.lbl_energy_val, 2, 1)
        power_group.setLayout(power_layout)
        container_layout.addWidget(power_group)

        # 냉각수 정보 그룹박스
        coolant_group = QGroupBox("COOLANTS")
        coolant_layout = QGridLayout()
        lbl_leak = QLabel("Leakage (L/day):")
        self.lbl_leak = QLabel("0")
        lbl_primary = QLabel("Primary Flow (%):")
        self.lbl_primary = QLabel("50")
        lbl_secondary = QLabel("Secondary Flow (%):")
        self.lbl_secondary = QLabel("50")
        coolant_layout.addWidget(lbl_leak, 0, 0)
        coolant_layout.addWidget(self.lbl_leak, 0, 1)
        coolant_layout.addWidget(lbl_primary, 1, 0)
        coolant_layout.addWidget(self.lbl_primary, 1, 1)
        coolant_layout.addWidget(lbl_secondary, 2, 0)
        coolant_layout.addWidget(self.lbl_secondary, 2, 1)
        coolant_group.setLayout(coolant_layout)
        container_layout.addWidget(coolant_group)

        container_layout.addStretch()
        return container

    def create_right_panel(self):
        container = QFrame()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # 4개의 수직 진행바 게이지 (R1: Reactor, R2: Heat Exchanger, R3: Cooling Tower, R4: Control Rod)
        gauge_layout = QHBoxLayout()
        self.gauge_bars = []
        gauge_labels = [
            "R1\n(Reactor Temp.)",
            "R2\n(Heat Exchanger)",
            "R3\n(Cooling Tower)",
            "R4\n(Control Rod)"
        ]
        for label in gauge_labels:
            box = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            bar = QProgressBar()
            bar.setOrientation(Qt.Vertical)
            bar.setRange(0, 100)
            bar.setValue(25)
            bar.setFixedHeight(150)
            box.addWidget(lbl)
            box.addWidget(bar)
            gauge_layout.addLayout(box)
            self.gauge_bars.append(bar)
        container_layout.addLayout(gauge_layout)

        # 제어 입력: 슬라이더와 SpinBox
        control_layout = QVBoxLayout()
        # 제어봉 위치 슬라이더
        row = QHBoxLayout()
        lbl = QLabel("Control Rod Position (%)")
        self.control_rod_slider = QSlider(Qt.Horizontal)
        self.control_rod_slider.setRange(0, 100)
        self.control_rod_slider.setValue(50)
        self.control_rod_slider.valueChanged.connect(self.rod_position_changed)
        spin = QSpinBox()
        spin.setRange(0, 100)
        spin.setValue(50)
        self.control_rod_slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(self.control_rod_slider.setValue)
        row.addWidget(lbl)
        row.addWidget(self.control_rod_slider)
        row.addWidget(spin)
        control_layout.addLayout(row)

        # Primary Coolant Flow 슬라이더
        row = QHBoxLayout()
        lbl_primary = QLabel("Primary Coolant Flow (%)")
        self.primary_coolant_slider = QSlider(Qt.Horizontal)
        self.primary_coolant_slider.setRange(0, 100)
        self.primary_coolant_slider.setValue(50)
        spin_primary = QSpinBox()
        spin_primary.setRange(0, 100)
        spin_primary.setValue(50)
        self.primary_coolant_slider.valueChanged.connect(spin_primary.setValue)
        spin_primary.valueChanged.connect(self.primary_coolant_slider.setValue)
        row.addWidget(lbl_primary)
        row.addWidget(self.primary_coolant_slider)
        row.addWidget(spin_primary)
        control_layout.addLayout(row)

        # Secondary Coolant Flow 슬라이더
        row = QHBoxLayout()
        lbl_secondary = QLabel("Secondary Coolant Flow (%)")
        self.secondary_coolant_slider = QSlider(Qt.Horizontal)
        self.secondary_coolant_slider.setRange(0, 100)
        self.secondary_coolant_slider.setValue(50)
        spin_secondary = QSpinBox()
        spin_secondary.setRange(0, 100)
        spin_secondary.setValue(50)
        self.secondary_coolant_slider.valueChanged.connect(spin_secondary.setValue)
        spin_secondary.valueChanged.connect(self.secondary_coolant_slider.setValue)
        row.addWidget(lbl_secondary)
        row.addWidget(self.secondary_coolant_slider)
        row.addWidget(spin_secondary)
        control_layout.addLayout(row)

        # Emergency Coolant Flow 슬라이더
        row = QHBoxLayout()
        lbl_emergency = QLabel("Emergency Coolant Flow (%)")
        self.emergency_coolant_slider = QSlider(Qt.Horizontal)
        self.emergency_coolant_slider.setRange(0, 100)
        self.emergency_coolant_slider.setValue(0)
        spin_emergency = QSpinBox()
        spin_emergency.setRange(0, 100)
        spin_emergency.setValue(0)
        self.emergency_coolant_slider.valueChanged.connect(spin_emergency.setValue)
        spin_emergency.valueChanged.connect(self.emergency_coolant_slider.setValue)
        row.addWidget(lbl_emergency)
        row.addWidget(self.emergency_coolant_slider)
        row.addWidget(spin_emergency)
        control_layout.addLayout(row)

        container_layout.addLayout(control_layout)
        container_layout.addStretch()
        return container

    def create_bottom_bar(self):
        layout = QHBoxLayout()
        self.manual_override_button = QPushButton("수동 복구")
        self.manual_override_button.setVisible(False)
        self.manual_override_button.clicked.connect(self.manual_recovery)
        layout.addWidget(self.manual_override_button)

        water_level_label = QLabel("Water Level:")
        layout.addWidget(water_level_label)
        self.water_level_bar = QProgressBar()
        self.water_level_bar.setRange(0, 100)
        self.water_level_bar.setValue(int(self.water_level))
        self.water_level_bar.setFixedWidth(150)
        layout.addWidget(self.water_level_bar)

        layout.addStretch()
        return layout

    def rod_position_changed(self, value):
        self.rod_status_label.setText(f"Control Rod Position: {value}%")

    def update_day(self):
        self.current_day += 1
        self.day_label.setText(f"DAY {self.current_day}")

    def update_simulation(self):
        try:
            if self.error_stage != 0:
                # Room1의 오류 단계별 시뮬레이션 처리
                if self.error_stage == 1:
                    # 1단계: 펌프 유량 저하 → 냉각수 부족으로 원자로 온도 서서히 상승
                    tau = 60  # 온도 변화 시간 상수 (초)
                    target_temp = 330
                    self.reactor_temp += (target_temp - self.reactor_temp) / tau
                    rod_pos = self.control_rod_slider.value() / 100
                    power_output = (1 - rod_pos**1.5) * 120  # 최대 출력 200 kW 기준
                elif self.error_stage == 2:
                    # 2단계: 예비 펌프 기동 → 유량 회복 시도, 온도는 약간 낮아지나 여전히 상승 추세
                    self.reactor_temp -= 0.2
                    power_output = (100 - self.control_rod_slider.value()) * 1.0
                elif self.error_stage == 3:
                    # 3단계: 고온 경보 및 자동 출력 80% 저감 → 추가 안전 조치 적용
                    self.reactor_temp -= 0.3
                    power_output = (100 - self.control_rod_slider.value()) * 0.8
                elif self.error_stage == 4:
                    # 4단계: 수동 모드 (운영자 개입)
                    rod = self.control_rod_slider.value()
                    primary_flow = self.primary_coolant_slider.value()
                    secondary_flow = self.secondary_coolant_slider.value()
                    emergency_flow = self.emergency_coolant_slider.value()
                    if self.selected_scenario == "밸브 개방 고착":
                        heat_gain = (100 - rod) * 0.25
                        cooling_power = (
                            (primary_flow * 0.4) +
                            (secondary_flow * 0.3) +
                            (emergency_flow * 1.2)
                        ) / 100

                    elif self.selected_scenario == "급수 펌프 정지":
                        heat_gain = (100 - rod) * 0.28
                        cooling_power = (
                            (primary_flow * 0.25) +
                            (secondary_flow * 0.2) +
                            (emergency_flow * 1.5)
                        ) / 100

                    elif self.selected_scenario == "격납건물 증기 누설":
                        heat_gain = (100 - rod) * 0.22
                        cooling_power = (
                            (primary_flow * 0.3) +
                            (secondary_flow * 0.25) +
                            (emergency_flow * 1.8)
                        ) / 100

                    cooling_effect = cooling_power * (self.reactor_temp - self.ambient_temp) * 0.015
                    delta_T = (heat_gain - cooling_effect) * self.simulation_dt
                    self.reactor_temp += delta_T
                    power_output = (100 - self.control_rod_slider.value()) * 1.0

                elif self.error_stage == 5:
                    # 복구 완료 후 정상 운전
                    power_output = (100 - self.control_rod_slider.value()) * 2
            elif not self.manual_mode:
                # 정상 운전 (Room 2~4 또는 Room 1의 오류 미발생 시)
                target_temp = 320.0  # 목표 온도
                error = target_temp - self.reactor_temp

                # PID 제어 연산
                self.pid_integral += error * self.simulation_dt
                derivative = (error - self.pid_prev_error) / self.simulation_dt
                pid_output = self.Kp * error + self.Ki * self.pid_integral + self.Kd * derivative
                self.pid_prev_error = error

                # 제어봉 위치 조정
                new_rod = self.control_rod_slider.value() - pid_output
                new_rod = max(0, min(100, new_rod))
                self.control_rod_slider.setValue(new_rod)

                # 온도 동역학: 발전 출력에 따른 온도 상승과 냉각 효과
                primary_flow = self.primary_coolant_slider.value()
                secondary_flow = self.secondary_coolant_slider.value()
                emergency_flow = self.emergency_coolant_slider.value()
                flow_sum = (primary_flow * 0.4 + secondary_flow * 0.3 + emergency_flow * 0.3) / 100
                cooling_effect = flow_sum * (self.reactor_temp - self.ambient_temp)
                rod_frac = self.control_rod_slider.value() / 100
                power_output = max(0, (1 - rod_frac**1.5)) * 120
                heat_input = power_output * 0.002  # 단위 시간당 온도 증가량 (가정)
                temp_delta = heat_input - cooling_effect * 0.01
                self.reactor_temp += self.simulation_dt * temp_delta

                # 열교환기와 냉각탑 온도 계산
                self.heat_exchanger_temp = self.reactor_temp - 10 + (random.random() - 0.5) * 0.3
                self.cooling_tower_temp = self.ambient_temp + (self.heat_exchanger_temp - self.ambient_temp) * 0.3

                # 냉각수 흐름은 자연 변동
                primary_flow = 50 + (random.random() - 0.5) * 2
                secondary_flow = 50 + (random.random() - 0.5) * 2
                self.primary_coolant_slider.setValue(int(primary_flow))
                self.secondary_coolant_slider.setValue(int(secondary_flow))

                power_output = (100 - self.control_rod_slider.value()) * 2

                if self.water_level < 100:
                    self.water_level = min(100, self.water_level + 0.2)
            else:
                # 수동 모드: 운영자가 직접 조절하는 경우
                rod = self.control_rod_slider.value()
                primary_flow = self.primary_coolant_slider.value()
                secondary_flow = self.secondary_coolant_slider.value()
                emergency_flow = self.emergency_coolant_slider.value()
                heat_gain = (100 - rod) * 0.5
                cooling_effect = ((primary_flow * 0.3) + (secondary_flow * 0.2) + (emergency_flow * 0.5)) / 100
                self.reactor_temp += (heat_gain - cooling_effect * (self.reactor_temp - self.ambient_temp)) * self.simulation_dt
                self.heat_exchanger_temp = self.reactor_temp * 0.5 + 25
                self.cooling_tower_temp = self.ambient_temp + (self.heat_exchanger_temp - self.ambient_temp) * 0.3
                power_output = (100 - self.control_rod_slider.value()) * 2

            # GUI 업데이트
            self.lbl_reactor_temp.setText(f"{self.reactor_temp:.1f}")
            self.lbl_hex_temp.setText(f"{self.heat_exchanger_temp:.1f}")
            self.lbl_cool_temp.setText(f"{self.cooling_tower_temp:.1f}")
            self.lbl_power.setText(f"{power_output:.1f}")
            self.total_time += self.simulation_dt
            self.total_energy += power_output * self.simulation_dt
            avg_power = self.total_energy / self.total_time
            self.lbl_avg_power.setText(f"{avg_power:.1f}")
            self.lbl_energy_val.setText(f"{self.total_energy:.1f}")
            self.lbl_leak.setText("0")
            self.water_level_bar.setValue(int(self.water_level))

            # 게이지 업데이트
            reactor_range = (250, 350)
            r1_val = int((self.reactor_temp - reactor_range[0]) / (reactor_range[1] - reactor_range[0]) * 100)
            r1_val = max(0, min(100, r1_val))  # 반드시 클램핑
            r2_val = int(max(0, min(100, (self.heat_exchanger_temp - 25) / (350 - 25) * 100)))
            r3_val = int(max(0, min(100, (self.cooling_tower_temp - self.ambient_temp) / (100 - self.ambient_temp) * 100)))
            r4_val = self.control_rod_slider.value()
            gauge_values = [r1_val, r2_val, r3_val, r4_val]
            for bar, val in zip(self.gauge_bars, gauge_values):
                bar.setValue(val)
        except Exception as e:
            print("update_simulation error:", e)

    # ----- 오류 시나리오 (Room 1 전용) -----

    # 1단계: 펌프 이상 감지 및 초기 대응 (순환펌프 유량 급감)
    def initiate_fault(self):
        try:
            if self.error_stage == 0:
                self.current_error_time = datetime.now()
                self.error_stage = 1
                # 펌프 이상: Primary Coolant Flow를 낮춰 유량 저하를 시뮬레이션
                self.primary_coolant_slider.setValue(20)
                QMessageBox.information(self, "펌프 이상 감지",
                    "자동화 시스템: 순환펌프 유량 급감 감지.\n예비 펌프 기동 시도 중입니다.")
                QTimer.singleShot(3000, self.auto_response_phase)
        except Exception as e:
            print("initiate_fault error:", e)

    # 2단계: 예비 펌프 기동 및 자동 안전 조치
    def auto_response_phase(self):
        try:
            if self.error_stage == 1:
                self.error_stage = 2
                # 예비 펌프 기동 성공 → 유량 회복 시도 (Primary, Secondary flow 증가)
                self.primary_coolant_slider.setValue(70)
                self.secondary_coolant_slider.setValue(70)
                # 부분적 온도 개선 (하지만 근본 문제로 완전한 복구는 아님)
                self.reactor_temp -= 5.0
                QMessageBox.information(self, "자동 안전 조치",
                    "예비 펌프 기동 성공 및 유량 회복 시도.\n그러나 온도 상승이 지속되어 추가 조치가 필요합니다.")
                QTimer.singleShot(5000, self.alarm_phase)
        except Exception as e:
            print("auto_response_phase error:", e)

    # 3단계: 고온 경보 및 자동 원자로 출력 저감 (80% 적용)
    def alarm_phase(self):
        try:
            if self.error_stage == 2:
                if self.reactor_temp > 340:
                    self.error_stage = 3
                    QMessageBox.warning(self, "고온 경보",
                        "경고: 냉각수 온도 상승 및 유량 문제로 인해 원자로 온도가 높습니다.\n자동으로 원자로 출력이 80%로 저감됩니다.")
                    # 추가 제어봉 조작: 출력 저감을 위해 제어봉을 추가 삽입
                    self.control_rod_slider.setValue(min(100, self.control_rod_slider.value() + 10))
                    QTimer.singleShot(3000, self.operator_phase)
                else:
                    self.recovery_phase()
        except Exception as e:
            print("alarm_phase error:", e)

    # 4단계: 운영자 개입 요구 (수동 모드 전환)
    def operator_phase(self):
        try:
            if self.error_stage == 3:
                self.error_stage = 4
                self.manual_mode = True
                self.manual_override_button.setVisible(True)
                QMessageBox.information(self, "운영자 개입 필요",
                    "비상 상황: 냉각수 유량과 온도 문제로 인해 운영자 직접 개입이 필요합니다.\n수동으로 밸브 전환 및 추가 조치를 진행하세요.")
        except Exception as e:
            print("operator_phase error:", e)

    # 수동 복구 버튼 클릭 – 운영자의 수동 조절 후 복구 확인
    def manual_recovery(self):
        try:
            # 복구 조건: 원자로 온도가 325°C 미만이면 복구 진행
            if self.reactor_temp < 330 and self.error_stage == 4:
                self.recovery_phase()
            else:
                QMessageBox.warning(self, "복구 실패",
                    "복구 조건 미달: 온도를 추가로 낮추어 주세요.")
        except Exception as e:
            print("manual_recovery error:", e)

    # 5단계: 복구 완료 및 실험 종료 처리
    def recovery_phase(self):
        try:
            if self.error_stage in [2, 3] or (self.manual_mode and self.error_stage == 4):
                self.error_stage = 5
                action_time = datetime.now()
                waiting_time = (action_time - self.current_error_time).total_seconds() if self.current_error_time else 0
                self.log_error_event("복구 완료", self.current_error_time, waiting_time, action_time)
                QMessageBox.information(self, "실험 종료",
                    "온도가 안전 범위로 복구되었습니다.\n원자로 출력이 서서히 정상으로 회복됩니다.\n실험을 종료합니다.")
                self.manual_mode = False
                self.manual_override_button.setVisible(False)
                # 복구 후 정상 운전을 위해 제어봉 초기화
                self.control_rod_slider.setValue(50)
                self.error_stage = 0
                # 실험 종료 시 시뮬레이션 관련 타이머 중지
                self.simulation_timer.stop()
                self.day_timer.stop()
        except Exception as e:
            print("recovery_phase error:", e)

    def log_error_event(self, error_label, error_time, waiting_time, action_time):
        try:
            with open(LOG_FILE_PATH, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    self.room,
                    error_label,
                    error_time.strftime("%Y-%m-%d %H:%M:%S") if error_time else "",
                    f"{waiting_time:.1f}",
                    action_time.strftime("%Y-%m-%d %H:%M:%S")
                ])
        except Exception as e:
            print(f"로그 기록 실패: {e}")

class MultiSMRMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-SMR Monitoring System")
        self.setGeometry(50, 50, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        grid_layout = QGridLayout()
        main_widget.setLayout(grid_layout)

        self.smr_widgets = []
        for i in range(4):
            smr = SMRWidget(room_number=i+1)
            group_box = QGroupBox(f"Room {i+1}")
            box_layout = QVBoxLayout()
            box_layout.addWidget(smr)
            group_box.setLayout(box_layout)
            row = i // 2
            col = i % 2
            grid_layout.addWidget(group_box, row, col)
            self.smr_widgets.append((smr, group_box))

        # 오류 시나리오 실행을 하나의 Room에서만 랜덤으로 시작
        QTimer.singleShot(10000, self.start_random_error_scenario)

    def start_random_error_scenario(self):
        error_pair = random.choice(self.smr_widgets)
        for smr, group_box in self.smr_widgets:

            if smr == error_pair[0]:
                group_box.setStyleSheet("QGroupBox { border: 3px solid red; border-radius: 10px; margin-top: 10px; }")
                smr.start_error_sequence()

            else:
                group_box.setStyleSheet("QGroupBox { border: 1px solid lightgray; margin-top: 10px; }")
                smr.error_stage = 0

if __name__ == "__main__":
    init_log_file()
    app = QApplication(sys.argv)
    window = MultiSMRMonitor()
    window.show()
    app.exec_()

