import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

class GamificationSystem:
    def __init__(self):
        self.point_values = {
            '출석': 10,
            '과제제출': 20,
            '게시글작성': 5,
            '댓글작성': 2,
            '퀴즈참여': 15,
            '투표참여': 5,
            '회의참석': 25,
            '우수활동': 50
        }
        
        self.badges = {
            '출석왕': {'condition': '출석', 'threshold': 30, 'icon': '👑', 'description': '30일 연속 출석'},
            '과제마스터': {'condition': '과제제출', 'threshold': 10, 'icon': '📚', 'description': '과제 10개 완료'},
            '소통왕': {'condition': '댓글작성', 'threshold': 50, 'icon': '💬', 'description': '댓글 50개 작성'},
            '퀴즈킹': {'condition': '퀴즈참여', 'threshold': 20, 'icon': '🧠', 'description': '퀴즈 20회 참여'},
            '리더': {'condition': '우수활동', 'threshold': 5, 'icon': '⭐', 'description': '우수활동 5회 인정'},
            '활동가': {'condition': '종합점수', 'threshold': 1000, 'icon': '🔥', 'description': '총 1000점 달성'},
            '창작자': {'condition': '게시글작성', 'threshold': 5, 'icon': '🎨', 'description': '첫 포트폴리오 등록'},
            '탐험가': {'condition': '검색', 'threshold': 50, 'icon': '🔍', 'description': '검색 50회 수행'},
            '스피드러너': {'condition': '빠른완료', 'threshold': 10, 'icon': '⚡', 'description': '과제 빠른 제출 10회'},
            '완벽주의자': {'condition': '완벽점수', 'threshold': 5, 'icon': '💯', 'description': '퀴즈 만점 5회'}
        }

    def show_gamification_interface(self, user):
        """Display gamification dashboard"""
        st.markdown("### 🎮 게임화 시스템")
        
        tabs = st.tabs(["🏆 내 현황", "🏅 배지", "📊 랭킹", "🎯 미션", "🎮 게임", "🏪 상점"])
        
        with tabs[0]:
            self.show_user_stats(user)
        
        with tabs[1]:
            self.show_badges_system(user)
        
        with tabs[2]:
            self.show_rankings(user)
        
        with tabs[3]:
            self.show_missions(user)
        
        with tabs[4]:
            self.show_games(user)
        
        with tabs[5]:
            self.show_point_shop(user)
    
    def show_user_stats(self, user):
        """Display user's gamification stats"""
        st.markdown("#### 🎯 내 게임 현황")
        
        # Calculate user points
        user_points = self.calculate_user_points(user['username'])
        user_level = self.calculate_level(user_points)
        points_to_next = self.points_to_next_level(user_points)
        
        # Stats dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "총 포인트", user_points, delta=f"+{self.get_daily_points(user['username'])}")
        
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "레벨", user_level, delta="📈")
        
        with col3:
            error_handler.wrap_streamlit_component(st.metric, "다음 레벨까지", points_to_next, delta="🎯")
        
        with col4:
            user_badges = self.get_user_badges(user['username'])
            error_handler.wrap_streamlit_component(st.metric, "보유 배지", len(user_badges), delta="🏅")
        
        # Progress bar for next level
        current_level_points = self.get_level_points(user_level)
        next_level_points = self.get_level_points(user_level + 1)
        progress = (user_points - current_level_points) / (next_level_points - current_level_points)
        
        st.progress(min(progress, 1.0))
        st.markdown(f"**레벨 {user_level + 1}까지 {points_to_next}포인트 필요**")
        
        # Recent activities
        st.markdown("#### 📈 최근 활동")
        recent_activities = self.get_recent_activities(user['username'])
        
        for activity in recent_activities[:5]:
            activity_html = f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 4px solid #FF6B6B;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{activity['type']}</strong>
                        <div style="color: #666; font-size: 14px;">{activity['description']}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #28a745; font-weight: bold;">+{activity['points']}</span>
                        <div style="color: #999; font-size: 12px;">{activity['date']}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(activity_html, unsafe_allow_html=True)
    
    def show_badges_system(self, user):
        """Display badges system"""
        st.markdown("#### 🏅 배지 컬렉션")
        
        user_badges = self.get_user_badges(user['username'])
        user_stats = self.get_user_activity_stats(user['username'])
        
        # Display badges in grid
        cols = st.columns(3)
        
        for i, (badge_name, badge_info) in enumerate(self.badges.items()):
            col = cols[i % 3]
            
            with col:
                # Check if user has this badge
                has_badge = badge_name in [b['badge_name'] for b in user_badges]
                
                # Calculate progress
                if badge_info['condition'] == '종합점수':
                    current_value = self.calculate_user_points(user['username'])
                else:
                    current_value = user_stats.get(badge_info['condition'], 0)
                
                progress = min(current_value / badge_info['threshold'], 1.0)
                
                # Badge styling
                if has_badge:
                    badge_style = "background: linear-gradient(135deg, #FFD700, #FFA500); color: white;"
                else:
                    badge_style = "background: #f8f9fa; color: #6c757d;"
                
                badge_html = f"""
                <div style="{badge_style} padding: 20px; border-radius: 12px; text-align: center; margin: 10px 0;">
                    <div style="font-size: 40px; margin-bottom: 10px;">{badge_info['icon']}</div>
                    <h4 style="margin: 5px 0;">{badge_name}</h4>
                    <p style="font-size: 12px; margin: 5px 0;">{badge_info['description']}</p>
                    <div style="margin-top: 10px;">
                        <div style="background: rgba(255,255,255,0.3); border-radius: 10px; height: 8px;">
                            <div style="background: {'#28a745' if has_badge else '#FF6B6B'}; height: 8px; border-radius: 10px; width: {progress * 100}%;"></div>
                        </div>
                        <small>{current_value}/{badge_info['threshold']}</small>
                    </div>
                </div>
                """
                st.markdown(badge_html, unsafe_allow_html=True)
    
    def show_rankings(self, user):
        """Display user rankings"""
        st.markdown("#### 📊 동아리 랭킹")
        
        # Get all users and their points
        users_df = st.session_state.data_manager.load_csv('users')
        rankings = []
        
        for _, user_row in users_df.iterrows():
            points = self.calculate_user_points(user_row['username'])
            level = self.calculate_level(points)
            badges_count = len(self.get_user_badges(user_row['username']))
            
            rankings.append({
                'username': user_row['username'],
                'name': user_row['name'],
                'club': user_row['club_name'],
                'points': points,
                'level': level,
                'badges': badges_count
            })
        
        # Sort by points
        rankings.sort(key=lambda x: x['points'], reverse=True)
        
        # Display top 10
        st.markdown("##### 🏆 전체 랭킹 (상위 10명)")
        
        for i, rank_user in enumerate(rankings[:10]):
            rank = i + 1
            is_current_user = rank_user['username'] == user['username']
            
            # Rank styling
            if rank == 1:
                rank_icon = "🥇"
                rank_color = "#FFD700"
            elif rank == 2:
                rank_icon = "🥈"
                rank_color = "#C0C0C0"
            elif rank == 3:
                rank_icon = "🥉"
                rank_color = "#CD7F32"
            else:
                rank_icon = f"{rank}"
                rank_color = "#6c757d"
            
            background = "background: linear-gradient(135deg, #FF6B6B, #ff8a80);" if is_current_user else "background: white;"
            
            rank_html = f"""
            <div style="{background} padding: 15px; border-radius: 10px; margin: 8px 0; border: {'2px solid #FF6B6B' if is_current_user else '1px solid #dee2e6'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="background: {rank_color}; color: white; padding: 8px 12px; border-radius: 50%; font-weight: bold;">{rank_icon}</span>
                        <div>
                            <strong style="color: {'white' if is_current_user else '#333'};">{rank_user['name']}</strong>
                            <div style="color: {'rgba(255,255,255,0.8)' if is_current_user else '#666'}; font-size: 14px;">{rank_user['club']}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {'white' if is_current_user else '#28a745'}; font-weight: bold;">{rank_user['points']}pt</div>
                        <div style="color: {'rgba(255,255,255,0.8)' if is_current_user else '#666'}; font-size: 12px;">Lv.{rank_user['level']} | 🏅{rank_user['badges']}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(rank_html, unsafe_allow_html=True)
    
    def show_missions(self, user):
        """Display daily/weekly missions"""
        st.markdown("#### 🎯 데일리 미션")
        
        daily_missions = self.get_daily_missions(user['username'])
        
        for mission in daily_missions:
            progress = mission['current'] / mission['target']
            completed = progress >= 1.0
            
            mission_style = "background: linear-gradient(135deg, #28a745, #20c997);" if completed else "background: white;"
            
            mission_html = f"""
            <div style="{mission_style} padding: 20px; border-radius: 12px; margin: 15px 0; border: 1px solid {'#28a745' if completed else '#dee2e6'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: {'white' if completed else '#333'};">{mission['icon']} {mission['title']}</h4>
                        <p style="color: {'rgba(255,255,255,0.8)' if completed else '#666'}; margin: 5px 0;">{mission['description']}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {'rgba(255,255,255,0.2)' if completed else '#FF6B6B'}; color: {'white' if completed else 'white'}; padding: 6px 12px; border-radius: 15px; font-size: 14px;">
                            +{mission['reward']}pt
                        </span>
                    </div>
                </div>
                <div style="margin-top: 15px;">
                    <div style="background: {'rgba(255,255,255,0.3)' if completed else '#f8f9fa'}; border-radius: 10px; height: 10px;">
                        <div style="background: {'white' if completed else '#FF6B6B'}; height: 10px; border-radius: 10px; width: {min(progress * 100, 100)}%;"></div>
                    </div>
                    <small style="color: {'rgba(255,255,255,0.8)' if completed else '#666'};">{mission['current']}/{mission['target']} {'✅ 완료!' if completed else ''}</small>
                </div>
            </div>
            """
            st.markdown(mission_html, unsafe_allow_html=True)
    
    def calculate_user_points(self, username):
        """Calculate total points for a user"""
        # Get attendance points
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == username]
        attendance_points = len(user_attendance[user_attendance['status'] == '출석']) * self.point_values['출석']
        
        # Get assignment points
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        user_submissions = submissions_df[submissions_df['username'] == username]
        assignment_points = len(user_submissions) * self.point_values['과제제출']
        
        # Get post points
        posts_df = st.session_state.data_manager.load_csv('posts')
        user_posts = posts_df[posts_df['author'] == username] if not posts_df.empty else pd.DataFrame()
        post_points = len(user_posts) * self.point_values['게시글작성']
        
        # Get quiz points
        quiz_responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_quizzes = quiz_responses_df[quiz_responses_df['username'] == username] if not quiz_responses_df.empty else pd.DataFrame()
        quiz_points = len(user_quizzes) * self.point_values['퀴즈참여']
        
        return attendance_points + assignment_points + post_points + quiz_points
    
    def calculate_level(self, points):
        """Calculate user level based on points"""
        return points // 100 + 1
    
    def points_to_next_level(self, points):
        """Calculate points needed for next level"""
        current_level = self.calculate_level(points)
        next_level_points = current_level * 100
        return next_level_points - points
    
    def get_level_points(self, level):
        """Get minimum points required for a level"""
        return (level - 1) * 100
    
    def get_user_badges(self, username):
        """Get badges earned by user"""
        badges_df = st.session_state.data_manager.load_csv('badges')
        return badges_df[badges_df['username'] == username].to_dict('records') if not badges_df.empty else []
    
    def get_user_activity_stats(self, username):
        """Get user activity statistics"""
        stats = {}
        
        # Attendance count
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        stats['출석'] = len(attendance_df[(attendance_df['username'] == username) & (attendance_df['status'] == '출석')])
        
        # Assignment submissions
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        stats['과제제출'] = len(submissions_df[submissions_df['username'] == username])
        
        # Posts
        posts_df = st.session_state.data_manager.load_csv('posts')
        stats['게시글작성'] = len(posts_df[posts_df['author'] == username]) if not posts_df.empty else 0
        
        # Quiz participation
        quiz_responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        stats['퀴즈참여'] = len(quiz_responses_df[quiz_responses_df['username'] == username]) if not quiz_responses_df.empty else 0
        
        return stats
    
    def get_daily_points(self, username):
        """Get points earned today"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Today's attendance
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        today_attendance = attendance_df[
            (attendance_df['username'] == username) & 
            (attendance_df['date'] == today) & 
            (attendance_df['status'] == '출석')
        ]
        
        return len(today_attendance) * self.point_values['출석']
    
    def get_recent_activities(self, username):
        """Get recent user activities"""
        activities = []
        
        # Recent attendance
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == username].tail(5)
        
        for _, record in user_attendance.iterrows():
            if record['status'] == '출석':
                activities.append({
                    'type': '출석',
                    'description': f"{record['club']} 동아리 출석",
                    'points': self.point_values['출석'],
                    'date': record['date']
                })
        
        return sorted(activities, key=lambda x: x['date'], reverse=True)
    
    def get_daily_missions(self, username):
        """Get daily missions for user"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        missions = [
            {
                'icon': '📚',
                'title': '과제 제출하기',
                'description': '오늘 과제를 제출하세요',
                'target': 1,
                'current': self.get_today_submissions(username),
                'reward': 20
            },
            {
                'icon': '✅',
                'title': '출석 체크',
                'description': '동아리 활동에 참석하세요',
                'target': 1,
                'current': self.get_today_attendance(username),
                'reward': 10
            },
            {
                'icon': '💬',
                'title': '채팅 참여',
                'description': '동아리 채팅방에 메시지를 남기세요',
                'target': 3,
                'current': self.get_today_messages(username),
                'reward': 5
            }
        ]
        
        return missions
    
    def get_today_submissions(self, username):
        """Get today's submissions count"""
        today = datetime.now().strftime('%Y-%m-%d')
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        today_submissions = submissions_df[
            (submissions_df['username'] == username) & 
            (submissions_df['submitted_date'].str.startswith(today))
        ] if not submissions_df.empty else pd.DataFrame()
        return len(today_submissions)
    
    def get_today_attendance(self, username):
        """Get today's attendance status"""
        today = datetime.now().strftime('%Y-%m-%d')
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        today_attendance = attendance_df[
            (attendance_df['username'] == username) & 
            (attendance_df['date'] == today) & 
            (attendance_df['status'] == '출석')
        ]
        return len(today_attendance)
    
    def get_today_messages(self, username):
        """Get today's chat messages count"""
        today = datetime.now().strftime('%Y-%m-%d')
        chat_df = st.session_state.data_manager.load_csv('chat_logs')
        today_messages = chat_df[
            (chat_df['username'] == username) & 
            (chat_df['timestamp'].str.startswith(today))
        ] if not chat_df.empty else pd.DataFrame()
        return len(today_messages)
    
    def award_badge(self, username, badge_name):
        """Award a badge to user"""
        if badge_name in self.badges:
            badge_data = {
                'username': username,
                'badge_name': badge_name,
                'badge_icon': self.badges[badge_name]['icon'],
                'description': self.badges[badge_name]['description'],
                'awarded_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'awarded_by': 'System'
            }
            
            return st.session_state.data_manager.add_record('badges', badge_data)
        return False
    
    def check_and_award_badges(self, username):
        """Check and award eligible badges"""
        user_stats = self.get_user_activity_stats(username)
        current_badges = [b['badge_name'] for b in self.get_user_badges(username)]
        user_points = self.calculate_user_points(username)
        
        for badge_name, badge_info in self.badges.items():
            if badge_name not in current_badges:
                if badge_info['condition'] == '종합점수':
                    current_value = user_points
                else:
                    current_value = user_stats.get(badge_info['condition'], 0)
                
                if current_value >= badge_info['threshold']:
                    self.award_badge(username, badge_name)
                    return badge_name
        
        return None
    
    def show_games(self, user):
        """Display mini-games and interactive features"""
        st.markdown("#### 🎮 미니 게임")
        
        games = [
            {
                'name': '출석 빙고',
                'description': '일주일 연속 출석으로 빙고를 완성하세요!',
                'icon': '🎯',
                'reward': 50,
                'type': 'bingo'
            },
            {
                'name': '지식 퀴즈 러시',
                'description': '5분 안에 최대한 많은 퀴즈를 풀어보세요!',
                'icon': '⚡',
                'reward': 30,
                'type': 'quiz_rush'
            },
            {
                'name': '포인트 룰렛',
                'description': '포인트를 걸고 룰렛을 돌려보세요!',
                'icon': '🎰',
                'reward': '???',
                'type': 'roulette'
            }
        ]
        
        for game in games:
            game_html = f"""
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 12px; margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 30px;">{game['icon']}</span>
                            {game['name']}
                        </h3>
                        <p style="margin: 10px 0; opacity: 0.9;">{game['description']}</p>
                        <div style="background: rgba(255,255,255,0.2); padding: 8px 12px; border-radius: 15px; display: inline-block;">
                            보상: {game['reward']}pt
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(game_html, unsafe_allow_html=True)
            
            if st.button(f"🎮 {game['name']} 플레이", key=f"play_{game['type']}"):
                if game['type'] == 'bingo':
                    self.show_attendance_bingo(user)
                elif game['type'] == 'quiz_rush':
                    self.show_quiz_rush(user)
                elif game['type'] == 'roulette':
                    self.show_point_roulette(user)
    
    def show_point_shop(self, user):
        """Display point shop for rewards"""
        st.markdown("#### 🏪 포인트 상점")
        
        user_points = self.calculate_user_points(user['username'])
        error_handler.wrap_streamlit_component(st.metric, "보유 포인트", user_points)
        
        shop_items = [
            {
                'name': '출석 면제권',
                'description': '하루 결석을 출석으로 변경할 수 있습니다',
                'cost': 100,
                'icon': '🎫',
                'type': 'attendance_pass'
            },
            {
                'name': '과제 연장권',
                'description': '과제 마감일을 3일 연장할 수 있습니다',
                'cost': 150,
                'icon': '📅',
                'type': 'deadline_extension'
            },
            {
                'name': '퀴즈 재도전권',
                'description': '퀴즈를 한 번 더 도전할 수 있습니다',
                'cost': 80,
                'icon': '🔄',
                'type': 'quiz_retry'
            },
            {
                'name': '특별 배지',
                'description': '한정판 특별 배지를 획득합니다',
                'cost': 500,
                'icon': '🏆',
                'type': 'special_badge'
            }
        ]
        
        for item in shop_items:
            can_afford = user_points >= item['cost']
            
            item_html = f"""
            <div style="background: {'white' if can_afford else '#f8f9fa'}; padding: 20px; border-radius: 12px; margin: 15px 0; border: 1px solid {'#28a745' if can_afford else '#dee2e6'}; opacity: {'1' if can_afford else '0.6'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; display: flex; align-items: center; gap: 10px; color: {'#333' if can_afford else '#666'};">
                            <span style="font-size: 30px;">{item['icon']}</span>
                            {item['name']}
                        </h4>
                        <p style="color: {'#666' if can_afford else '#999'}; margin: 10px 0;">{item['description']}</p>
                    </div>
                    <div style="text-align: right;">
                        <div style="background: {'#28a745' if can_afford else '#6c757d'}; color: white; padding: 8px 15px; border-radius: 15px; font-weight: bold;">
                            {item['cost']}pt
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(item_html, unsafe_allow_html=True)
            
            if can_afford:
                if st.button(f"💰 구매", key=f"buy_{item['type']}"):
                    if self.purchase_item(user['username'], item):
                        st.success(f"{item['name']}을(를) 구매했습니다!")
                        st.rerun()
            else:
                st.button(f"💸 포인트 부족", key=f"cannot_buy_{item['type']}", disabled=True)
    
    def show_attendance_bingo(self, user):
        """Show attendance bingo game"""
        st.markdown("##### 🎯 출석 빙고")
        
        # Get last 7 days attendance
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']]
        
        # Create bingo grid
        bingo_grid = []
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            date_str = date.strftime('%Y-%m-%d')
            day_attendance = user_attendance[user_attendance['date'] == date_str]
            is_present = not day_attendance.empty and day_attendance.iloc[0]['status'] == '출석'
            
            bingo_grid.append({
                'date': date.strftime('%m/%d'),
                'day': date.strftime('%a'),
                'present': is_present
            })
        
        # Display bingo grid
        cols = st.columns(7)
        for i, day in enumerate(bingo_grid):
            with cols[i]:
                color = '#28a745' if day['present'] else '#dee2e6'
                icon = '✅' if day['present'] else '❌'
                
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 15px; border-radius: 10px; text-align: center; margin: 5px 0;">
                    <div style="font-size: 20px;">{icon}</div>
                    <div style="font-weight: bold;">{day['day']}</div>
                    <div style="font-size: 12px;">{day['date']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Check for bingo
        present_days = sum(1 for day in bingo_grid if day['present'])
        if present_days == 7:
            st.success("🎉 빙고! 일주일 연속 출석을 달성했습니다!")
            if st.button("🎁 보상 받기"):
                # Award points
                points_df = st.session_state.data_manager.load_csv('points')
                st.success("50포인트를 획득했습니다!")
        
        st.progress(present_days / 7)
        st.markdown(f"진행률: {present_days}/7일")
    
    def show_quiz_rush(self, user):
        """Show quiz rush mini-game"""
        st.markdown("##### ⚡ 퀴즈 러시")
        
        if 'quiz_rush_active' not in st.session_state:
            st.session_state.quiz_rush_active = False
            st.session_state.quiz_rush_score = 0
            st.session_state.quiz_rush_time = 300  # 5 minutes
        
        if not st.session_state.quiz_rush_active:
            st.markdown("5분 안에 최대한 많은 퀴즈를 풀어보세요!")
            
            if st.button("🚀 퀴즈 러시 시작"):
                st.session_state.quiz_rush_active = True
                st.session_state.quiz_rush_start_time = datetime.now()
                st.rerun()
        else:
            # Show timer
            elapsed = (datetime.now() - st.session_state.quiz_rush_start_time).seconds
            remaining = max(0, 300 - elapsed)
            
            if remaining > 0:
                error_handler.wrap_streamlit_component(st.metric, "남은 시간", f"{remaining}초")
                error_handler.wrap_streamlit_component(st.metric, "현재 점수", st.session_state.quiz_rush_score)
                
                # Show quick quiz question
                questions = [
                    {"q": "파이썬에서 리스트를 만드는 기호는?", "a": "[]", "options": ["[]", "{}", "()", "<>"]},
                    {"q": "HTML에서 제목을 나타내는 태그는?", "a": "h1", "options": ["h1", "title", "head", "header"]},
                    {"q": "1 + 1 = ?", "a": "2", "options": ["1", "2", "3", "4"]}
                ]
                
                import random
                current_q = random.choice(questions)
                
                st.markdown(f"**문제:** {current_q['q']}")
                
                answer = st.radio("답:", current_q['options'], key=f"rush_q_{elapsed}")
                
                if st.button("제출"):
                    if answer == current_q['a']:
                        st.session_state.quiz_rush_score += 10
                        st.success("정답!")
                    else:
                        st.error("틀렸습니다!")
                    st.rerun()
            else:
                st.markdown("### 🏁 퀴즈 러시 종료!")
                error_handler.wrap_streamlit_component(st.metric, "최종 점수", st.session_state.quiz_rush_score)
                
                # Award points based on score
                if st.session_state.quiz_rush_score > 50:
                    st.success("50포인트를 획득했습니다!")
                
                if st.button("다시 도전"):
                    st.session_state.quiz_rush_active = False
                    st.session_state.quiz_rush_score = 0
                    st.rerun()
    
    def show_point_roulette(self, user):
        """Show point roulette game"""
        st.markdown("##### 🎰 포인트 룰렛")
        
        user_points = self.calculate_user_points(user['username'])
        
        if user_points < 10:
            st.warning("룰렛을 돌리려면 최소 10포인트가 필요합니다.")
            return
        
        bet_amount = st.selectbox("베팅 포인트", [10, 20, 50, 100])
        
        if bet_amount > user_points:
            st.error("보유 포인트가 부족합니다.")
            return
        
        if st.button("🎲 룰렛 돌리기"):
            import random
            
            outcomes = [
                {"result": "꽝", "multiplier": 0, "probability": 0.4},
                {"result": "2배", "multiplier": 2, "probability": 0.3},
                {"result": "3배", "multiplier": 3, "probability": 0.2},
                {"result": "5배", "multiplier": 5, "probability": 0.08},
                {"result": "잭팟!", "multiplier": 10, "probability": 0.02}
            ]
            
            # Weighted random selection
            rand = random.random()
            cumulative_prob = 0
            
            for outcome in outcomes:
                cumulative_prob += outcome["probability"]
                if rand <= cumulative_prob:
                    selected_outcome = outcome
                    break
            
            result_points = bet_amount * selected_outcome["multiplier"]
            net_gain = result_points - bet_amount
            
            if selected_outcome["result"] == "꽝":
                st.error(f"😢 {selected_outcome['result']}! {bet_amount}포인트를 잃었습니다.")
            elif selected_outcome["result"] == "잭팟!":
                st.balloons()
                st.success(f"🎉 {selected_outcome['result']} {result_points}포인트를 획득했습니다! (+{net_gain})")
            else:
                st.success(f"🎊 {selected_outcome['result']}! {result_points}포인트를 획득했습니다! (+{net_gain})")
    
    def purchase_item(self, username, item):
        """Purchase an item from the point shop"""
        user_points = self.calculate_user_points(username)
        
        if user_points >= item['cost']:
            # Deduct points (this would need a proper points tracking system)
            # For now, just log the purchase
            st.session_state.logging_system.log_activity(
                username,
                'Point Shop Purchase',
                f"Purchased {item['name']} for {item['cost']} points",
                'Point Shop'
            )
            return True
        
        return False