import sys
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QLineEdit, QLabel, QSplitter,
                           QMessageBox, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor

class VirtualFileSystem:
    def __init__(self):
        self.root = {
            'type': 'directory',
            'name': '/',
            'children': {
                'bin': {
                    'type': 'directory',
                    'name': 'bin',
                    'children': {
                        'ls': {'type': 'file', 'name': 'ls', 'content': '#!/bin/bash\necho "List directory contents"'},
                        'cat': {'type': 'file', 'name': 'cat', 'content': '#!/bin/bash\necho "Concatenate files"'}
                    }
                },
                'etc': {
                    'type': 'directory',
                    'name': 'etc',
                    'children': {
                        'passwd': {'type': 'file', 'name': 'passwd', 'content': 'root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash'},
                        'hostname': {'type': 'file', 'name': 'hostname', 'content': 'linux-simulator'}
                    }
                },
                'home': {
                    'type': 'directory',
                    'name': 'home',
                    'children': {
                        'user': {
                            'type': 'directory',
                            'name': 'user',
                            'children': {
                                'Documents': {'type': 'directory', 'name': 'Documents', 'children': {}},
                                'Downloads': {'type': 'directory', 'name': 'Downloads', 'children': {}},
                                'hello.txt': {'type': 'file', 'name': 'hello.txt', 'content': 'Hello, Linux World!'}
                            }
                        }
                    }
                },
                'var': {
                    'type': 'directory',
                    'name': 'var',
                    'children': {
                        'log': {
                            'type': 'directory',
                            'name': 'log',
                            'children': {
                                'syslog': {'type': 'file', 'name': 'syslog', 'content': 'System log file'}
                            }
                        }
                    }
                }
            }
        }
        self.current_path = ['/']

    def get_current_dir(self):
        current = self.root
        for part in self.current_path[1:]:
            if part in current['children']:
                current = current['children'][part]
            else:
                return None
        return current

    def list_dir(self, path=None):
        if path is None:
            current = self.get_current_dir()
        else:
            current = self._resolve_path(path)
        if current and current['type'] == 'directory':
            return sorted(current['children'].keys())
        return []

    def _resolve_path(self, path):
        if path.startswith('/'):
            parts = path.strip('/').split('/')
            current = self.root
        else:
            parts = path.split('/')
            current = self.get_current_dir()

        for part in parts:
            if part == '..':
                if len(self.current_path) > 1:
                    self.current_path.pop()
                current = self.get_current_dir()
            elif part == '.':
                continue
            elif part in current['children']:
                current = current['children'][part]
            else:
                return None
        return current

    def change_dir(self, path):
        target = self._resolve_path(path)
        if target and target['type'] == 'directory':
            if path.startswith('/'):
                self.current_path = ['/'] + path.strip('/').split('/')
            else:
                for part in path.split('/'):
                    if part == '..':
                        if len(self.current_path) > 1:
                            self.current_path.pop()
                    elif part != '.':
                        self.current_path.append(part)
            return True
        return False

    def get_path(self):
        return '/'.join(self.current_path)

    def create_file(self, name):
        current = self.get_current_dir()
        if current and name not in current['children']:
            current['children'][name] = {'type': 'file', 'name': name, 'content': ''}
            return True
        return False

    def create_dir(self, name):
        current = self.get_current_dir()
        if current and name not in current['children']:
            current['children'][name] = {'type': 'directory', 'name': name, 'children': {}}
            return True
        return False

    def read_file(self, path):
        target = self._resolve_path(path)
        if target and target['type'] == 'file':
            return target['content']
        return None

    def remove(self, path):
        target = self._resolve_path(path)
        if target:
            parent = self.get_current_dir()
            if parent and target['name'] in parent['children']:
                del parent['children'][target['name']]
                return True
        return False

class LinuxSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vfs = VirtualFileSystem()
        self.command_history = []  # 명령어 히스토리 저장
        self.editor_mode = False  # 에디터 모드 상태
        self.editor_buffer = []  # 에디터 버퍼
        self.editor_filename = ""  # 편집 중인 파일명
        self.top_mode = False  # top 모드 상태
        self.commands = {
            'ls': self.ls_command,
            'cd': self.cd_command,
            'pwd': self.pwd_command,
            'mkdir': self.mkdir_command,
            'rm': self.rm_command,
            'cp': self.cp_command,
            'mv': self.mv_command,
            'cat': self.cat_command,
            'touch': self.touch_command,
            'clear': self.clear_command,
            'exit': self.exit_command,
            'echo': self.echo_command,
            'whoami': self.whoami_command,
            'date': self.date_command,
            'help': self.help_command,
            'history': self.history_command,
            'vi': self.vi_command,
            'vim': self.vi_command,
            'nano': self.nano_command,
            'top': self.top_command
        }
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('리눅스 명령어 학습 시뮬레이터')
        self.setGeometry(100, 100, 800, 600)
        
        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 상단 버튼 영역
        button_layout = QHBoxLayout()
        creator_button = QPushButton("제작자 정보 보기")
        creator_button.clicked.connect(self.show_creator_info)
        button_layout.addWidget(creator_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 환영 메시지와 명령어 목록을 표시할 레이블
        welcome_label = QLabel("리눅스 명령어 학습 시뮬레이터에 오신 것을 환영합니다!")
        commands_label = QLabel("사용 가능한 명령어: ls, cd, pwd, mkdir, rm, cp, mv, cat, touch, clear, exit, echo, whoami, date, help, history, vi, vim, nano, top")
        self.current_dir_label = QLabel("현재 디렉토리: /")
        
        # 레이블 스타일 설정
        welcome_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        commands_label.setStyleSheet("font-size: 11pt;")
        self.current_dir_label.setStyleSheet("font-size: 11pt; color: blue;")
        
        # 레이블 추가
        layout.addWidget(welcome_label)
        layout.addWidget(commands_label)
        layout.addWidget(self.current_dir_label)
        
        # 스플리터로 화면을 상하로 분할
        splitter = QSplitter(Qt.Vertical)
        
        # 상단 패널 (Windows 환경 시뮬레이션)
        self.windows_panel = QTextEdit()
        self.windows_panel.setReadOnly(True)
        self.windows_panel.setFont(QFont('Consolas', 10))
        
        # 하단 패널 (터미널)
        terminal_widget = QWidget()
        terminal_layout = QVBoxLayout(terminal_widget)
        
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont('Consolas', 10))
        
        # 명령어 입력을 위한 위젯들
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prompt_label = QLabel()
        self.prompt_label.setFont(QFont('Consolas', 10))
        self.prompt_label.setStyleSheet("color: green;")
        
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self.execute_command)
        
        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.command_input)
        
        terminal_layout.addWidget(self.terminal_output)
        terminal_layout.addWidget(input_widget)
        
        # 스플리터에 위젯 추가
        splitter.addWidget(self.windows_panel)
        splitter.addWidget(terminal_widget)
        
        # 스플리터 비율 설정
        splitter.setSizes([200, 400])
        
        layout.addWidget(splitter)
        
        # 초기 메시지 출력
        self.terminal_output.append("리눅스 명령어 학습 시뮬레이터에 오신 것을 환영합니다!")
        self.terminal_output.append("사용 가능한 명령어: ls, cd, pwd, mkdir, rm, cp, mv, cat, touch, clear, exit, echo, whoami, date, help, history, vi, vim, nano, top")
        self.terminal_output.append("현재 디렉토리: " + self.vfs.get_path())
        self.terminal_output.append("")
        
        # 초기 프롬프트 설정
        self.update_prompt()

    def update_prompt(self):
        current_path = self.vfs.get_path()
        if current_path == "/":
            path_display = "/"
        else:
            path_display = current_path
        self.prompt_label.setText(f"user@ubuntu_Server:{path_display}$ ")

    def execute_command(self):
        command = self.command_input.text().strip()
        self.command_input.clear()
        
        if not command:
            return
            
        if self.editor_mode:
            if command == ":wq":
                self.save_and_exit_editor()
            elif command == ":q!":
                self.exit_editor_without_save()
            elif command == "^X":  # Ctrl+X (nano 종료)
                self.save_and_exit_editor()
            elif command == "^C":  # Ctrl+C (nano 취소)
                self.exit_editor_without_save()
            else:
                self.editor_buffer.append(command)
                self.terminal_output.append(command)
            return
            
        if self.top_mode:
            if command == "q":
                self.top_mode = False
                self.terminal_output.append("top 모드를 종료합니다.")
                self.update_prompt()
                return
            self.show_top_info()
            return
            
        # 명령어와 프롬프트를 함께 출력
        self.terminal_output.append(f"{self.prompt_label.text()}{command}")
        self.command_history.append(command)  # 명령어 히스토리에 추가
        
        # 명령어 파싱
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            self.terminal_output.append(f"명령어 '{cmd}'를 찾을 수 없습니다.")
        
        self.terminal_output.append("")
        self.update_prompt()
        self.terminal_output.moveCursor(QTextCursor.End)
        
    def ls_command(self, args):
        try:
            path = args[0] if args else None
            items = self.vfs.list_dir(path)
            if items is not None:
                self.terminal_output.append("\n".join(items))
                self.update_windows_panel(f"디렉토리 내용을 표시합니다: {path if path else self.vfs.get_path()}")
            else:
                self.terminal_output.append(f"디렉토리를 찾을 수 없습니다: {path}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def cd_command(self, args):
        if not args:
            self.terminal_output.append("사용법: cd <디렉토리>")
            return
            
        try:
            if self.vfs.change_dir(args[0]):
                self.terminal_output.append(f"현재 디렉토리: {self.vfs.get_path()}")
                self.update_windows_panel(f"디렉토리로 이동합니다: {args[0]}")
                self.update_current_dir()  # 현재 디렉토리 레이블 업데이트
                self.update_prompt()  # 프롬프트 업데이트
            else:
                self.terminal_output.append(f"디렉토리를 찾을 수 없습니다: {args[0]}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def pwd_command(self, args):
        self.terminal_output.append(self.vfs.get_path())
        self.update_windows_panel(f"현재 경로: {self.vfs.get_path()}")
        self.update_current_dir()  # 현재 디렉토리 레이블 업데이트
        
    def mkdir_command(self, args):
        if not args:
            self.terminal_output.append("사용법: mkdir <디렉토리명>")
            return
            
        try:
            if self.vfs.create_dir(args[0]):
                self.terminal_output.append(f"디렉토리 '{args[0]}'가 생성되었습니다.")
                self.update_windows_panel(f"새 디렉토리 생성: {args[0]}")
                # 생성된 디렉토리 목록에 추가
                current_dir = self.vfs.get_current_dir()
                if current_dir:
                    current_dir['children'][args[0]] = {
                        'type': 'directory',
                        'name': args[0],
                        'children': {}
                    }
            else:
                self.terminal_output.append(f"디렉토리를 생성할 수 없습니다: {args[0]}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def rm_command(self, args):
        if not args:
            self.terminal_output.append("사용법: rm <파일명>")
            return
            
        try:
            target = self.vfs._resolve_path(args[0])
            if target:
                parent = self.vfs.get_current_dir()
                if parent and target['name'] in parent['children']:
                    del parent['children'][target['name']]
                    self.terminal_output.append(f"'{args[0]}'가 삭제되었습니다.")
                    self.update_windows_panel(f"파일/디렉토리 삭제: {args[0]}")
                else:
                    self.terminal_output.append(f"파일이나 디렉토리를 찾을 수 없습니다: {args[0]}")
            else:
                self.terminal_output.append(f"파일이나 디렉토리를 찾을 수 없습니다: {args[0]}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def cp_command(self, args):
        if len(args) != 2:
            self.terminal_output.append("사용법: cp <원본> <대상>")
            return
            
        try:
            # 가상 파일 시스템에서는 복사 기능을 구현하지 않음
            self.terminal_output.append("가상 파일 시스템에서는 복사 기능이 지원되지 않습니다.")
            self.update_windows_panel(f"복사 작업 시뮬레이션: {args[0]} -> {args[1]}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def mv_command(self, args):
        if len(args) != 2:
            self.terminal_output.append("사용법: mv <원본> <대상>")
            return
            
        try:
            # 가상 파일 시스템에서는 이동 기능을 구현하지 않음
            self.terminal_output.append("가상 파일 시스템에서는 이동 기능이 지원되지 않습니다.")
            self.update_windows_panel(f"이동 작업 시뮬레이션: {args[0]} -> {args[1]}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def cat_command(self, args):
        if not args:
            self.terminal_output.append("사용법: cat <파일명>")
            return
            
        try:
            content = self.vfs.read_file(args[0])
            if content is not None:
                self.terminal_output.append(content)
                self.update_windows_panel(f"파일 내용 표시: {args[0]}")
            else:
                self.terminal_output.append(f"파일을 찾을 수 없습니다: {args[0]}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def touch_command(self, args):
        if not args:
            self.terminal_output.append("사용법: touch <파일명>")
            return
            
        try:
            if self.vfs.create_file(args[0]):
                self.terminal_output.append(f"파일 '{args[0]}'가 생성되었습니다.")
                self.update_windows_panel(f"새 파일 생성: {args[0]}")
                # 생성된 파일 목록에 추가
                current_dir = self.vfs.get_current_dir()
                if current_dir:
                    current_dir['children'][args[0]] = {
                        'type': 'file',
                        'name': args[0],
                        'content': ''
                    }
            else:
                self.terminal_output.append(f"파일을 생성할 수 없습니다: {args[0]}")
        except Exception as e:
            self.terminal_output.append(f"오류: {str(e)}")
            
    def clear_command(self, args):
        self.terminal_output.clear()
        self.update_windows_panel("화면을 초기화합니다.")
        
    def exit_command(self, args):
        self.terminal_output.append("프로그램을 종료합니다.")
        self.close()
        
    def update_windows_panel(self, message):
        self.windows_panel.append(message)
        self.windows_panel.moveCursor(QTextCursor.End)

    def show_creator_info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("제작자 정보")
        msg.setText("리눅스 명령어 학습 시뮬레이터")
        msg.setInformativeText("제작자: 김연범\n이메일: yeonbumk@gmail.com")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def update_current_dir(self):
        self.current_dir_label.setText(f"현재 디렉토리: {self.vfs.get_path()}")

    def echo_command(self, args):
        if not args:
            self.terminal_output.append("")
            return
        self.terminal_output.append(" ".join(args))
        self.update_windows_panel(f"텍스트 출력: {' '.join(args)}")

    def whoami_command(self, args):
        self.terminal_output.append("user")
        self.update_windows_panel("현재 사용자 정보 표시")

    def date_command(self, args):
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.terminal_output.append(current_time)
        self.update_windows_panel("현재 날짜와 시간 표시")

    def help_command(self, args):
        help_text = """
사용 가능한 명령어:
- ls: 디렉토리 내용 보기
- cd: 디렉토리 이동
- pwd: 현재 작업 디렉토리 확인
- mkdir: 새 디렉토리 생성
- rm: 파일/디렉토리 삭제
- cp: 파일/디렉토리 복사
- mv: 파일/디렉토리 이동
- cat: 파일 내용 보기
- touch: 빈 파일 생성
- clear: 화면 지우기
- exit: 프로그램 종료
- echo: 텍스트 출력
- whoami: 현재 사용자 정보
- date: 현재 날짜와 시간
- help: 이 도움말 보기
- history: 명령어 히스토리 보기
- vi/vim: 텍스트 에디터 (기본 모드)
- nano: 텍스트 에디터 (간단 모드)
        """
        self.terminal_output.append(help_text)
        self.update_windows_panel("도움말 정보 표시")

    def history_command(self, args):
        if not self.command_history:
            self.terminal_output.append("명령어 히스토리가 없습니다.")
            return
        for i, cmd in enumerate(self.command_history, 1):
            self.terminal_output.append(f"{i}  {cmd}")
        self.update_windows_panel("명령어 히스토리 표시")

    def top_command(self, args):
        self.top_mode = True
        self.terminal_output.append("top - 시뮬레이션된 프로세스 정보")
        self.terminal_output.append("종료하려면 'q'를 입력하세요.")
        self.terminal_output.append("")
        self.show_top_info()
        self.update_windows_panel("시스템 프로세스 정보 표시")

    def show_top_info(self):
        import random
        import time
        
        # 시뮬레이션된 프로세스 정보 생성
        processes = [
            {"PID": 1, "USER": "root", "PR": 20, "NI": 0, "VIRT": "100m", "RES": "10m", "SHR": "5m", "S": "S", "CPU": random.randint(0, 5), "MEM": random.randint(1, 10), "TIME": "00:00:10", "COMMAND": "init"},
            {"PID": 2, "USER": "root", "PR": 20, "NI": 0, "VIRT": "200m", "RES": "20m", "SHR": "10m", "S": "S", "CPU": random.randint(0, 5), "MEM": random.randint(1, 10), "TIME": "00:00:20", "COMMAND": "kthreadd"},
            {"PID": 3, "USER": "user", "PR": 20, "NI": 0, "VIRT": "300m", "RES": "30m", "SHR": "15m", "S": "R", "CPU": random.randint(0, 5), "MEM": random.randint(1, 10), "TIME": "00:00:30", "COMMAND": "bash"},
            {"PID": 4, "USER": "user", "PR": 20, "NI": 0, "VIRT": "400m", "RES": "40m", "SHR": "20m", "S": "S", "CPU": random.randint(0, 5), "MEM": random.randint(1, 10), "TIME": "00:00:40", "COMMAND": "python"},
            {"PID": 5, "USER": "user", "PR": 20, "NI": 0, "VIRT": "500m", "RES": "50m", "SHR": "25m", "S": "S", "CPU": random.randint(0, 5), "MEM": random.randint(1, 10), "TIME": "00:00:50", "COMMAND": "top"}
        ]
        
        # 헤더 출력
        self.terminal_output.append("PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND")
        
        # 프로세스 정보 출력
        for proc in processes:
            line = f"{proc['PID']:<4} {proc['USER']:<9} {proc['PR']:<3} {proc['NI']:<3} {proc['VIRT']:<7} {proc['RES']:<7} {proc['SHR']:<7} {proc['S']} {proc['CPU']:>4} {proc['MEM']:>4} {proc['TIME']:>9} {proc['COMMAND']}"
            self.terminal_output.append(line)
        
        # 시스템 정보 출력
        self.terminal_output.append("")
        self.terminal_output.append(f"Tasks: {len(processes)} total, 1 running, {len(processes)-1} sleeping, 0 stopped, 0 zombie")
        self.terminal_output.append(f"Cpu(s): {random.randint(1, 100)}%us, {random.randint(1, 50)}%sy, {random.randint(0, 20)}%ni, {random.randint(1, 50)}%id, {random.randint(0, 10)}%wa, {random.randint(0, 5)}%hi, {random.randint(0, 5)}%si, {random.randint(0, 5)}%st")
        self.terminal_output.append(f"Mem: {random.randint(1000, 8000)}M total, {random.randint(500, 4000)}M used, {random.randint(500, 4000)}M free, {random.randint(100, 1000)}M buffers")
        self.terminal_output.append(f"Swap: {random.randint(1000, 4000)}M total, {random.randint(0, 1000)}M used, {random.randint(1000, 4000)}M free, {random.randint(500, 2000)}M cached")
        self.terminal_output.append("")

    def vi_command(self, args):
        if not args:
            self.terminal_output.append("사용법: vi <파일명>")
            return
            
        self.editor_filename = args[0]
        self.editor_mode = True
        self.editor_buffer = []
        self.terminal_output.append(f"'{self.editor_filename}' 파일 편집 모드로 진입했습니다.")
        self.terminal_output.append("편집을 마치려면 :wq 를 입력하세요.")
        self.terminal_output.append("저장하지 않고 종료하려면 :q! 를 입력하세요.")
        self.update_windows_panel(f"파일 편집 시작: {self.editor_filename}")

    def nano_command(self, args):
        if not args:
            self.terminal_output.append("사용법: nano <파일명>")
            return
            
        self.editor_filename = args[0]
        self.editor_mode = True
        self.editor_buffer = []
        self.terminal_output.append(f"'{self.editor_filename}' 파일 편집 모드로 진입했습니다.")
        self.terminal_output.append("편집을 마치려면 ^X (Ctrl+X)를 입력하세요.")
        self.terminal_output.append("저장하지 않고 종료하려면 ^C (Ctrl+C)를 입력하세요.")
        self.update_windows_panel(f"파일 편집 시작: {self.editor_filename}")

    def save_and_exit_editor(self):
        if self.editor_filename:
            content = "\n".join(self.editor_buffer)
            current_dir = self.vfs.get_current_dir()
            if current_dir:
                current_dir['children'][self.editor_filename] = {
                    'type': 'file',
                    'name': self.editor_filename,
                    'content': content
                }
                self.terminal_output.append(f"'{self.editor_filename}' 파일이 저장되었습니다.")
                self.update_windows_panel(f"파일 저장 완료: {self.editor_filename}")
        self.editor_mode = False
        self.editor_buffer = []
        self.editor_filename = ""

    def exit_editor_without_save(self):
        self.terminal_output.append("편집을 취소하고 종료합니다.")
        self.update_windows_panel("파일 편집 취소")
        self.editor_mode = False
        self.editor_buffer = []
        self.editor_filename = ""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LinuxSimulator()
    ex.show()
    sys.exit(app.exec_()) 