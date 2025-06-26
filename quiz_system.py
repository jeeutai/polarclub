
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random
from error_handler import error_handler


class QuizSystem:

    def __init__(self):
        self.quizzes_file = 'data/quizzes.csv'
        self.quiz_responses_file = 'data/quiz_responses.csv'
        # 세션 상태 확인 후 초기화
        if hasattr(st.session_state, 'data_manager'):
            self.initialize_quiz_files()

    def initialize_quiz_files(self):
        """Initialize quiz-related CSV files"""
        # data_manager가 있는 경우에만 실행
        if not hasattr(st.session_state, 'data_manager'):
            return
            
        # Initialize quizzes.csv
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        if quizzes_df.empty:
            quizzes_structure = [
                'id', 'title', 'description', 'club', 'creator', 'questions',
                'time_limit', 'attempts_allowed', 'status', 'created_date'
            ]
            empty_df = pd.DataFrame(columns=quizzes_structure)
            st.session_state.data_manager.save_csv('quizzes', empty_df)

        # Initialize quiz_responses.csv
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        if responses_df.empty:
            responses_structure = [
                'id', 'quiz_id', 'username', 'answers', 'score',
                'total_questions', 'completed_date', 'time_taken'
            ]
            empty_df = pd.DataFrame(columns=responses_structure)
            st.session_state.data_manager.save_csv('quiz_responses', empty_df)

    def show_quiz_interface(self, user):
        """Display the enhanced quiz interface"""
        st.markdown("### 🧠 퀴즈 시스템")
        
        # data_manager 확인
        if not hasattr(st.session_state, 'data_manager'):
            st.error("데이터 매니저가 초기화되지 않았습니다.")
            return
        
        # 퀴즈 파일 초기화 (지연 초기화)
        self.initialize_quiz_files()

        # 사용자 통계 표시
        self.show_user_quiz_stats(user)
        
        if user['role'] in ['선생님', '회장', '부회장']:
            tabs = st.tabs(["📝 퀴즈 목록", "➕ 퀴즈 생성", "📊 결과 분석", "🏆 리더보드", "📈 통계"])
        else:
            tabs = st.tabs(["📝 퀴즈 목록", "📈 내 점수", "🏆 리더보드", "🎯 성취도"])

        with tabs[0]:
            self.show_quiz_list(user)

        if user['role'] in ['선생님', '회장', '부회장']:
            with tabs[1]:
                self.show_quiz_creation(user)

            with tabs[2]:
                self.show_quiz_analytics(user)
                
            with tabs[3]:
                self.show_leaderboard(user)
                
            with tabs[4]:
                self.show_detailed_statistics(user)
        else:
            with tabs[1]:
                self.show_my_scores(user)
                
            with tabs[2]:
                self.show_leaderboard(user)
                
            with tabs[3]:
                self.show_achievements(user)

    def show_user_quiz_stats(self, user):
        """Display user quiz statistics at the top"""
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_responses = responses_df[responses_df['username'] == user['username']] if not responses_df.empty else pd.DataFrame()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_attempts = len(user_responses)
            error_handler.wrap_streamlit_component(st.metric, "🎯 총 시도", total_attempts)
        
        with col2:
            if not user_responses.empty:
                avg_score = (user_responses['score'] / user_responses['total_questions']).mean() * 100
                error_handler.wrap_streamlit_component(st.metric, "📊 평균 점수", f"{avg_score:.1f}%")
            else:
                error_handler.wrap_streamlit_component(st.metric, "📊 평균 점수", "0%")
        
        with col3:
            perfect_scores = len(user_responses[user_responses['score'] == user_responses['total_questions']]) if not user_responses.empty else 0
            error_handler.wrap_streamlit_component(st.metric, "🏆 만점 횟수", perfect_scores)
        
        with col4:
            quizzes_df = st.session_state.data_manager.load_csv('quizzes')
            available_quizzes = len(quizzes_df[quizzes_df['status'] == '활성']) if not quizzes_df.empty else 0
            error_handler.wrap_streamlit_component(st.metric, "📚 사용 가능", available_quizzes)

    def show_quiz_list(self, user):
        """Display available quizzes with enhanced UI"""
        st.markdown("#### 📝 사용 가능한 퀴즈")

        quizzes_df = st.session_state.data_manager.load_csv('quizzes')

        if quizzes_df.empty:
            st.info("등록된 퀴즈가 없습니다.")
            return

        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            club_filter = st.selectbox("🏷️ 동아리 필터", 
                                     ["전체"] + list(quizzes_df['club'].unique()))
        
        with col2:
            status_filter = st.selectbox("📊 상태 필터", 
                                       ["전체", "활성", "비활성"])
        
        with col3:
            difficulty_filter = st.selectbox("🎯 난이도", 
                                           ["전체", "쉬움", "보통", "어려움"])

        # Apply filters
        filtered_df = quizzes_df.copy()
        
        if club_filter != "전체":
            filtered_df = filtered_df[filtered_df['club'] == club_filter]
        
        if status_filter != "전체":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        # Filter quizzes based on user's clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist() if not user_clubs.empty else ["전체"]
            filtered_df = filtered_df[(filtered_df['club'].isin(user_club_names)) | (filtered_df['creator'] == user['name'])]

        # Show active quizzes only for students
        if user['role'] not in ['선생님', '회장', '부회장']:
            filtered_df = filtered_df[filtered_df['status'] == '활성']

        # Display quizzes
        if filtered_df.empty:
            st.info("필터 조건에 맞는 퀴즈가 없습니다.")
        else:
            for _, quiz in filtered_df.iterrows():
                self.show_enhanced_quiz_card(quiz, user)

    def show_enhanced_quiz_card(self, quiz, user):
        """Display an enhanced quiz card"""
        # Get user's attempts
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_attempts = responses_df[
            (responses_df['quiz_id'] == quiz['id'])
            & (responses_df['username'] == user['username'])] if not responses_df.empty else pd.DataFrame()

        attempts_count = len(user_attempts)
        max_attempts = int(quiz.get('attempts_allowed', 999)) if pd.notna(quiz.get('attempts_allowed', 999)) else 999
        best_score = user_attempts['score'].max() if not user_attempts.empty else 0
        
        # Parse questions to get difficulty
        try:
            questions = json.loads(quiz['questions'])
            question_count = len(questions)
        except:
            question_count = 0

        # Status styling
        status_colors = {
            '활성': "#28a745",
            '비활성': "#6c757d",
            '종료': "#dc3545"
        }
        status_color = status_colors.get(quiz['status'], "#6c757d")

        with st.container():
            st.markdown(f"""
            <div class="club-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #333;">🧠 {quiz['title']}</h4>
                        <div style="margin: 10px 0; display: flex; gap: 10px; align-items: center;">
                            <span style="background-color: {status_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                                {quiz['status']}
                            </span>
                            <span style="background-color: #17a2b8; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                                {question_count}문제
                            </span>
                            <span style="background-color: #ffc107; color: #000; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                                ⏱️ {quiz.get('time_limit', 10)}분
                            </span>
                        </div>
                    </div>
                    {f'<div style="text-align: right;"><h3 style="color: #28a745; margin: 0;">{best_score}점</h3><small>최고 점수</small></div>' if best_score > 0 else ''}
                </div>

                <p style="color: #666; line-height: 1.6; margin: 15px 0;">{quiz['description']}</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                        <div><strong>🏷️ 동아리:</strong> {quiz['club']}</div>
                        <div><strong>👤 출제자:</strong> {quiz['creator']}</div>
                        <div><strong>🔄 시도:</strong> {attempts_count}/{max_attempts}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Enhanced action buttons
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                if quiz['status'] == '활성' and attempts_count < max_attempts:
                    if st.button("🚀 시작", key=f"start_quiz_{quiz['id']}", use_container_width=True):
                        st.session_state[f'taking_quiz_{quiz["id"]}'] = True
                        st.session_state[f'quiz_start_time_{quiz["id"]}'] = datetime.now()
                        st.rerun()
                elif attempts_count >= max_attempts:
                    st.error("시도 초과")
                else:
                    st.info("비활성")

            with col2:
                if not user_attempts.empty:
                    if st.button("📊 결과", key=f"results_{quiz['id']}", use_container_width=True):
                        st.session_state[f'show_results_{quiz["id"]}'] = True

            with col3:
                if user['role'] in ['선생님', '회장'] or str(user.get('name', '')).strip() == quiz['creator']:
                    if st.button("⚙️ 관리", key=f"manage_quiz_{quiz['id']}", use_container_width=True):
                        st.session_state[f'manage_quiz_{quiz["id"]}'] = True

            with col4:
                if st.button("ℹ️ 상세", key=f"info_{quiz['id']}", use_container_width=True):
                    self.show_quiz_info(quiz)

            with col5:
                if st.button("📈 통계", key=f"stats_{quiz['id']}", use_container_width=True):
                    self.show_quiz_stats(quiz)

            # Show quiz taking interface if requested
            if st.session_state.get(f'taking_quiz_{quiz["id"]}', False):
                self.show_enhanced_quiz_taking_interface(quiz, user)

            # Show results if requested
            if st.session_state.get(f'show_results_{quiz["id"]}', False):
                self.show_enhanced_quiz_results(quiz, user)

            # Show management interface if requested
            if st.session_state.get(f'manage_quiz_{quiz["id"]}', False):
                self.show_quiz_management(quiz, user)

    def show_enhanced_quiz_taking_interface(self, quiz, user):
        """Display enhanced quiz taking interface"""
        st.markdown("---")
        st.markdown(f"#### 🚀 퀴즈 진행: {quiz['title']}")

        # Parse questions
        try:
            questions = json.loads(quiz['questions'])
        except:
            st.error("퀴즈 데이터에 오류가 있습니다.")
            return

        # Enhanced time tracking with progress
        start_time = st.session_state.get(f'quiz_start_time_{quiz["id"]}')
        if start_time:
            elapsed_time = (datetime.now() - start_time).total_seconds() / 60
            total_time = int(quiz.get('time_limit', 10))
            remaining_time = total_time - elapsed_time
            progress = min(elapsed_time / total_time, 1.0)

            if remaining_time <= 0:
                st.error("⏰ 시간이 초과되었습니다!")
                st.session_state[f'taking_quiz_{quiz["id"]}'] = False
                st.rerun()
                return

            # Progress bar
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress*100}%;">
                    ⏰ 남은 시간: {remaining_time:.1f}분
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Enhanced quiz form
        with st.form(f"quiz_form_{quiz['id']}"):
            answers = []
            
            # Question progress
            total_questions = len(questions)
            st.markdown(f"**진행도: 0/{total_questions} 문제**")

            for i, question in enumerate(questions):
                st.markdown(f"### 문제 {i+1}. {question['question']}")

                # Filter out empty options
                options = [opt for opt in question['options'] if opt.strip()]

                # Enhanced radio with custom styling
                answer = st.radio(
                    f"선택하세요 (문제 {i+1})",
                    options,
                    key=f"q_{quiz['id']}_{i}",
                    label_visibility="collapsed"
                )
                answers.append(answer)
                
                # Add visual separator
                st.markdown("---")

            # Enhanced submit section
            col1, col2, col3 = st.columns(3)
            with col1:
                submit_button = st.form_submit_button("📤 제출하기", use_container_width=True)
            with col2:
                review_button = st.form_submit_button("👀 검토하기", use_container_width=True)
            with col3:
                cancel_quiz = st.form_submit_button("❌ 취소", use_container_width=True)

            if submit_button:
                self.submit_quiz_answers(quiz, user, questions, answers, start_time)

            if review_button:
                st.info("답안을 검토해보세요!")
                for i, (question, answer) in enumerate(zip(questions, answers)):
                    if answer:
                        st.write(f"**문제 {i+1}:** {question['question']}")
                        st.write(f"**선택한 답:** {answer}")

            if cancel_quiz:
                st.session_state[f'taking_quiz_{quiz["id"]}'] = False
                st.rerun()

    def submit_quiz_answers(self, quiz, user, questions, answers, start_time):
        """Submit quiz answers with enhanced feedback"""
        # Calculate score
        score = 0
        detailed_results = []
        
        for i, question in enumerate(questions):
            is_correct = answers[i] == question['correct']
            if is_correct:
                score += 1
            
            detailed_results.append({
                'question': question['question'],
                'user_answer': answers[i],
                'correct_answer': question['correct'],
                'is_correct': is_correct
            })

        # Calculate time taken
        time_taken = (datetime.now() - start_time).total_seconds() / 60

        # Save response
        response_data = {
            'quiz_id': quiz['id'],
            'username': user['username'],
            'answers': json.dumps(answers, ensure_ascii=False),
            'score': score,
            'total_questions': len(questions),
            'completed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'time_taken': round(time_taken, 2)
        }

        if st.session_state.data_manager.add_record('quiz_responses', response_data):
            # Enhanced success message
            score_percentage = (score / len(questions)) * 100
            
            if score_percentage == 100:
                st.balloons()
                st.success(f"🏆 완벽합니다! {score}/{len(questions)}점 (만점!)")
                
                # Award perfect score badge
                badge_data = {
                    'username': user['username'],
                    'badge_name': '퀴즈 마스터',
                    'badge_icon': '🏆',
                    'description': f"{quiz['title']} 만점 달성",
                    'awarded_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'awarded_by': 'System'
                }
                st.session_state.data_manager.add_record('badges', badge_data)
                
            elif score_percentage >= 80:
                st.success(f"🎉 우수합니다! {score}/{len(questions)}점 ({score_percentage:.1f}%)")
            elif score_percentage >= 60:
                st.info(f"👍 좋습니다! {score}/{len(questions)}점 ({score_percentage:.1f}%)")
            else:
                st.warning(f"📚 더 공부해보세요! {score}/{len(questions)}점 ({score_percentage:.1f}%)")

            # Show detailed results
            with st.expander("📊 상세 결과 보기"):
                for i, result in enumerate(detailed_results):
                    status = "✅" if result['is_correct'] else "❌"
                    st.write(f"{status} **문제 {i+1}:** {result['question']}")
                    st.write(f"   - 내 답: {result['user_answer']}")
                    st.write(f"   - 정답: {result['correct_answer']}")
                    
            st.session_state[f'taking_quiz_{quiz["id"]}'] = False
            st.rerun()
        else:
            st.error("퀴즈 제출에 실패했습니다.")

    def show_leaderboard(self, user):
        """Display quiz leaderboard"""
        st.markdown("#### 🏆 퀴즈 리더보드")
        
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        if responses_df.empty:
            st.info("아직 퀴즈 응답이 없습니다.")
            return
        
        # Calculate user statistics
        user_stats = responses_df.groupby('username').agg({
            'score': 'sum',
            'total_questions': 'sum',
            'quiz_id': 'count'
        }).reset_index()
        
        user_stats['accuracy'] = (user_stats['score'] / user_stats['total_questions'] * 100).round(1)
        user_stats = user_stats.sort_values(['score', 'accuracy'], ascending=[False, False])
        
        # Display top 10
        st.markdown("##### 🥇 상위 랭킹")
        for idx, row in user_stats.head(10).iterrows():
            rank = user_stats.index.get_loc(idx) + 1
            is_current_user = row['username'] == user['username']
            
            rank_emojis = {1: "🥇", 2: "🥈", 3: "🥉"}
            rank_emoji = rank_emojis.get(rank, f"{rank}.")
            
            bg_color = "linear-gradient(135deg, #FFD700, #FFA500)" if is_current_user else "#f8f9fa"
            text_color = "#000" if is_current_user else "#333"
            
            st.markdown(f"""
            <div style="background: {bg_color}; padding: 15px; border-radius: 10px; margin: 8px 0; 
                        border: {'2px solid #FF6B6B' if is_current_user else '1px solid #dee2e6'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 24px;">{rank_emoji}</span>
                        <div>
                            <strong style="color: {text_color};">{row['username']}</strong>
                            <div style="color: {text_color}; font-size: 14px; opacity: 0.8;">
                                퀴즈 {row['quiz_id']}개 참여
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {text_color}; font-size: 18px; font-weight: bold;">
                            {row['score']}점
                        </div>
                        <div style="color: {text_color}; font-size: 12px;">
                            정확도: {row['accuracy']}%
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def show_achievements(self, user):
        """Display user achievements"""
        st.markdown("#### 🎯 나의 성취도")
        
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_responses = responses_df[responses_df['username'] == user['username']] if not responses_df.empty else pd.DataFrame()
        
        # Achievement calculations
        achievements = []
        
        if not user_responses.empty:
            total_attempts = len(user_responses)
            perfect_scores = len(user_responses[user_responses['score'] == user_responses['total_questions']])
            avg_score = (user_responses['score'] / user_responses['total_questions']).mean() * 100
            
            # Define achievements
            if total_attempts >= 1:
                achievements.append({"name": "첫 걸음", "icon": "🎯", "desc": "첫 퀴즈 완료"})
            if total_attempts >= 5:
                achievements.append({"name": "열정적인 학습자", "icon": "📚", "desc": "5개 퀴즈 완료"})
            if total_attempts >= 10:
                achievements.append({"name": "퀴즈 마니아", "icon": "🔥", "desc": "10개 퀴즈 완료"})
            if perfect_scores >= 1:
                achievements.append({"name": "완벽주의자", "icon": "💯", "desc": "첫 만점 달성"})
            if perfect_scores >= 3:
                achievements.append({"name": "퀴즈 마스터", "icon": "🏆", "desc": "만점 3회 달성"})
            if avg_score >= 90:
                achievements.append({"name": "우수 학습자", "icon": "⭐", "desc": "평균 90% 이상"})
        
        # Display achievements
        if achievements:
            cols = st.columns(3)
            for i, achievement in enumerate(achievements):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="achievement-badge">
                        <div style="text-align: center;">
                            <div style="font-size: 32px;">{achievement['icon']}</div>
                            <div style="font-weight: bold; margin: 5px 0;">{achievement['name']}</div>
                            <div style="font-size: 12px; opacity: 0.8;">{achievement['desc']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("아직 획득한 성취가 없습니다. 퀴즈에 참여해보세요!")

    def show_quiz_creation(self, user):
        """Display enhanced quiz creation form"""
        st.markdown("#### ➕ 새 퀴즈 생성")

        with st.form("create_quiz_form"):
            # Basic information
            col1, col2 = st.columns(2)
            with col1:
                # Get user's clubs for club selection
                if user['role'] == '선생님':
                    clubs_df = st.session_state.data_manager.load_csv('clubs')
                    club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
                else:
                    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                    club_options = user_clubs['club_name'].tolist() if not user_clubs.empty else []

                selected_club = st.selectbox("🏷️ 동아리 선택", club_options)
                title = st.text_input("📝 퀴즈 제목", placeholder="퀴즈 제목을 입력하세요")
                
            with col2:
                time_limit = st.number_input("⏱️ 제한시간 (분)", min_value=1, max_value=60, value=10)
                attempts_allowed = st.number_input("🔄 허용 시도 횟수", min_value=1, max_value=10, value=3)
            
            description = st.text_area("📄 퀴즈 설명", placeholder="퀴즈에 대한 설명을 입력하세요", height=100)

            # Advanced settings
            with st.expander("🔧 고급 설정"):
                col1, col2 = st.columns(2)
                with col1:
                    show_results = st.checkbox("📊 결과 즉시 표시", value=True)
                    randomize_questions = st.checkbox("🔀 문제 순서 섞기", value=False)
                with col2:
                    randomize_options = st.checkbox("🔀 선택지 순서 섞기", value=False)
                    allow_review = st.checkbox("👀 답안 검토 허용", value=True)

            st.markdown("##### 📝 문제 등록")

            # Initialize questions in session state
            if 'quiz_questions' not in st.session_state:
                st.session_state.quiz_questions = []

            # Enhanced question input
            col1, col2 = st.columns([2, 1])
            with col1:
                question_text = st.text_area("❓ 문제", placeholder="문제를 입력하세요", height=100)
            with col2:
                question_type = st.selectbox("📋 문제 유형", ["객관식", "O/X", "단답형"])
                difficulty = st.selectbox("🎯 난이도", ["쉬움", "보통", "어려움"])

            # Options based on question type
            if question_type == "객관식":
                col1, col2 = st.columns(2)
                with col1:
                    option1 = st.text_input("선택지 1 ⭐", key="quiz_option1")
                    option2 = st.text_input("선택지 2", key="quiz_option2")
                with col2:
                    option3 = st.text_input("선택지 3", key="quiz_option3")
                    option4 = st.text_input("선택지 4", key="quiz_option4")

                correct_answer = st.selectbox("정답", ["선택지 1", "선택지 2", "선택지 3", "선택지 4"])
                options = [option1, option2, option3, option4]
                
            elif question_type == "O/X":
                options = ["O", "X"]
                correct_answer = st.selectbox("정답", ["O", "X"])
                
            else:  # 단답형
                correct_answer_text = st.text_input("정답", placeholder="정답을 입력하세요")
                options = [correct_answer_text]
                correct_answer = correct_answer_text

            explanation = st.text_area("💡 해설 (선택사항)", placeholder="문제에 대한 해설을 입력하세요")

            # Add question button
            if st.form_submit_button("➕ 문제 추가"):
                if question_text and (question_type != "객관식" or (option1 and option2)):
                    question = {
                        'question': question_text,
                        'type': question_type,
                        'options': options,
                        'correct': correct_answer,
                        'difficulty': difficulty,
                        'explanation': explanation
                    }
                    st.session_state.quiz_questions.append(question)
                    st.success(f"문제가 추가되었습니다! (총 {len(st.session_state.quiz_questions)}문제)")

            # Show added questions with enhanced display
            if st.session_state.quiz_questions:
                st.markdown("##### 등록된 문제 목록")
                for i, q in enumerate(st.session_state.quiz_questions):
                    with st.expander(f"문제 {i+1}: {q['question'][:50]}..."):
                        st.write(f"**문제:** {q['question']}")
                        st.write(f"**유형:** {q['type']} | **난이도:** {q['difficulty']}")
                        
                        if q['type'] == "객관식":
                            for j, opt in enumerate(q['options']):
                                if opt:
                                    marker = "✅" if f"선택지 {j+1}" == q['correct'] else "⭕"
                                    st.write(f"{marker} 선택지 {j+1}: {opt}")
                        else:
                            st.write(f"**정답:** {q['correct']}")
                            
                        if q.get('explanation'):
                            st.write(f"**해설:** {q['explanation']}")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"📝 수정", key=f"edit_q_{i}"):
                                st.info("문제 수정 기능은 개발 중입니다.")
                        with col2:
                            if st.button(f"🗑️ 삭제", key=f"del_q_{i}"):
                                st.session_state.quiz_questions.pop(i)
                                st.rerun()

            status = st.selectbox("📊 상태", ["활성", "비활성"])

            # Submit quiz
            col1, col2, col3 = st.columns(3)
            with col2:
                submit_button = st.form_submit_button("🚀 퀴즈 생성", use_container_width=True)

            if submit_button:
                if title and description and selected_club and st.session_state.quiz_questions:
                    quiz_data = {
                        'title': title,
                        'description': description,
                        'club': selected_club,
                        'creator': user['name'],
                        'questions': json.dumps(st.session_state.quiz_questions, ensure_ascii=False),
                        'time_limit': time_limit,
                        'attempts_allowed': attempts_allowed,
                        'status': status,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record('quizzes', quiz_data):
                        st.success("🎉 퀴즈가 성공적으로 생성되었습니다!")
                        st.session_state.quiz_questions = []  # Clear questions
                        
                        # Add notification
                        if hasattr(st.session_state, 'notification_system'):
                            st.session_state.notification_system.add_notification(
                                f"새 퀴즈: {title}", "info", "all",
                                f"{user['name']}님이 새 퀴즈를 등록했습니다."
                            )
                        st.rerun()
                    else:
                        st.error("퀴즈 생성에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력하고 최소 1개 이상의 문제를 등록해주세요.")

    def show_quiz_analytics(self, user):
        """Display enhanced quiz analytics"""
        st.markdown("#### 📊 퀴즈 결과 분석")

        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')

        if quizzes_df.empty:
            st.info("분석할 퀴즈가 없습니다.")
            return

        # Filter quizzes based on user role
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist() if not user_clubs.empty else []
            quizzes_df = quizzes_df[(quizzes_df['club'].isin(user_club_names)) | (quizzes_df['creator'] == user['name'])]

        # Select quiz for analysis
        quiz_options = {f"{row['title']} ({row['club']})": row['id'] for _, row in quizzes_df.iterrows()}

        if not quiz_options:
            st.info("분석할 수 있는 퀴즈가 없습니다.")
            return

        selected_quiz = st.selectbox("📊 분석할 퀴즈 선택", options=list(quiz_options.keys()))

        if selected_quiz:
            quiz_id = quiz_options[selected_quiz]
            quiz_responses = responses_df[responses_df['quiz_id'] == quiz_id] if not responses_df.empty else pd.DataFrame()

            if quiz_responses.empty:
                st.info("이 퀴즈에 대한 응답이 없습니다.")
                return

            # Enhanced statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                error_handler.wrap_streamlit_component(st.metric, "총 응답 수", len(quiz_responses))

            with col2:
                unique_users = quiz_responses['username'].nunique()
                error_handler.wrap_streamlit_component(st.metric, "참여 학생 수", unique_users)

            with col3:
                avg_score = quiz_responses['score'].mean()
                avg_total = quiz_responses['total_questions'].mean()
                error_handler.wrap_streamlit_component(st.metric, "평균 점수", f"{avg_score:.1f}/{avg_total:.0f}")

            with col4:
                avg_time = quiz_responses['time_taken'].mean()
                error_handler.wrap_streamlit_component(st.metric, "평균 소요 시간", f"{avg_time:.1f}분")

            # Enhanced visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 📊 점수 분포")
                score_counts = quiz_responses['score'].value_counts().sort_index()
                fig = px.bar(x=score_counts.index, y=score_counts.values, 
                           title="점수별 학생 수", labels={'x': '점수', 'y': '학생 수'})
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
            
            with col2:
                st.markdown("##### ⏱️ 소요 시간 분포")
                fig = px.histogram(quiz_responses, x='time_taken', nbins=10,
                                 title="소요 시간 분포", labels={'time_taken': '소요 시간(분)', 'count': '학생 수'})
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)

            # Individual results table
            st.markdown("##### 👥 개별 결과")
            display_columns = ['username', 'score', 'total_questions', 'completed_date', 'time_taken']
            display_df = quiz_responses[display_columns].copy()
            display_df.columns = ['학생명', '점수', '총 문제수', '완료일', '소요시간(분)']
            display_df = display_df.sort_values('점수', ascending=False)
            
            # Add ranking
            display_df['순위'] = range(1, len(display_df) + 1)
            display_df = display_df[['순위'] + list(display_df.columns[:-1])]

            error_handler.wrap_streamlit_component(st.dataframe, display_df, use_container_width=True)

    def show_my_scores(self, user):
        """Display enhanced user scores"""
        st.markdown("#### 📈 내 퀴즈 성과")

        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_responses = responses_df[responses_df['username'] == user['username']] if not responses_df.empty else pd.DataFrame()

        if user_responses.empty:
            st.info("참여한 퀴즈가 없습니다.")
            return

        # Enhanced overall statistics
        total_quizzes = user_responses['quiz_id'].nunique()
        total_attempts = len(user_responses)
        avg_score = (user_responses['score'] / user_responses['total_questions']).mean() * 100
        best_score = (user_responses['score'] / user_responses['total_questions']).max() * 100

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "참여 퀴즈", total_quizzes)
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "총 시도", total_attempts)
        with col3:
            error_handler.wrap_streamlit_component(st.metric, "평균 점수", f"{avg_score:.1f}%")
        with col4:
            error_handler.wrap_streamlit_component(st.metric, "최고 점수", f"{best_score:.1f}%")

        # Progress visualization
        st.markdown("##### 📈 성과 트렌드")
        user_responses['completed_date'] = pd.to_datetime(user_responses['completed_date'])
        user_responses['score_percentage'] = (user_responses['score'] / user_responses['total_questions']) * 100
        
        daily_progress = user_responses.groupby(user_responses['completed_date'].dt.date)['score_percentage'].mean()
        
        if not daily_progress.empty:
            fig = px.line(x=daily_progress.index, y=daily_progress.values,
                         title="일별 평균 점수 추이", labels={'x': '날짜', 'y': '점수 (%)'})
            error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)

        # Quiz-specific performance
        st.markdown("##### 📋 퀴즈별 성과")
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')

        for quiz_id in user_responses['quiz_id'].unique():
            quiz_attempts = user_responses[user_responses['quiz_id'] == quiz_id]
            quiz_info = quizzes_df[quizzes_df['id'] == quiz_id]

            if not quiz_info.empty:
                quiz = quiz_info.iloc[0]
                best_score = quiz_attempts['score'].max()
                attempts_count = len(quiz_attempts)
                best_attempt = quiz_attempts.loc[quiz_attempts['score'].idxmax()]
                best_time = best_attempt['time_taken']
                score_percentage = (best_score / best_attempt['total_questions']) * 100

                # Enhanced quiz card
                performance_color = "#28a745" if score_percentage >= 80 else "#ffc107" if score_percentage >= 60 else "#dc3545"
                
                st.markdown(f"""
                <div class="club-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: #333;">🧠 {quiz['title']}</h4>
                            <p style="color: #666; margin: 10px 0;">{quiz['description']}</p>
                        </div>
                        <div style="text-align: right;">
                            <h2 style="color: {performance_color}; margin: 0;">{score_percentage:.0f}%</h2>
                            <small>최고 점수</small>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 15px; text-align: center;">
                        <div>
                            <h3 style="color: #FF6B6B; margin: 0;">{best_score}/{best_attempt['total_questions']}</h3>
                            <small>최고 점수</small>
                        </div>
                        <div>
                            <h3 style="color: #4ECDC4; margin: 0;">{attempts_count}</h3>
                            <small>시도 횟수</small>
                        </div>
                        <div>
                            <h3 style="color: #28a745; margin: 0;">{best_time:.1f}분</h3>
                            <small>최단 시간</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    def show_enhanced_quiz_results(self, quiz, user):
        """Show enhanced detailed quiz results"""
        st.markdown("---")
        st.markdown(f"#### 📊 {quiz['title']} - 상세 결과")

        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_responses = responses_df[
            (responses_df['quiz_id'] == quiz['id'])
            & (responses_df['username'] == user['username'])] if not responses_df.empty else pd.DataFrame()

        if user_responses.empty:
            st.info("이 퀴즈에 대한 결과가 없습니다.")
            return

        # Show all attempts with enhanced visualization
        for idx, response in user_responses.iterrows():
            score_percentage = (response['score'] / response['total_questions']) * 100
            
            # Performance badge
            if score_percentage == 100:
                badge = "🏆 완벽!"
                badge_color = "#FFD700"
            elif score_percentage >= 80:
                badge = "🎉 우수"
                badge_color = "#28a745"
            elif score_percentage >= 60:
                badge = "👍 양호"
                badge_color = "#ffc107"
            else:
                badge = "📚 노력필요"
                badge_color = "#dc3545"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {badge_color}22, {badge_color}11); 
                        padding: 20px; border-radius: 12px; margin: 15px 0; 
                        border-left: 4px solid {badge_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #333;">{badge}</h4>
                        <div style="margin: 10px 0;">
                            <strong>점수: {response['score']}/{response['total_questions']} ({score_percentage:.1f}%)</strong>
                        </div>
                        <div style="color: #666;">
                            <p>📅 완료일: {response['completed_date']}</p>
                            <p>⏱️ 소요 시간: {response['time_taken']}분</p>
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 48px;">{badge.split()[0]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Close button
        if st.button("❌ 결과 닫기", key=f"close_results_{quiz['id']}", use_container_width=True):
            st.session_state[f'show_results_{quiz["id"]}'] = False
            st.rerun()

    def show_quiz_info(self, quiz):
        """Show enhanced quiz information"""
        try:
            questions = json.loads(quiz['questions'])
            question_count = len(questions)
            
            # Analyze difficulty
            difficulties = [q.get('difficulty', '보통') for q in questions]
            difficulty_count = Counter(difficulties)
            
        except:
            question_count = 0
            difficulty_count = {}

        st.markdown(f"""
        ### 📋 퀴즈 상세 정보
        
        **📝 제목:** {quiz.get('title', '제목 없음')}  
        **📄 설명:** {quiz.get('description', '설명 없음')}  
        **🏷️ 동아리:** {quiz.get('club', '동아리 없음')}  
        **👤 출제자:** {quiz.get('creator', '출제자 없음')}  
        **📊 문제 수:** {question_count}문제  
        **⏱️ 제한시간:** {quiz.get('time_limit', 10)}분  
        **🔄 허용 시도:** {quiz.get('attempts_allowed', 999)}회  
        **📊 상태:** {quiz.get('status', '상태 없음')}  
        **📅 생성일:** {quiz.get('created_date', '날짜 없음')}  
        """)
        
        if difficulty_count:
            st.markdown("**🎯 난이도 분포:**")
            for difficulty, count in difficulty_count.items():
                st.write(f"- {difficulty}: {count}문제")

    def show_quiz_stats(self, quiz):
        """Show quiz statistics"""
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        quiz_responses = responses_df[responses_df['quiz_id'] == quiz['id']] if not responses_df.empty else pd.DataFrame()
        
        if quiz_responses.empty:
            st.info("아직 응답이 없습니다.")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "총 응답", len(quiz_responses))
        with col2:
            avg_score = (quiz_responses['score'] / quiz_responses['total_questions']).mean() * 100
            error_handler.wrap_streamlit_component(st.metric, "평균 점수", f"{avg_score:.1f}%")
        with col3:
            completion_rate = (quiz_responses['score'] == quiz_responses['total_questions']).sum() / len(quiz_responses) * 100
            error_handler.wrap_streamlit_component(st.metric, "완료율", f"{completion_rate:.1f}%")

    def show_quiz_management(self, quiz, user):
        """Show quiz management interface"""
        st.markdown("---")
        st.markdown(f"#### ⚙️ {quiz['title']} 관리")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 상태 변경", use_container_width=True):
                new_status = "비활성" if quiz['status'] == "활성" else "활성"
                if st.session_state.data_manager.update_record('quizzes', quiz['id'], {'status': new_status}):
                    st.success(f"상태가 {new_status}로 변경되었습니다.")
                    st.rerun()
        
        with col2:
            if st.button("📝 수정", use_container_width=True):
                st.info("퀴즈 수정 기능은 개발 중입니다.")
        
        with col3:
            if st.button("🗑️ 삭제", use_container_width=True):
                if st.session_state.data_manager.delete_record('quizzes', quiz['id']):
                    st.success("퀴즈가 삭제되었습니다.")
                    st.rerun()
        
        if st.button("❌ 관리 닫기", key=f"close_manage_{quiz['id']}", use_container_width=True):
            st.session_state[f'manage_quiz_{quiz["id"]}'] = False
            st.rerun()

    def show_detailed_statistics(self, user):
        """Show detailed statistics for teachers"""
        st.markdown("#### 📈 상세 통계")
        
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        
        if responses_df.empty:
            st.info("통계 데이터가 없습니다.")
            return
        
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_quizzes = len(quizzes_df)
            error_handler.wrap_streamlit_component(st.metric, "총 퀴즈 수", total_quizzes)
        
        with col2:
            total_responses = len(responses_df)
            error_handler.wrap_streamlit_component(st.metric, "총 응답 수", total_responses)
        
        with col3:
            active_users = responses_df['username'].nunique()
            error_handler.wrap_streamlit_component(st.metric, "활성 사용자", active_users)
        
        with col4:
            avg_participation = total_responses / total_quizzes if total_quizzes > 0 else 0
            error_handler.wrap_streamlit_component(st.metric, "평균 참여도", f"{avg_participation:.1f}")
        
        # Detailed charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 일별 퀴즈 참여")
            responses_df['completed_date'] = pd.to_datetime(responses_df['completed_date'])
            daily_responses = responses_df.groupby(responses_df['completed_date'].dt.date).size()
            
            if not daily_responses.empty:
                fig = px.bar(x=daily_responses.index, y=daily_responses.values,
                           title="일별 퀴즈 참여 현황")
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
        
        with col2:
            st.markdown("##### 🏆 사용자별 성과")
            user_scores = responses_df.groupby('username')['score'].sum().sort_values(ascending=False).head(10)
            
            if not user_scores.empty:
                fig = px.bar(x=user_scores.values, y=user_scores.index, orientation='h',
                           title="상위 10명 총점")
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
