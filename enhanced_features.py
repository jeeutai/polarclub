import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import random
from error_handler import error_handler

class EnhancedFeatures:
    def __init__(self):
        pass
    
    def show_dashboard_widgets(self, user):
        """Display enhanced dashboard widgets"""
        
        # Quick stats widgets
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.show_today_schedule_widget(user)
        
        with col2:
            self.show_pending_tasks_widget(user)
        
        with col3:
            self.show_recent_notifications_widget(user)
        
        with col4:
            self.show_achievement_widget(user)
    
    def show_today_schedule_widget(self, user):
        """Today's schedule widget"""
        st.markdown("##### 📅 오늘 일정")
        
        schedules_df = st.session_state.data_manager.load_csv('schedules')
        today = datetime.now().strftime('%Y-%m-%d')
        
        today_schedules = schedules_df[
            schedules_df['date'].str.startswith(today)
        ] if not schedules_df.empty else pd.DataFrame()
        
        if today_schedules.empty:
            st.info("오늘 일정이 없습니다")
        else:
            for _, schedule in today_schedules.head(3).iterrows():
                st.markdown(f"• {schedule['title']}")
        
        if len(today_schedules) > 3:
            st.markdown(f"외 {len(today_schedules) - 3}건 더...")
    
    def show_pending_tasks_widget(self, user):
        """Pending tasks widget"""
        st.markdown("##### 📋 대기 중인 과제")
        
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        
        if assignments_df.empty:
            st.info("과제가 없습니다")
            return
        
        # Find pending assignments
        user_submissions = submissions_df[
            submissions_df['username'] == user['username']
        ]['assignment_id'].tolist() if not submissions_df.empty else []
        
        pending_assignments = assignments_df[
            ~assignments_df['id'].isin(user_submissions)
        ]
        
        if pending_assignments.empty:
            st.success("모든 과제 완료!")
        else:
            for _, assignment in pending_assignments.head(3).iterrows():
                due_date = pd.to_datetime(assignment['due_date'])
                days_left = (due_date - datetime.now()).days
                
                color = "🔴" if days_left < 1 else "🟡" if days_left < 3 else "🟢"
                st.markdown(f"{color} {assignment['title']} ({days_left}일 남음)")
    
    def show_recent_notifications_widget(self, user):
        """Recent notifications widget"""
        st.markdown("##### 🔔 최근 알림")
        
        notifications_df = st.session_state.data_manager.load_csv('notifications')
        
        if notifications_df.empty:
            st.info("알림이 없습니다")
            return
        
        # Check if recipient column exists, if not use a default filtering approach
        if 'recipient' in notifications_df.columns:
            user_notifications = notifications_df[
                (notifications_df['recipient'] == user['username']) |
                (notifications_df['recipient'] == 'all')
            ].sort_values('created_date', ascending=False)
        else:
            # Fallback if recipient column doesn't exist
            user_notifications = notifications_df.sort_values('created_date', ascending=False)
        
        for _, notif in user_notifications.head(3).iterrows():
            st.markdown(f"• {notif['title']}")
    
    def show_achievement_widget(self, user):
        """Achievement widget"""
        st.markdown("##### 🏆 최근 성과")
        
        user_points = st.session_state.gamification_system.calculate_user_points(user['username'])
        user_level = st.session_state.gamification_system.calculate_level(user_points)
        
        error_handler.wrap_streamlit_component(st.metric, "레벨", user_level)
        error_handler.wrap_streamlit_component(st.metric, "포인트", user_points)
        
        # Recent badges
        badges_df = st.session_state.data_manager.load_csv('badges')
        user_badges = badges_df[
            badges_df['username'] == user['username']
        ].sort_values('awarded_date', ascending=False) if not badges_df.empty else pd.DataFrame()
        
        if not user_badges.empty:
            latest_badge = user_badges.iloc[0]
            st.markdown(f"🏅 {latest_badge['badge_name']}")
    
    def show_advanced_analytics(self, user):
        """Advanced analytics dashboard"""
        st.markdown("### 📊 고급 분석")
        
        tabs = st.tabs(["📈 성과 트렌드", "📊 활동 패턴", "🎯 목표 달성", "📋 상세 리포트"])
        
        with tabs[0]:
            self.show_performance_trends(user)
        
        with tabs[1]:
            self.show_activity_patterns(user)
        
        with tabs[2]:
            self.show_goal_achievement(user)
        
        with tabs[3]:
            self.show_detailed_reports(user)
    
    def show_performance_trends(self, user):
        """Performance trends analysis"""
        st.markdown("#### 📈 성과 트렌드")
        
        # Get user data with error handling
        try:
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            if attendance_df.empty:
                st.info("분석할 데이터가 부족합니다.")
                return
                
            user_attendance = attendance_df[attendance_df['username'] == user['username']]
            
            if user_attendance.empty:
                st.info("분석할 데이터가 부족합니다.")
                return
        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
            return
        
        # Calculate weekly trends only if data exists
        if not user_attendance.empty and len(user_attendance) > 1:
            user_attendance['date'] = pd.to_datetime(user_attendance['date'])
            user_attendance['week'] = user_attendance['date'].dt.isocalendar().week
            
            weekly_stats = user_attendance.groupby('week').agg({
                'status': lambda x: (x == '출석').sum(),
                'date': 'count'
            }).rename(columns={'status': 'present_days', 'date': 'total_days'})
            
            weekly_stats['attendance_rate'] = weekly_stats['present_days'] / weekly_stats['total_days'] * 100
            
            # Display trend chart only if we have data
            if not weekly_stats.empty and len(weekly_stats) > 0:
                st.line_chart(weekly_stats['attendance_rate'])
                
                # Trend analysis
                if len(weekly_stats) > 1:
                    trend = "상승" if len(weekly_stats) > 1 and weekly_stats['attendance_rate'].iloc[-1] > weekly_stats['attendance_rate'].iloc[0] else "하락"
                    st.markdown(f"**트렌드:** {trend}")
        else:
            st.info("트렌드 분석을 위해 더 많은 데이터가 필요합니다.")
    
    def show_activity_patterns(self, user):
        """Activity patterns analysis"""
        st.markdown("#### 📊 활동 패턴")
        
        # Analyze activity by day of week
        logs_df = st.session_state.data_manager.load_csv('logs')
        user_logs = logs_df[logs_df['username'] == user['username']] if not logs_df.empty else pd.DataFrame()
        
        if user_logs.empty:
            st.info("활동 데이터가 없습니다.")
            return
        
        user_logs['timestamp'] = pd.to_datetime(user_logs['timestamp'])
        user_logs['day_of_week'] = user_logs['timestamp'].dt.day_name()
        user_logs['hour'] = user_logs['timestamp'].dt.hour
        
        # Day of week analysis
        if not user_logs.empty:
            daily_activity = user_logs['day_of_week'].value_counts()
            if not daily_activity.empty:
                st.bar_chart(daily_activity)
            
            # Peak activity hours
            hourly_activity = user_logs['hour'].value_counts().sort_index()
            if not hourly_activity.empty:
                peak_hour = hourly_activity.idxmax()
                st.markdown(f"**가장 활발한 시간:** {peak_hour}시")
        else:
            st.info("활동 패턴을 분석할 데이터가 없습니다.")
    
    def show_goal_achievement(self, user):
        """Goal achievement tracking"""
        st.markdown("#### 🎯 목표 달성률")
        
        # Monthly attendance goal
        monthly_goal = st.session_state.attendance_system.get_user_attendance_goal(user['username'])
        if monthly_goal:
            monthly_rate, streak_rate = st.session_state.attendance_system.get_goal_achievement_rate(
                user['username'], monthly_goal['monthly'], monthly_goal['streak']
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                error_handler.wrap_streamlit_component(st.metric, "월간 출석 목표", f"{monthly_rate:.1f}%")
                st.progress(monthly_rate / 100)
            
            with col2:
                error_handler.wrap_streamlit_component(st.metric, "연속 출석 목표", f"{streak_rate:.1f}%")
                st.progress(streak_rate / 100)
        
        # Assignment completion goal
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        
        if not assignments_df.empty:
            total_assignments = len(assignments_df)
            user_submissions = len(submissions_df[submissions_df['username'] == user['username']]) if not submissions_df.empty else 0
            completion_rate = (user_submissions / total_assignments * 100) if total_assignments > 0 else 0
            
            error_handler.wrap_streamlit_component(st.metric, "과제 완료율", f"{completion_rate:.1f}%")
            st.progress(completion_rate / 100)
    
    def show_detailed_reports(self, user):
        """Detailed reports"""
        st.markdown("#### 📋 상세 리포트")
        
        report_type = st.selectbox("리포트 유형", [
            "월간 활동 요약",
            "과제 성과 분석",
            "출석 패턴 리포트",
            "참여도 분석"
        ])
        
        if report_type == "월간 활동 요약":
            self.generate_monthly_summary(user)
        elif report_type == "과제 성과 분석":
            self.generate_assignment_report(user)
        elif report_type == "출석 패턴 리포트":
            self.generate_attendance_report(user)
        elif report_type == "참여도 분석":
            self.generate_participation_report(user)
    
    def generate_monthly_summary(self, user):
        """Generate monthly activity summary"""
        st.markdown("##### 📅 월간 활동 요약")
        
        # Current month data
        current_month = datetime.now().strftime('%Y-%m')
        
        # Attendance this month
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        month_attendance = attendance_df[
            (attendance_df['username'] == user['username']) &
            (attendance_df['date'].str.startswith(current_month))
        ] if not attendance_df.empty else pd.DataFrame()
        
        # Assignments this month
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        month_submissions = submissions_df[
            (submissions_df['username'] == user['username']) &
            (submissions_df['submitted_date'].str.startswith(current_month))
        ] if not submissions_df.empty else pd.DataFrame()
        
        # Posts this month
        posts_df = st.session_state.data_manager.load_csv('posts')
        month_posts = posts_df[
            (posts_df['author'] == user['username']) &
            (posts_df['created_date'].str.startswith(current_month))
        ] if not posts_df.empty else pd.DataFrame()
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            attendance_count = len(month_attendance[month_attendance['status'] == '출석'])
            error_handler.wrap_streamlit_component(st.metric, "이번 달 출석", attendance_count)
        
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "과제 제출", len(month_submissions))
        
        with col3:
            error_handler.wrap_streamlit_component(st.metric, "게시글 작성", len(month_posts))
        
        with col4:
            total_points = st.session_state.gamification_system.calculate_user_points(user['username'])
            error_handler.wrap_streamlit_component(st.metric, "누적 포인트", total_points)
    
    def generate_assignment_report(self, user):
        """Generate assignment performance report"""
        st.markdown("##### 📚 과제 성과 분석")
        
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        
        if assignments_df.empty:
            st.info("과제 데이터가 없습니다.")
            return
        
        user_submissions = submissions_df[
            submissions_df['username'] == user['username']
        ] if not submissions_df.empty else pd.DataFrame()
        
        # Calculate metrics
        total_assignments = len(assignments_df)
        submitted_assignments = len(user_submissions)
        completion_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        # On-time submissions
        on_time_count = 0
        for _, submission in user_submissions.iterrows():
            assignment = assignments_df[assignments_df['id'] == submission['assignment_id']]
            if not assignment.empty:
                due_date = pd.to_datetime(assignment.iloc[0]['due_date'])
                submit_date = pd.to_datetime(submission['submitted_date'])
                if submit_date <= due_date:
                    on_time_count += 1
        
        on_time_rate = (on_time_count / submitted_assignments * 100) if submitted_assignments > 0 else 0
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "완료율", f"{completion_rate:.1f}%")
        
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "제시간 제출률", f"{on_time_rate:.1f}%")
        
        with col3:
            avg_grade = user_submissions['grade'].mean() if 'grade' in user_submissions.columns and not user_submissions.empty else 0
            error_handler.wrap_streamlit_component(st.metric, "평균 점수", f"{avg_grade:.1f}")
    
    def generate_attendance_report(self, user):
        """Generate attendance pattern report"""
        st.markdown("##### ✅ 출석 패턴 리포트")
        
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[
            attendance_df['username'] == user['username']
        ] if not attendance_df.empty else pd.DataFrame()
        
        if user_attendance.empty:
            st.info("출석 데이터가 없습니다.")
            return
        
        # Convert date column and analyze patterns
        user_attendance['date'] = pd.to_datetime(user_attendance['date'])
        user_attendance['day_of_week'] = user_attendance['date'].dt.day_name()
        user_attendance['month'] = user_attendance['date'].dt.month
        
        # Day of week patterns
        st.markdown("**요일별 출석 패턴:**")
        present_attendance = user_attendance[user_attendance['status'] == '출석']
        if not present_attendance.empty and 'day_of_week' in present_attendance.columns:
            day_patterns = present_attendance['day_of_week'].value_counts()
            if len(day_patterns) > 0:
                st.bar_chart(day_patterns)
                
                # Best and worst days
                best_day = day_patterns.idxmax()
                worst_day = day_patterns.idxmin()
                st.markdown(f"**가장 출석률이 높은 요일:** {best_day}")
                st.markdown(f"**가장 출석률이 낮은 요일:** {worst_day}")
        
        # Monthly trends
        st.markdown("**월별 출석 트렌드:**")
        monthly_present = user_attendance[user_attendance['status'] == '출석']
        if not monthly_present.empty and 'month' in monthly_present.columns:
            monthly_attendance = monthly_present['month'].value_counts().sort_index()
            if len(monthly_attendance) > 0:
                st.line_chart(monthly_attendance)
        else:
            st.info("월별 트렌드를 분석할 데이터가 없습니다.")
    
    def generate_participation_report(self, user):
        """Generate participation analysis report"""
        st.markdown("##### 💬 참여도 분석")
        
        # Chat participation
        chat_df = st.session_state.data_manager.load_csv('chat_logs')
        user_chats = chat_df[
            chat_df['username'] == user['username']
        ] if not chat_df.empty else pd.DataFrame()
        
        # Post participation
        posts_df = st.session_state.data_manager.load_csv('posts')
        user_posts = posts_df[
            posts_df['author'] == user['username']
        ] if not posts_df.empty else pd.DataFrame()
        
        # Quiz participation
        quiz_responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_quiz_responses = quiz_responses_df[
            quiz_responses_df['username'] == user['username']
        ] if not quiz_responses_df.empty else pd.DataFrame()
        
        # Display participation metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "채팅 메시지", len(user_chats))
        
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "게시글 작성", len(user_posts))
        
        with col3:
            error_handler.wrap_streamlit_component(st.metric, "퀴즈 참여", len(user_quiz_responses))
        
        # Participation trends over time
        if not user_chats.empty:
            user_chats['timestamp'] = pd.to_datetime(user_chats['timestamp'])
            user_chats['date'] = user_chats['timestamp'].dt.date
            daily_chats = user_chats['date'].value_counts().sort_index()
            
            if not daily_chats.empty:
                st.markdown("**일별 채팅 활동:**")
                st.line_chart(daily_chats)
        else:
            st.info("채팅 활동 데이터가 없습니다.")
    
    def show_smart_recommendations(self, user):
        """Show smart recommendations based on user data"""
        st.markdown("### 🎯 맞춤 추천")
        
        recommendations = self.generate_recommendations(user)
        
        for rec in recommendations:
            rec_html = f"""
            <div style="background: linear-gradient(135deg, {rec['color']}, {rec['color']}aa); color: white; padding: 20px; border-radius: 12px; margin: 15px 0;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span style="font-size: 30px;">{rec['icon']}</span>
                    <div>
                        <h4 style="margin: 0;">{rec['title']}</h4>
                        <p style="margin: 5px 0; opacity: 0.9;">{rec['description']}</p>
                        <small style="opacity: 0.8;">{rec['reason']}</small>
                    </div>
                </div>
            </div>
            """
            st.markdown(rec_html, unsafe_allow_html=True)
    
    def generate_recommendations(self, user):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Analyze user patterns
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']] if not attendance_df.empty else pd.DataFrame()
        
        # Low attendance recommendation
        if not user_attendance.empty:
            recent_attendance = user_attendance.tail(7)
            attendance_rate = len(recent_attendance[recent_attendance['status'] == '출석']) / len(recent_attendance)
            
            if attendance_rate < 0.7:
                recommendations.append({
                    'title': '출석률 개선',
                    'description': '최근 출석률이 낮습니다. 일정을 확인하고 꾸준히 참석해보세요.',
                    'reason': f'최근 7일 출석률: {attendance_rate*100:.1f}%',
                    'icon': '📅',
                    'color': '#FF6B6B'
                })
        
        # Assignment submission recommendation
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        
        if not assignments_df.empty:
            pending_assignments = assignments_df[
                ~assignments_df['id'].isin(
                    submissions_df[submissions_df['username'] == user['username']]['assignment_id'].tolist()
                    if not submissions_df.empty else []
                )
            ]
            
            if len(pending_assignments) > 0:
                recommendations.append({
                    'title': '미제출 과제 확인',
                    'description': '제출하지 않은 과제가 있습니다. 마감일을 확인해보세요.',
                    'reason': f'{len(pending_assignments)}개의 미제출 과제',
                    'icon': '📚',
                    'color': '#4ECDC4'
                })
        
        # Participation recommendation
        chat_df = st.session_state.data_manager.load_csv('chat_logs')
        recent_chats = chat_df[
            (chat_df['username'] == user['username']) &
            (chat_df['timestamp'] >= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        ] if not chat_df.empty else pd.DataFrame()
        
        if len(recent_chats) < 5:
            recommendations.append({
                'title': '소통 늘리기',
                'description': '동아리 채팅방에서 더 많이 소통해보세요.',
                'reason': '최근 채팅 참여가 적습니다',
                'icon': '💬',
                'color': '#45B7D1'
            })
        
        # Gamification recommendation
        user_points = st.session_state.gamification_system.calculate_user_points(user['username'])
        if user_points < 100:
            recommendations.append({
                'title': '포인트 적립하기',
                'description': '다양한 활동으로 포인트를 적립하고 레벨을 올려보세요.',
                'reason': f'현재 포인트: {user_points}',
                'icon': '🎮',
                'color': '#96CEB4'
            })
        
        return recommendations