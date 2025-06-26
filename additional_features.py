import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class AdditionalFeatures:
    """Additional features to enhance the platform"""
    
    def __init__(self):
        pass
    
    def show_advanced_dashboard(self, user):
        """Advanced dashboard with charts and metrics"""
        st.markdown("### 📊 고급 대시보드")
        
        # Real-time metrics with error handling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Active users today
            try:
                logs_df = st.session_state.data_manager.load_csv('logs')
                today = datetime.now().strftime('%Y-%m-%d')
                if not logs_df.empty and 'timestamp' in logs_df.columns and 'username' in logs_df.columns:
                    today_users = logs_df[logs_df['timestamp'].str.startswith(today)]['username'].nunique()
                else:
                    today_users = 0
                error_handler.wrap_streamlit_component(st.metric, "🔥 오늘 활성 사용자", today_users, delta="+2")
            except Exception:
                error_handler.wrap_streamlit_component(st.metric, "🔥 오늘 활성 사용자", 0)
        
        with col2:
            # Total posts this week
            try:
                posts_df = st.session_state.data_manager.load_csv('posts')
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                if not posts_df.empty and 'created_date' in posts_df.columns:
                    week_posts = len(posts_df[posts_df['created_date'] >= week_ago])
                else:
                    week_posts = 0
                error_handler.wrap_streamlit_component(st.metric, "📝 이번 주 게시글", week_posts, delta="+5")
            except Exception:
                error_handler.wrap_streamlit_component(st.metric, "📝 이번 주 게시글", 0)
        
        with col3:
            # Pending assignments
            try:
                assignments_df = st.session_state.data_manager.load_csv('assignments')
                submissions_df = st.session_state.data_manager.load_csv('submissions')
                
                if not submissions_df.empty and 'username' in submissions_df.columns and 'assignment_id' in submissions_df.columns:
                    user_submissions = submissions_df[submissions_df['username'] == user['username']]['assignment_id'].tolist()
                else:
                    user_submissions = []
                    
                if not assignments_df.empty and 'id' in assignments_df.columns:
                    pending = len(assignments_df[~assignments_df['id'].isin(user_submissions)])
                else:
                    pending = 0
                    
                error_handler.wrap_streamlit_component(st.metric, "📚 미완료 과제", pending, delta="-1")
            except Exception:
                error_handler.wrap_streamlit_component(st.metric, "📚 미완료 과제", 0)
        
        with col4:
            # Attendance rate this month
            try:
                attendance_df = st.session_state.data_manager.load_csv('attendance')
                current_month = datetime.now().strftime('%Y-%m')
                
                if not attendance_df.empty and 'username' in attendance_df.columns and 'date' in attendance_df.columns and 'status' in attendance_df.columns:
                    month_attendance = attendance_df[
                        (attendance_df['username'] == user['username']) &
                        (attendance_df['date'].str.startswith(current_month))
                    ]
                    if not month_attendance.empty:
                        rate = len(month_attendance[month_attendance['status'] == '출석']) / len(month_attendance) * 100
                    else:
                        rate = 0
                else:
                    rate = 0
                    
                error_handler.wrap_streamlit_component(st.metric, "✅ 이번 달 출석률", f"{rate:.1f}%", delta="+5%")
            except Exception:
                error_handler.wrap_streamlit_component(st.metric, "✅ 이번 달 출석률", "0.0%")
        
        # Interactive charts
        if user['role'] == '선생님':
            self.show_admin_charts()
        else:
            self.show_student_charts(user)
    
    def show_admin_charts(self):
        """Admin-specific charts"""
        st.markdown("#### 📈 관리자 차트")
        
        # Club activity chart
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        if not attendance_df.empty:
            club_activity = attendance_df.groupby('club')['status'].apply(
                lambda x: (x == '출석').sum()
            ).reset_index()
            club_activity.columns = ['동아리', '출석 수']
            
            fig = px.bar(club_activity, x='동아리', y='출석 수', 
                        title='동아리별 출석 현황',
                        color='출석 수',
                        color_continuous_scale='viridis')
            error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
        
        # Daily activity trend
        logs_df = st.session_state.data_manager.load_csv('logs')
        if not logs_df.empty:
            logs_df['date'] = pd.to_datetime(logs_df['timestamp']).dt.date
            daily_activity = logs_df.groupby('date').size().reset_index()
            daily_activity.columns = ['날짜', '활동 수']
            
            fig = px.line(daily_activity, x='날짜', y='활동 수',
                         title='일별 시스템 활동 추이',
                         markers=True)
            error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
    
    def show_student_charts(self, user):
        """Student-specific charts"""
        st.markdown("#### 📊 내 활동 차트")
        
        # Personal attendance chart
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']] if not attendance_df.empty else pd.DataFrame()
        
        if not user_attendance.empty:
            status_counts = user_attendance['status'].value_counts()
            
            fig = px.pie(values=status_counts.values, names=status_counts.index,
                        title='내 출석 현황',
                        color_discrete_map={
                            '출석': '#28a745',
                            '지각': '#ffc107',
                            '결석': '#dc3545',
                            '조퇴': '#fd7e14'
                        })
            error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
        
        # Monthly activity heatmap
        logs_df = st.session_state.data_manager.load_csv('logs')
        user_logs = logs_df[logs_df['username'] == user['username']] if not logs_df.empty else pd.DataFrame()
        
        if not user_logs.empty:
            user_logs['timestamp'] = pd.to_datetime(user_logs['timestamp'])
            user_logs['hour'] = user_logs['timestamp'].dt.hour
            user_logs['day'] = user_logs['timestamp'].dt.day_name()
            
            heatmap_data = user_logs.groupby(['day', 'hour']).size().unstack(fill_value=0)
            
            fig = px.imshow(heatmap_data.values,
                           x=heatmap_data.columns,
                           y=heatmap_data.index,
                           title='활동 시간 히트맵',
                           color_continuous_scale='Blues')
            error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
    
    def show_quick_actions(self, user):
        """Quick action buttons"""
        st.markdown("### ⚡ 빠른 작업")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 새 게시글", use_container_width=True):
                st.session_state.redirect_to_board = True
                st.success("게시판으로 이동합니다!")
        
        with col2:
            if st.button("💬 채팅하기", use_container_width=True):
                st.session_state.redirect_to_chat = True
                st.success("채팅으로 이동합니다!")
        
        with col3:
            if st.button("📚 과제 확인", use_container_width=True):
                st.session_state.redirect_to_assignments = True
                st.success("과제탭으로 이동합니다!")
        
        with col4:
            if st.button("📅 일정 보기", use_container_width=True):
                st.session_state.redirect_to_schedule = True
                st.success("일정탭으로 이동합니다!")
    
    def show_weather_widget(self):
        """Weather widget simulation"""
        import random
        
        weather_options = [
            {"condition": "맑음", "icon": "☀️", "temp": "23°C"},
            {"condition": "흐림", "icon": "☁️", "temp": "20°C"},
            {"condition": "비", "icon": "🌧️", "temp": "18°C"},
            {"condition": "눈", "icon": "❄️", "temp": "2°C"}
        ]
        
        today_weather = random.choice(weather_options)
        
        st.markdown(f"""
        ##### 🌤️ 오늘 날씨
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #74b9ff, #0984e3); color: white; border-radius: 12px;">
            <div style="font-size: 40px;">{today_weather['icon']}</div>
            <div style="font-size: 18px; margin: 10px 0;">{today_weather['condition']}</div>
            <div style="font-size: 24px; font-weight: bold;">{today_weather['temp']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_inspirational_quote(self):
        """Daily inspirational quote"""
        quotes = [
            "성공은 준비와 기회가 만나는 곳에서 일어난다.",
            "배움에는 끝이 없다.",
            "오늘의 노력이 내일의 성과를 만든다.",
            "작은 변화가 큰 결과를 만든다.",
            "꿈을 이루는 첫 번째 단계는 꿈을 꾸는 것이다.",
            "실패는 성공의 어머니다.",
            "포기하지 않는 자가 승리한다."
        ]
        
        import random
        daily_quote = random.choice(quotes)
        
        st.markdown(f"""
        ##### 💡 오늘의 한마디
        <div style="background: linear-gradient(135deg, #a29bfe, #6c5ce7); color: white; padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-style: italic; font-size: 16px; line-height: 1.6;">
                "{daily_quote}"
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_club_spotlight(self, user):
        """Club spotlight section"""
        st.markdown("##### 🌟 동아리 스포트라이트")
        
        clubs_df = st.session_state.data_manager.load_csv('clubs')
        if clubs_df.empty:
            st.info("등록된 동아리가 없습니다.")
            return
        
        # Randomly select a club to spotlight
        import random
        featured_club = clubs_df.sample(1).iloc[0]
        
        # Get recent activity for this club
        posts_df = st.session_state.data_manager.load_csv('posts')
        club_posts = posts_df[posts_df['club'] == featured_club['name']] if not posts_df.empty else pd.DataFrame()
        
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        club_attendance = attendance_df[attendance_df['club'] == featured_club['name']] if not attendance_df.empty else pd.DataFrame()
        
        recent_activity = len(club_posts) + len(club_attendance)
        
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border-left: 6px solid #FF6B6B;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 40px;">{featured_club['icon']}</span>
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #333;">{featured_club['name']}</h4>
                    <p style="color: #666; margin: 5px 0;">{featured_club['description']}</p>
                    <div style="display: flex; gap: 15px; font-size: 14px; color: #888;">
                        <span>👑 회장: {featured_club['president']}</span>
                        <span>🎯 최근 활동: {recent_activity}회</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_achievements_showcase(self, user):
        """Recent achievements showcase"""
        st.markdown("##### 🏆 최근 성과")
        
        badges_df = st.session_state.data_manager.load_csv('badges')
        recent_badges = badges_df.sort_values('awarded_date', ascending=False).head(3) if not badges_df.empty else pd.DataFrame()
        
        if recent_badges.empty:
            st.info("최근 획득한 배지가 없습니다.")
            return
        
        for _, badge in recent_badges.iterrows():
            users_df = st.session_state.data_manager.load_csv('users')
            user_info = users_df[users_df['username'] == badge['username']]
            name = user_info.iloc[0]['name'] if not user_info.empty else badge['username']
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FFD700, #FFA500); color: white; padding: 15px; border-radius: 10px; margin: 8px 0;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px;">{badge['badge_icon']}</span>
                    <div>
                        <strong>{name}님이 '{badge['badge_name']}' 배지를 획득했습니다!</strong>
                        <div style="opacity: 0.9; font-size: 14px;">{badge['description']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def show_system_announcements(self):
        """System announcements"""
        st.markdown("##### 📢 시스템 공지")
        
        announcements = [
            {
                'title': '새로운 기능 업데이트',
                'content': '포트폴리오 시스템이 새롭게 추가되었습니다!',
                'type': 'info',
                'date': '2025-06-23'
            },
            {
                'title': '서버 점검 안내',
                'content': '매주 일요일 새벽 2시-4시 정기 점검이 있습니다.',
                'type': 'warning',
                'date': '2025-06-22'
            }
        ]
        
        for announcement in announcements:
            color = {
                'info': '#17a2b8',
                'warning': '#ffc107',
                'success': '#28a745',
                'error': '#dc3545'
            }.get(announcement['type'], '#6c757d')
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 4px solid {color};">
                <h5 style="margin: 0 0 5px 0; color: #333;">{announcement['title']}</h5>
                <p style="margin: 0; color: #666;">{announcement['content']}</p>
                <small style="color: #999;">📅 {announcement['date']}</small>
            </div>
            """, unsafe_allow_html=True)