import pandas as pd
from datetime import datetime
import os
import json
from error_handler import error_handler


def initialize_all_data():
    """Initialize all required CSV files with sample data for deployment"""

    # Ensure data directory exists
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Initialize logs.csv with complete column structure
    logs_df = pd.DataFrame({
        'id': [1, 2, 3],
        'timestamp': [
            '2025-01-23 07:30:00.000000', '2025-01-23 07:31:00.000000',
            '2025-01-23 07:32:00.000000'
        ],
        'username': ['조성우', '강서준', '조성우'],
        'user_name': ['조성우', '강서준', '조성우'],
        'user_role': ['선생님', '총무', '선생님'],
        'club_name': ['시스템', '코딩', '시스템'],
        'ip_address': ['127.0.0.1', '127.0.0.1', '127.0.0.1'],
        'session_id': ['session_001', 'session_002', 'session_003'],
        'activity_type': ['Authentication', 'Data Access', 'Admin Action'],
        'activity_description':
        ['Login attempt - Success', 'View posts', 'System initialization'],
        'target_resource': ['Login System', 'posts', 'System'],
        'action_result': ['Success', 'Success', 'Success'],
        'error_message': ['None', 'None', 'None'],
        'user_agent': ['Streamlit App', 'Streamlit App', 'Streamlit App'],
        'device_type': ['Desktop', 'Desktop', 'Desktop'],
        'browser_info': [
            'Browser Detection N/A', 'Browser Detection N/A',
            'Browser Detection N/A'
        ],
        'request_method': ['POST', 'GET', 'POST'],
        'response_time': ['15.23ms', '8.45ms', '22.67ms'],
        'data_modified': ['None', 'None', '1 records'],
        'security_level': ['Normal', 'Normal', 'High'],
        'notes':
        ['User login successful', 'None', 'System initialization complete']
    })
    logs_df.to_csv(os.path.join(data_dir, 'logs.csv'),
                   index=False,
                   encoding='utf-8-sig')

    # Initialize users.csv (if not exists)
    users_file = os.path.join(data_dir, 'users.csv')
    if not os.path.exists(users_file):
        users_df = pd.DataFrame({
            'username': ['조성우', '강서준', '김보경'],
            'password': ['admin', '1234', '1234'],
            'name': ['조성우', '강서준', '김보경'],
            'role': ['선생님', '총무', '회장'],
            'club_name': ['전체', '코딩', '만들기'],
            'club_role': ['선생님', '총무', '회장'],
            'created_date': [
                '2024-01-15 09:00:00', '2024-01-15 09:07:00',
                '2024-01-15 09:07:00'
            ]
        })
        users_df.to_csv(users_file, index=False, encoding='utf-8-sig')

    # Initialize clubs.csv (if not exists)
    clubs_file = os.path.join(data_dir, 'clubs.csv')
    if not os.path.exists(clubs_file):
        clubs_df = pd.DataFrame({
            'name': ['코딩', '만들기', '미스테리탐구', '댄스', '줄넘기', '풍선아트'],
            'icon': ['💻', '🔨', '🔍', '💃', '🪢', '🎈'],
            'description': [
                '프로그래밍을 배우는 동아리', '다양한 만들기 활동', '미스테리를 풀어보는 동아리', '춤을 배우는 동아리',
                '줄넘기 운동', '풍선아트 만들기'
            ],
            'president': ['정찬희', '김보경', '오채윤', '백주아', '김제이', '최명준'],
            'max_members': [15, 12, 10, 15, 20, 10],
            'created_date': [
                '2024-01-15 10:00:00', '2024-01-15 10:00:00',
                '2024-01-15 10:00:00', '2024-01-15 10:00:00',
                '2024-01-15 10:00:00', '2024-01-15 10:00:00'
            ]
        })
        clubs_df.to_csv(clubs_file, index=False, encoding='utf-8-sig')

    # Initialize badges.csv
    badges_df = pd.DataFrame({
        'id': [1, 2],
        'username': ['강서준', '김보경'],
        'badge_name': ['출석왕', '과제마스터'],
        'badge_icon': ['👑', '📚'],
        'description': ['30일 연속 출석', '과제 10개 완료'],
        'awarded_date': ['2025-01-20 10:00:00', '2025-01-21 15:30:00'],
        'awarded_by': ['System', 'System']
    })
    badges_df.to_csv(os.path.join(data_dir, 'badges.csv'),
                     index=False,
                     encoding='utf-8-sig')

    # Initialize portfolio.csv
    portfolio_df = pd.DataFrame({
        'id': [1, 2],
        'username': ['강서준', '김보경'],
        'title': ['나의 첫 번째 프로젝트', '창의적인 아이디어'],
        'category': ['프로그래밍 프로젝트', '창작 활동'],
        'description': ['Python으로 만든 간단한 게임입니다.', '새로운 아이디어를 구현한 작품입니다.'],
        'technologies': ['Python, Pygame', 'HTML, CSS, JavaScript'],
        'status': ['완료', '진행중'],
        'project_url': ['https://github.com/student1/game', ''],
        'tags': ['게임, Python, 초보자', '창작, 웹개발'],
        'image_path': ['', ''],
        'created_date': ['2025-01-20 14:00:00', '2025-01-21 16:00:00']
    })
    portfolio_df.to_csv(os.path.join(data_dir, 'portfolio.csv'),
                        index=False,
                        encoding='utf-8-sig')

    # Add posts if file doesn't exist
    posts_file = os.path.join(data_dir, 'posts.csv')
    if not os.path.exists(posts_file):
        sample_posts = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ['환영합니다!', '첫 번째 과제 안내', '동아리 모임 안내'],
            'content': [
                '폴라리스반 동아리 시스템에 오신 것을 환영합니다.', '이번 주 과제에 대한 안내사항입니다.',
                '이번 주 동아리 모임 일정을 알려드립니다.'
            ],
            'author': ['조성우', '조성우', '강서준'],
            'club': ['전체', '코딩', '코딩'],
            'tags': ['환영, 시작', '과제, 안내', '모임, 일정'],
            'image_path': ['', '', ''],
            'likes': [5, 3, 7],
            'comments': [2, 1, 3],
            'created_date': [
                '2025-01-20 09:00:00', '2025-01-21 10:00:00',
                '2025-01-22 11:00:00'
            ]
        })
        sample_posts.to_csv(posts_file, index=False, encoding='utf-8-sig')

    # Add assignments if file doesn't exist
    assignments_file = os.path.join(data_dir, 'assignments.csv')
    if not os.path.exists(assignments_file):
        sample_assignments = pd.DataFrame({
            'id': [1, 2],
            'title': ['Python 기초 학습', '창의적 아이디어 발표'],
            'description':
            ['Python 기초 문법을 학습하고 간단한 프로그램을 작성하세요.', '자신만의 창의적인 아이디어를 발표해보세요.'],
            'club': ['코딩', '미스테리탐구'],
            'creator': ['조성우', '조성우'],
            'due_date': ['2025-02-28 23:59:59', '2025-03-05 23:59:59'],
            'status': ['활성', '활성'],
            'created_date': ['2025-01-20 10:00:00', '2025-01-21 11:00:00']
        })
        sample_assignments.to_csv(assignments_file,
                                  index=False,
                                  encoding='utf-8-sig')

    # Add attendance records if file doesn't exist
    attendance_file = os.path.join(data_dir, 'attendance.csv')
    if not os.path.exists(attendance_file):
        sample_attendance = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6],
            'username': ['강서준', '김보경', '강서준', '김보경', '강서준', '김보경'],
            'club': ['코딩', '만들기', '코딩', '만들기', '코딩', '만들기'],
            'date': [
                '2025-01-20', '2025-01-20', '2025-01-21', '2025-01-21',
                '2025-01-22', '2025-01-22'
            ],
            'status': ['출석', '출석', '지각', '출석', '출석', '결석'],
            'recorded_by': ['조성우', '조성우', '조성우', '조성우', '조성우', '조성우']
        })
        sample_attendance.to_csv(attendance_file,
                                 index=False,
                                 encoding='utf-8-sig')

    # Add quizzes if file doesn't exist
    quizzes_file = os.path.join(data_dir, 'quizzes.csv')
    if not os.path.exists(quizzes_file):
        sample_quizzes = [{
            'id':
            1,
            'title':
            '파이썬 기초 퀴즈',
            'description':
            '파이썬의 기본 문법을 테스트하는 퀴즈입니다.',
            'club':
            '코딩',
            'creator':
            '조성우',
            'questions':
            json.dumps([{
                'question':
                '파이썬에서 리스트를 생성하는 올바른 방법은?',
                'options':
                ['list = []', 'list = ()', 'list = {}', 'list = ""'],
                'correct':
                '선택지 1'
            }, {
                'question': 'print() 함수의 역할은?',
                'options': ['값을 저장', '값을 출력', '값을 삭제', '값을 계산'],
                'correct': '선택지 2'
            }],
                       ensure_ascii=False),
            'time_limit':
            10,
            'attempts_allowed':
            3,
            'status':
            '활성',
            'created_date':
            '2025-01-20 14:00:00'
        }]
        sample_quizzes_df = pd.DataFrame(sample_quizzes)
        sample_quizzes_df.to_csv(quizzes_file,
                                 index=False,
                                 encoding='utf-8-sig')

    # Add votes if file doesn't exist
    votes_file = os.path.join(data_dir, 'votes.csv')
    if not os.path.exists(votes_file):
        sample_votes = pd.DataFrame({
            'id': [1, 2],
            'title': ['다음 모임 장소 투표', '간식 선택 투표'],
            'description': ['다음 동아리 모임 장소를 정해주세요.', '모임에서 먹을 간식을 선택해주세요.'],
            'club': ['코딩', '전체'],
            'creator': ['강서준', '조성우'],
            'options': ['["컴퓨터실", "도서관", "교실"]', '["과자", "음료수", "과일", "케이크"]'],
            'end_date': ['2025-02-25 23:59:59', '2025-02-28 23:59:59'],
            'created_date': ['2025-01-20 15:00:00', '2025-01-21 16:00:00']
        })
        sample_votes.to_csv(votes_file, index=False, encoding='utf-8-sig')

    # Add schedules if file doesn't exist
    schedules_file = os.path.join(data_dir, 'schedules.csv')
    if not os.path.exists(schedules_file):
        sample_schedules = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ['코딩 동아리 모임', '만들기 워크샵', '미스테리 탐구'],
            'description':
            ['Python 기초 학습 및 프로젝트 진행', '창의적인 만들기 활동', '흥미로운 미스테리 풀기'],
            'club': ['코딩', '만들기', '미스테리탐구'],
            'date': ['2025-02-25', '2025-02-26', '2025-02-27'],
            'time': ['14:00', '15:00', '16:00'],
            'location': ['컴퓨터실', '미술실', '과학실'],
            'creator': ['조성우', '조성우', '조성우'],
            'created_date': [
                '2025-01-20 10:00:00', '2025-01-20 11:00:00',
                '2025-01-20 12:00:00'
            ]
        })
        sample_schedules.to_csv(schedules_file,
                                index=False,
                                encoding='utf-8-sig')

    # Initialize notifications.csv with required columns
    notifications_file = os.path.join(data_dir, 'notifications.csv')
    if not os.path.exists(notifications_file):
        sample_notifications = pd.DataFrame({
            'id': [1, 2, 3],
            'username': ['강서준', '김보경', 'all'],
            'title': ['새 과제 등록', '출석 확인', '시스템 점검 안내'],
            'message':
            ['새로운 과제가 등록되었습니다.', '오늘 출석을 확인해주세요.', '시스템 점검이 예정되어 있습니다.'],
            'type': ['info', 'warning', 'announcement'],
            'read': [False, False, False],
            'created_date': [
                '2025-01-20 09:00:00', '2025-01-21 10:00:00',
                '2025-01-22 11:00:00'
            ]
        })
        sample_notifications.to_csv(notifications_file,
                                    index=False,
                                    encoding='utf-8-sig')

    # Add chat logs if file doesn't exist
    chat_logs_file = os.path.join(data_dir, 'chat_logs.csv')
    if not os.path.exists(chat_logs_file):
        sample_chat_logs = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'username': ['강서준', '김보경', '조성우', '강서준', '김보경'],
            'club': ['코딩', '코딩', '코딩', '만들기', '만들기'],
            'message': [
                '안녕하세요!', '오늘 모임 재미있었어요', '다들 수고하셨습니다', '내일 활동 언제인가요?',
                '2시에 미술실에서 만나요'
            ],
            'timestamp': [
                '2025-01-20 14:00:00', '2025-01-20 14:05:00',
                '2025-01-20 14:10:00', '2025-01-21 15:00:00',
                '2025-01-21 15:05:00'
            ]
        })
        sample_chat_logs.to_csv(chat_logs_file,
                                index=False,
                                encoding='utf-8-sig')

    print("✅ 모든 데이터 파일이 성공적으로 초기화되었습니다!")


def create_logs_csv():
    """Create logs.csv with proper structure and sample data"""
    sample_logs = [{
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'username': 'system',
        'name': 'System',
        'role': 'System',
        'club_name': 'System',
        'ip_address': '127.0.0.1',
        'session_id': 'system_init',
        'activity_type': 'System',
        'activity_description': 'System initialized',
        'target_resource': 'System',
        'action_result': 'Success',
        'error_message': 'None',
        'user_agent': 'System',
        'device_type': 'Server',
        'browser_info': 'N/A',
        'request_method': 'INIT',
        'response_time': '0ms',
        'data_modified': 'Initial setup',
        'security_level': 'Normal',
        'notes': 'System initialization log'
    }]

    logs_df = pd.DataFrame(sample_logs)
    logs_df.to_csv('data/logs.csv', index=False, encoding='utf-8-sig')
    print("✅ logs.csv 생성 완료 (샘플 데이터 포함)")
