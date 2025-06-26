import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from error_handler import error_handler

# Configure page
st.set_page_config(
    page_title="폴라리스반 동아리 관리 시스템",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize core systems first (without dependencies)
@st.cache_resource
def initialize_core_systems():
    """Initialize core systems without dependencies"""
    from auth import AuthManager
    from data_manager import DataManager
    from ui_components import UIComponents

    core_systems = {}
    core_systems['auth_manager'] = AuthManager()
    core_systems['data_manager'] = DataManager()
    core_systems['ui_components'] = UIComponents()

    return core_systems

# Initialize dependent systems
@st.cache_resource
def initialize_dependent_systems():
    """Initialize systems that depend on core systems"""
    from board_system import BoardSystem
    from chat_system import ChatSystem
    from assignment_system import AssignmentSystem
    from quiz_system import QuizSystem
    from attendance_system import AttendanceSystem
    from schedule_system import ScheduleSystem
    from report_generator import ReportGenerator
    from vote_system import VoteSystem

    from video_conference_system import VideoConferenceSystem
    from backup_system import BackupSystem
    from notification_system import NotificationSystem
    from search_system import SearchSystem
    from admin_system import AdminSystem
    from ai_assistant import AIAssistant
    from gamification_system import GamificationSystem
    from portfolio_system import PortfolioSystem
    from logging_system import LoggingSystem
    from enhanced_features import EnhancedFeatures
    from additional_features import AdditionalFeatures
    from deployment_features import DeploymentFeatures

    dependent_systems = {}
    dependent_systems['board_system'] = BoardSystem()
    dependent_systems['chat_system'] = ChatSystem()
    dependent_systems['assignment_system'] = AssignmentSystem()
    dependent_systems['quiz_system'] = QuizSystem()
    dependent_systems['attendance_system'] = AttendanceSystem()
    dependent_systems['schedule_system'] = ScheduleSystem()
    dependent_systems['report_generator'] = ReportGenerator()
    dependent_systems['vote_system'] = VoteSystem()

    dependent_systems['video_conference_system'] = VideoConferenceSystem()
    dependent_systems['backup_system'] = BackupSystem()
    dependent_systems['notification_system'] = NotificationSystem()
    dependent_systems['search_system'] = SearchSystem()
    dependent_systems['admin_system'] = AdminSystem()
    dependent_systems['ai_assistant'] = AIAssistant()
    dependent_systems['gamification_system'] = GamificationSystem()
    dependent_systems['portfolio_system'] = PortfolioSystem()
    dependent_systems['logging_system'] = LoggingSystem()
    dependent_systems['enhanced_features'] = EnhancedFeatures()
    dependent_systems['additional_features'] = AdditionalFeatures()
    dependent_systems['deployment_features'] = DeploymentFeatures()

    return dependent_systems

# Initialize systems in proper order
if 'core_systems_initialized' not in st.session_state:
    core_systems = initialize_core_systems()
    st.session_state.update(core_systems)
    st.session_state.core_systems_initialized = True

if 'dependent_systems_initialized' not in st.session_state:
    dependent_systems = initialize_dependent_systems()
    st.session_state.update(dependent_systems)
    st.session_state.dependent_systems_initialized = True

# Initialize sample data for deployment only once
if 'data_initialized' not in st.session_state:
    from initialize_data import initialize_all_data
    try:
        initialize_all_data()
        st.session_state.data_initialized = True

        # Initialize portfolio CSV after data is ready
        if hasattr(st.session_state, 'portfolio_system'):
            st.session_state.portfolio_system.initialize_portfolio_csv()

    except Exception as e:
        st.error(f"데이터 초기화 오류: {e}")

# Custom CSS for modern design
st.markdown("""
<style>
    .css-1d391kg, [data-testid="stSidebar"] {
        display: none !important;
    }

    .main > div {
        padding-top: 0.5rem;
        max-width: 100%;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8f9fa;
        padding: 4px;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: #6c757d;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 12px;
        min-width: 80px;
        transition: all 0.2s ease;
        border: none;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        color: #495057;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #FF6B6B;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        border-bottom: 3px solid #FF6B6B;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border-radius: 0 0 12px 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-top: 0;
    }

    .club-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6B6B;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .club-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    .status-active {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }

    .status-inactive {
        background-color: #6c757d;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }

    .achievement-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #000;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .progress-bar {
        background-color: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 20px;
        margin: 10px 0;
    }

    .progress-fill {
        background: linear-gradient(90deg, #28a745, #20c997);
        height: 100%;
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        font-weight: bold;
    }

    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 11px;
            padding: 0 8px;
            min-width: 60px;
        }

        .club-card {
            padding: 15px;
            margin: 10px 0;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check login status
    if 'user' not in st.session_state:
        show_login()
    else:
        try:
            show_main_app()
        except Exception as e:
            st.error(f"앱 실행 중 오류가 발생했습니다: {e}")
            st.error("상세 오류 정보는 개발자에게 문의하세요.")
            
            # 오류 로깅
            if hasattr(st.session_state, 'logging_system'):
                try:
                    st.session_state.logging_system.log_error(
                        st.session_state.get('user', {}).get('username', 'Unknown'),
                        'Application Error',
                        str(e),
                        'Main Application'
                    )
                except:
                    pass  # 로깅 실패해도 앱이 멈추지 않도록
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 새로고침"):
                    st.rerun()
            with col2:
                if st.button("🚪 다시 로그인"):
                    if 'user' in st.session_state:
                        del st.session_state.user
                    st.rerun()

def show_login():
    st.title("🌟 폴라리스반")
    st.subheader("동아리 관리 시스템")
    st.info("🎯 6학년 폴라리스반의 동아리 활동을 관리하는 통합 플랫폼")
    st.success("✨ 게시판, 과제, 퀴즈, 출석, 투표 등 모든 기능을 한 곳에서!")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔐 로그인")

        # Demo account buttons
        # st.markdown("#### ⚡ 빠른 로그인")
        # col_a, col_b, col_c = st.columns(3)

        # with col_a:
        #     if st.button("👨‍🏫 선생님", use_container_width=True):
        #         attempt_login('조성우', 'admin')

        # with col_b:
        #     if st.button("👨‍🎓 강서준", use_container_width=True):
        #         attempt_login('강서준', '1234')

        # with col_c:
        #     if st.button("👩‍🎓 김보경", use_container_width=True):
        #         attempt_login('김보경', '1234')

        st.divider()
        st.markdown("#### 🔑 직접 로그인")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 사용자명", placeholder="사용자명을 입력하세요")
            password = st.text_input("🔑 비밀번호", type="password", placeholder="비밀번호를 입력하세요")

            login_button = st.form_submit_button("🚀 로그인", use_container_width=True)

            # 로그인 처리
            if login_button and username and password:
                attempt_login(username, password)

def attempt_login(username, password):
    """로그인 시도 처리"""
    with st.spinner('로그인 중...'):
        try:
            user = st.session_state.auth_manager.login(username, password)
            if user:
                st.session_state.user = user

                # 성공한 로그인 로그 기록 (안전하게)
                try:
                    if hasattr(st.session_state, 'logging_system'):
                        st.session_state.logging_system.log_login(username, True)
                except Exception:
                    pass  # 로그 실패해도 로그인은 계속 진행

                # 환영 알림 추가
                if hasattr(st.session_state, 'notification_system'):
                    st.session_state.notification_system.add_notification(
                        f"{user['name']}님이 로그인했습니다.", "info", user['username']
                    )

                st.success(f"환영합니다, {user['name']}님!")
                st.rerun()
            else:
                # 실패한 로그인 로그 기록
                if hasattr(st.session_state, 'logging_system'):
                    st.session_state.logging_system.log_activity(
                        username, 'Authentication', 'Failed login attempt',
                        'Login System', 'Failed', 'Invalid credentials', 
                        security_level='High',
                        notes=f'Failed login attempt for username: {username}'
                    )
                st.error("❌ 사용자명 또는 비밀번호가 잘못되었습니다.")
        except Exception as e:
            st.error(f"로그인 중 오류가 발생했습니다: {e}")

def show_main_app():
    user = st.session_state.user

    # 페이지 접근 로그 기록
    if hasattr(st.session_state, 'logging_system'):
        st.session_state.logging_system.log_activity(
            user['username'], 'Page Access', 'Main application accessed',
            'Main App', 'Success',
            notes=f'User {user["name"]} accessed main application'
        )

    # Enhanced Header with user info
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        st.success(f"🌟 안녕하세요, {user['name']}님!")
        st.caption(f"역할: {user['role']} | 동아리: {user.get('club_name', '전체')}")

    with col2:
        # 현재 시간 표시
        current_time = datetime.now().strftime("%H:%M")
        error_handler.wrap_streamlit_component(st.metric, "🕐 현재 시간", current_time)

    with col3:
        # 알림 표시
        if hasattr(st.session_state, 'notification_system'):
            notifications = st.session_state.notification_system.get_user_notifications(user['username'])
            unread_count = len([n for n in notifications if not n.get('read', False)])
            if unread_count > 0:
                error_handler.wrap_streamlit_component(st.metric, "🔔 알림", f"{unread_count}개")
            else:
                error_handler.wrap_streamlit_component(st.metric, "🔔 알림", "없음")

    with col4:
        if st.button("🚪 로그아웃", use_container_width=True):
            # 로그아웃 로그 기록
            if hasattr(st.session_state, 'logging_system'):
                st.session_state.logging_system.log_activity(
                    user['username'], 'Authentication', 'User logged out',
                    'Login System', 'Success',
                    notes=f'User {user["name"]} logged out'
                )
            del st.session_state.user
            st.rerun()

    st.divider()

    # Define tab structure based on user role
    base_tabs = [
        "🏠 홈", "📝 게시판", "💬 채팅", "📚 과제", "🧠 퀴즈", 
        "📅 일정", "✅ 출석", "🗳️ 투표", "📹 화상회의", "🎮 게임화", 
        "📁 포트폴리오", "🤖 AI 도우미"
    ]



    if user['role'] == '선생님':
        tab_names = base_tabs + ["📊 보고서", "🔍 검색", "🔔 알림", "💾 백업", "📊 로그", "⚙️ 관리자", "🚀 고급기능"]
    elif user['role'] in ['회장', '부회장']:
        tab_names = base_tabs + ["📊 보고서", "🔍 검색", "🔔 알림", "📊 로그", "🚀 고급기능"]
    else:
        tab_names = base_tabs + ["🔍 검색", "🔔 알림", "🚀 고급기능"]

    tabs = st.tabs(tab_names)

    # Tab content mapping
    tab_index = 0

    # Base tabs (available to all users)
    with tabs[tab_index]:  # 홈
        show_home_dashboard(user)
    tab_index += 1

    with tabs[tab_index]:  # 게시판
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Board system accessed',
                'Board System', 'Success'
            )
        st.session_state.board_system.show_board_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 채팅
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Chat system accessed',
                'Chat System', 'Success'
            )
        st.session_state.chat_system.show_chat_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 과제
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Assignment system accessed',
                'Assignment System', 'Success'
            )
        st.session_state.assignment_system.show_assignment_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 퀴즈
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Quiz system accessed',
                'Quiz System', 'Success'
            )
        st.session_state.quiz_system.show_quiz_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 일정
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Schedule system accessed',
                'Schedule System', 'Success'
            )
        st.session_state.schedule_system.show_schedule_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 출석
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Attendance system accessed',
                'Attendance System', 'Success'
            )
        st.session_state.attendance_system.show_attendance_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 투표
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Vote system accessed',
                'Vote System', 'Success'
            )
        st.session_state.vote_system.show_vote_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 화상회의
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Video conference accessed',
                'Video Conference', 'Success'
            )
        st.session_state.video_conference_system.show_conference_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 게임화
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Gamification system accessed',
                'Gamification', 'Success'
            )
        st.session_state.gamification_system.show_gamification_interface(user)
    tab_index += 1

    with tabs[tab_index]:  # 포트폴리오
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Portfolio system accessed',
                'Portfolio', 'Success'
            )
        st.session_state.portfolio_system.show_portfolio_interface(user)
    tab_index += 1



    with tabs[tab_index]:  # AI 도우미
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'AI assistant accessed',
                'AI Assistant', 'Success'
            )
        st.session_state.ai_assistant.show_ai_interface(user)
    tab_index += 1

    # Role-specific tabs
    if user['role'] in ['선생님', '회장', '부회장']:
        with tabs[tab_index]:  # 보고서
            if hasattr(st.session_state, 'logging_system'):
                st.session_state.logging_system.log_activity(
                    user['username'], 'Page Access', 'Report generator accessed',
                    'Reports', 'Success'
                )
            st.session_state.report_generator.show_report_interface(user)
        tab_index += 1

    # Search tab
    with tabs[tab_index]:  # 검색
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Search system accessed',
                'Search', 'Success'
            )
        st.session_state.search_system.show_search_interface(user)
    tab_index += 1

    # Notification tab
    with tabs[tab_index]:  # 알림
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Notification system accessed',
                'Notifications', 'Success'
            )
        st.session_state.notification_system.show_notification_interface(user)
    tab_index += 1

    # Log access for higher roles
    if user['role'] in ['선생님', '회장', '부회장']:
        with tabs[tab_index]:  # 로그
            if hasattr(st.session_state, 'logging_system'):
                st.session_state.logging_system.log_activity(
                    user['username'], 'Page Access', 'Logging system accessed',
                    'Logs', 'Success', security_level='High'
                )
            st.session_state.logging_system.show_logs_interface(user)
        tab_index += 1

    # Teacher-only tabs
    if user['role'] == '선생님':
        with tabs[tab_index]:  # 백업
            if hasattr(st.session_state, 'logging_system'):
                st.session_state.logging_system.log_activity(
                    user['username'], 'Page Access', 'Backup system accessed',
                    'Backup', 'Success', security_level='High'
                )
            st.session_state.backup_system.show_backup_interface(user)
        tab_index += 1

        with tabs[tab_index]:  # 관리자
            if hasattr(st.session_state, 'logging_system'):
                st.session_state.logging_system.log_activity(
                    user['username'], 'Page Access', 'Admin system accessed',
                    'Admin Panel', 'Success', security_level='High'
                )
            st.session_state.admin_system.show_admin_interface(user)
        tab_index += 1

    # Enhanced features tab for all users
    with tabs[tab_index]:  # 고급기능
        if hasattr(st.session_state, 'logging_system'):
            st.session_state.logging_system.log_activity(
                user['username'], 'Page Access', 'Enhanced features accessed',
                'Enhanced Features', 'Success'
            )
        # Show both enhanced features and deployment features
        feature_tabs = st.tabs(["🚀 향상된 기능", "🌟 배포 기능"])
        
        with feature_tabs[0]:
            show_enhanced_features(user)
        
        with feature_tabs[1]:
            if hasattr(st.session_state, 'deployment_features'):
                st.session_state.deployment_features.show_deployment_dashboard(user)
            else:
                st.info("배포 기능을 준비 중입니다...")
    tab_index += 1

def show_home_dashboard(user):
    """Display enhanced home dashboard"""
    st.markdown(f"## 👋 안녕하세요, {user['name']}님!")

    # Quick stats with enhanced design
    col1, col2, col3, col4, col5 = st.columns(5)

    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])

    with col1:
        club_count = len(user_clubs) if not user_clubs.empty else 0
        error_handler.wrap_streamlit_component(st.metric, "🎯 가입 동아리", club_count, delta=f"+{club_count}")

    with col2:
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        pending_assignments = len(assignments_df[assignments_df['status'] == '활성']) if not assignments_df.empty else 0
        error_handler.wrap_streamlit_component(st.metric, "📚 진행 중 과제", pending_assignments)

    with col3:
        if hasattr(st.session_state, 'notification_system'):
            notifications = st.session_state.notification_system.get_user_notifications(user['username'])
            unread_count = len([n for n in notifications if not n.get('read', False)])
            error_handler.wrap_streamlit_component(st.metric, "🔔 읽지 않은 알림", unread_count)
        else:
            error_handler.wrap_streamlit_component(st.metric, "🔔 읽지 않은 알림", 0)

    with col4:
        badges_df = st.session_state.data_manager.load_csv('badges')
        user_badges = badges_df[badges_df['username'] == user['username']] if not badges_df.empty else pd.DataFrame()
        badge_count = len(user_badges)
        error_handler.wrap_streamlit_component(st.metric, "🏅 획득 배지", badge_count)

    with col5:
        posts_df = st.session_state.data_manager.load_csv('posts')
        user_posts = len(posts_df[posts_df['author'] == user['name']]) if not posts_df.empty else 0
        error_handler.wrap_streamlit_component(st.metric, "📝 내 게시글", user_posts)

    st.divider()

    # Enhanced dashboard with additional features
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 🎯 내 동아리 현황")
        if not user_clubs.empty:
            for _, club_info in user_clubs.iterrows():
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_detail = clubs_df[clubs_df['name'] == club_info['club_name']]

                if not club_detail.empty:
                    club = club_detail.iloc[0]

                    # 동아리별 활동 통계
                    club_posts = len(posts_df[posts_df['club'] == club['name']]) if not posts_df.empty else 0
                    club_assignments = len(assignments_df[assignments_df['club'] == club['name']]) if not assignments_df.empty else 0

                    with st.container():
                        st.subheader(f"{club['icon']} {club['name']}")
                        st.write(club['description'])

                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            error_handler.wrap_streamlit_component(st.metric, "게시글", club_posts)
                        with col_b:
                            error_handler.wrap_streamlit_component(st.metric, "과제", club_assignments)
                        with col_c:
                            error_handler.wrap_streamlit_component(st.metric, "내 역할", club_info['role'])

                    # 화상회의 링크
                    meet_link_value = club.get('meet_link', '')
                    if pd.notna(meet_link_value) and meet_link_value and meet_link_value.strip():
                        st.link_button(f"🎥 {club['name']} 화상회의 참여", meet_link_value, use_container_width=True)
        else:
            st.info("가입된 동아리가 없습니다.")

    with col2:
        st.markdown("#### 📢 최근 알림")
        if hasattr(st.session_state, 'notification_system'):
            notifications = st.session_state.notification_system.get_user_notifications(user['username'])
            recent_notifications = notifications[:5] if notifications else []

            if recent_notifications:
                for notification in recent_notifications:
                    read_status = "✅" if notification.get('read', False) else "🔴"
                    notification_type = notification.get('type', 'info')

                    # 알림 타입별 아이콘
                    type_icons = {'info': '💬', 'warning': '⚠️', 'success': '✅', 'error': '❌'}
                    icon = type_icons.get(notification_type, '📢')

                    with st.container():
                        status_color = "normal" if notification.get('read', False) else "inverse"
                        st.write(f"{read_status} {icon} **{notification['title']}**")
                        st.caption(notification['created_date'])
            else:
                st.info("새로운 알림이 없습니다.")
        else:
            st.info("알림 시스템을 로드할 수 없습니다.")

        # 오늘의 일정
        st.markdown("#### 📅 오늘의 일정")
        schedules_df = st.session_state.data_manager.load_csv('schedules')
        today = date.today().strftime('%Y-%m-%d')

        if not schedules_df.empty:
            today_schedules = schedules_df[schedules_df['date'] == today]
            if not today_schedules.empty:
                for _, schedule in today_schedules.iterrows():
                    with st.container():
                        st.write(f"**📍 {schedule['title']}**")
                        st.caption(f"🕐 {schedule['time']} | 📍 {schedule['location']}")
            else:
                st.info("오늘 예정된 일정이 없습니다.")
        else:
            st.info("등록된 일정이 없습니다.")

def show_enhanced_features(user):
    """Display enhanced features"""
    st.markdown("### 🚀 고급 기능")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 대시보드", "🎯 목표 설정", "📈 성과 분석", "🔧 개인 설정"])

    with tab1:
        show_advanced_dashboard(user)

    with tab2:
        show_goal_setting(user)

    with tab3:
        show_performance_analytics(user)

    with tab4:
        show_personal_settings(user)

def show_advanced_dashboard(user):
    """Advanced dashboard with charts and analytics"""
    st.markdown("#### 📊 고급 대시보드")

    # 활동 차트
    posts_df = st.session_state.data_manager.load_csv('posts')
    assignments_df = st.session_state.data_manager.load_csv('assignments')

    if not posts_df.empty:
        # 월별 활동 통계
        posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
        monthly_posts = posts_df.groupby(posts_df['created_date'].dt.strftime('%Y-%m')).size()

        if not monthly_posts.empty:
            st.markdown("##### 📈 월별 게시글 현황")
            st.bar_chart(monthly_posts)

    # 동아리별 활동 비교
    if not posts_df.empty:
        club_activity = posts_df['club'].value_counts()
        st.markdown("##### 🏆 동아리별 활동 순위")
        st.bar_chart(club_activity)

def show_goal_setting(user):
    """Goal setting interface"""
    st.markdown("#### 🎯 개인 목표 설정")

    with st.form("goal_setting"):
        st.markdown("##### 이번 달 목표")

        col1, col2 = st.columns(2)
        with col1:
            post_goal = st.number_input("📝 게시글 작성 목표", min_value=0, max_value=50, value=5, key="post_goal")
            assignment_goal = st.number_input("📚 과제 완료 목표", min_value=0, max_value=20, value=3, key="assignment_goal")

        with col2:
            attendance_goal = st.number_input("✅ 출석 목표 (%)", min_value=0, max_value=100, value=90, key="attendance_goal")
            quiz_goal = st.number_input("🧠 퀴즈 참여 목표", min_value=0, max_value=10, value=2, key="quiz_goal")

        goal_note = st.text_area("📝 목표 메모", placeholder="이번 달 달성하고 싶은 목표나 다짐을 적어보세요", key="goal_note")

        if st.form_submit_button("🎯 목표 설정", use_container_width=True):
            # 목표 저장 로직
            st.success("목표가 설정되었습니다!")

def show_performance_analytics(user):
    """Performance analytics"""
    st.markdown("#### 📈 성과 분석")

    # 사용자별 통계
    posts_df = st.session_state.data_manager.load_csv('posts')
    user_posts = posts_df[posts_df['author'] == user['name']] if not posts_df.empty else pd.DataFrame()

    col1, col2, col3 = st.columns(3)

    with col1:
        error_handler.wrap_streamlit_component(st.metric, "📝 총 게시글", len(user_posts))

    with col2:
        total_likes = user_posts['likes'].sum() if not user_posts.empty and 'likes' in user_posts.columns else 0
        error_handler.wrap_streamlit_component(st.metric, "❤️ 받은 좋아요", int(total_likes))

    with col3:
        badges_df = st.session_state.data_manager.load_csv('badges')
        user_badges = badges_df[badges_df['username'] == user['username']] if not badges_df.empty else pd.DataFrame()
        error_handler.wrap_streamlit_component(st.metric, "🏅 획득 배지", len(user_badges))

    # 성과 트렌드
    if not user_posts.empty:
        st.markdown("##### 📊 활동 트렌드")
        user_posts['created_date'] = pd.to_datetime(user_posts['created_date'])
        daily_posts = user_posts.groupby(user_posts['created_date'].dt.date).size()
        st.line_chart(daily_posts)

def show_personal_settings(user):
    """Personal settings"""
    st.markdown("#### 🔧 개인 설정")

    with st.form("personal_settings"):
        st.markdown("##### 알림 설정")

        email_notifications = st.checkbox("📧 이메일 알림 받기", value=True, key="email_notifications")
        browser_notifications = st.checkbox("🔔 브라우저 알림 받기", value=True, key="browser_notifications")
        daily_summary = st.checkbox("📊 일일 요약 받기", value=False, key="daily_summary")

        st.markdown("##### 표시 설정")

        theme = st.selectbox("🎨 테마 선택", ["기본", "다크", "컬러풀"], key="theme_select")
        language = st.selectbox("🌍 언어 설정", ["한국어", "English"], key="language_select")

        st.markdown("##### 개인정보")

        display_name = st.text_input("👤 표시 이름", value=user['name'], key="display_name")
        bio = st.text_area("📝 자기소개", placeholder="간단한 자기소개를 작성해보세요", key="bio")

        if st.form_submit_button("💾 설정 저장", use_container_width=True):
            st.success("설정이 저장되었습니다!")

if __name__ == "__main__":
    main()