import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import requests
import json
import urllib.parse
from error_handler import error_handler

class AIAssistant:
    def __init__(self):
        self.search_enabled = True
        self.responses = {
            "greeting": [
                "안녕하세요! 폴라리스반 AI 어시스턴트입니다. 무엇을 도와드릴까요?",
                "반갑습니다! 동아리 활동에 대해 궁금한 것이 있으시면 언제든 물어보세요!",
                "안녕하세요! 오늘도 열심히 활동하시는 모습이 멋져요!"
            ],
            "attendance": [
                "출석률을 높이려면 매일 일정한 시간에 체크인하는 습관을 만들어보세요!",
                "연속 출석 목표를 설정하고 달성해보는 것은 어떨까요?",
                "출석 알림을 설정해서 빠뜨리지 않도록 도움을 받아보세요!"
            ],
            "study": [
                "학습 계획을 세우고 단계별로 진행해보세요!",
                "동아리 친구들과 스터디 그룹을 만들어보는 것은 어떨까요?",
                "과제는 미리미리 준비하는 것이 좋아요!"
            ],
            "출석": [
                "오늘도 출석해주셔서 감사합니다! 🎉",
                "꾸준한 출석이 성공의 열쇠입니다! 💪",
                "훌륭한 출석률을 유지하고 계시네요! ⭐"
            ],
            "지각": [
                "지각하셨군요. 다음에는 좀 더 일찍 와주세요! ⏰",
                "시간 관리에 신경써보세요. 응원합니다! 📅",
                "지각보다는 출석이 좋겠어요! 화이팅! 🔥"
            ],
            "결석": [
                "결석하셨네요. 괜찮으신가요? 😟",
                "건강 관리 잘 하시고 다음에는 만나요! 🏥",
                "몸조리 잘 하시고 빨리 회복하세요! 💊"
            ]
        }

    def show_ai_interface(self, user):
        """AI 어시스턴트 인터페이스 표시"""
        st.markdown("### 🤖 AI 어시스턴트")

        # AI 어시스턴트 소개
        with st.expander("🤖 AI 어시스턴트 소개", expanded=False):
            st.markdown("""
            **폴라리스반 AI 어시스턴트**는 여러분의 동아리 활동을 도와주는 똑똑한 도우미입니다!

            **주요 기능:**
            - 📊 학습 분석 및 조언
            - 🎯 개인 맞춤 추천
            - 📅 일정 관리 도움
            - 🏆 목표 설정 지원
            - 💡 창의적 아이디어 제안
            """)

        # 채팅 인터페이스
        st.markdown("#### 💬 AI와 대화하기")

        # 채팅 히스토리 표시
        if 'ai_chat_history' not in st.session_state:
            st.session_state.ai_chat_history = []

        # 채팅 기록 표시
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.ai_chat_history:
                if message['sender'] == 'user':
                    st.markdown(f"""
                    <div style="text-align: right; margin: 10px 0;">
                        <div style="background: #007bff; color: white; padding: 10px; border-radius: 15px; display: inline-block; max-width: 70%;">
                            {message['content']}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            {message['timestamp']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin: 10px 0;">
                        <div style="background: #f1f3f4; color: #333; padding: 10px; border-radius: 15px; display: inline-block; max-width: 70%;">
                            🤖 {message['content']}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            {message['timestamp']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # 사용자 입력
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("메시지를 입력하세요...", key="ai_chat_input", label_visibility="collapsed")
        with col2:
            send_button = st.button("전송", use_container_width=True)

        # 빠른 질문 버튼들
        st.markdown("##### 🚀 빠른 질문")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button("📊 내 출석률은?", key="quick_attendance"):
                user_input = "내 출석률을 알려줘"
                send_button = True

        with col2:
            if st.button("🎯 학습 조언", key="quick_study"):
                user_input = "학습 방법을 추천해줘"
                send_button = True

        with col3:
            if st.button("📅 일정 도움", key="quick_schedule"):
                user_input = "일정 관리 도움이 필요해"
                send_button = True

        with col4:
            if st.button("💡 아이디어", key="quick_ideas"):
                user_input = "창의적인 아이디어를 제안해줘"
                send_button = True

        with col5:
            if st.button("🔍 검색", key="quick_search"):
                user_input = "파이썬 프로그래밍 학습법을 검색해줘"
                send_button = True

        # 메시지 처리
        if send_button and user_input:
            # 사용자 메시지 추가
            st.session_state.ai_chat_history.append({
                'sender': 'user',
                'content': user_input,
                'timestamp': datetime.now().strftime('%H:%M')
            })

            # AI 응답 생성
            ai_response = self.generate_ai_response(user_input, user)

            # AI 응답 추가
            st.session_state.ai_chat_history.append({
                'sender': 'ai',
                'content': ai_response,
                'timestamp': datetime.now().strftime('%H:%M')
            })

            st.rerun()

        # AI 분석 대시보드
        st.markdown("---")
        st.markdown("#### 📊 AI 분석 대시보드")

        tabs = st.tabs(["🎯 개인 분석", "📈 추세 예측", "💡 맞춤 추천", "🏆 목표 설정"])

        with tabs[0]:
            self.show_personal_analysis(user)

        with tabs[1]:
            self.show_trend_prediction(user)

        with tabs[2]:
            self.show_personalized_recommendations(user)

        with tabs[3]:
            self.show_goal_suggestions(user)

    def web_search(self, query):
        """웹 검색 기능 (가상 구현)"""
        try:
            # 실제 웹 검색 API 대신 교육적 내용 제공
            search_responses = {
                "파이썬": "🐍 파이썬 학습법:\n• 기초 문법부터 차근차근 시작\n• 실습 위주의 학습\n• 작은 프로젝트부터 도전\n• 코딩테스트 문제 풀기",
                "프로그래밍": "💻 프로그래밍 학습 팁:\n• 매일 조금씩이라도 코딩하기\n• 에러를 두려워하지 마세요\n• 구글링도 중요한 능력입니다\n• 다른 사람의 코드 읽어보기",
                "학습법": "📚 효과적인 학습법:\n• 포모도로 기법 (25분 집중 + 5분 휴식)\n• 액티브 러닝 (설명해보기)\n• 스페이스 리피티션 (간격 반복)\n• 피어 러닝 (친구와 함께)",
                "창의": "💡 창의성 기르기:\n• 브레인스토밍\n• 마인드맵 활용\n• 다양한 분야 경험\n• 질문하는 습관",
                "시간관리": "⏰ 시간 관리법:\n• 우선순위 정하기\n• 할 일 목록 작성\n• 시간 블록킹\n• 완벽주의 버리기"
            }

            for keyword, response in search_responses.items():
                if keyword in query:
                    return f"🔍 '{query}' 검색 결과:\n\n{response}"

            return f"🔍 '{query}'에 대한 정보를 찾았습니다:\n\n💡 관련 키워드를 더 구체적으로 말씀해주시면 더 정확한 정보를 제공할 수 있어요!"
        except Exception:
            return "검색 중 오류가 발생했습니다. 다시 시도해주세요."

    def generate_ai_response(self, user_input, user):
        """AI 응답 생성 (개선된 버전)"""
        try:
            input_lower = str(user_input).lower() if user_input else ""
        except Exception:
            input_lower = ""

        # 검색 요청 감지
        if any(keyword in input_lower for keyword in ['검색', 'search', '찾아줘', '알아봐']):
            search_query = user_input.replace('검색해줘', '').replace('찾아줘', '').replace('알아봐', '').strip()
            if search_query:
                return self.web_search(search_query)

        # 출석 관련 질문
        if any(keyword in input_lower for keyword in ['출석', '출석률', '참석']):
            return self.get_attendance_response(user)

        # 학습 관련 질문
        elif any(keyword in input_lower for keyword in ['학습', '공부', '과제', '퀴즈']):
            return self.get_study_response(user)

        # 일정 관련 질문
        elif any(keyword in input_lower for keyword in ['일정', '스케줄', '계획']):
            return self.get_schedule_response(user)

        # 동아리 관련 질문
        elif any(keyword in input_lower for keyword in ['동아리', '활동', '참여']):
            return self.get_club_response(user)

        # 인사말
        elif any(keyword in input_lower for keyword in ['안녕', '안녕하세요', '반가워', '처음']):
            return random.choice(self.responses["greeting"])

        # 도움 요청
        elif any(keyword in input_lower for keyword in ['도움', '도와줘', '모르겠어']):
            return self.get_help_response(user_input)

        # 기본 응답
        else:
            return self.get_general_response(user_input, user)

    def get_attendance_response(self, user):
        """출석 관련 응답"""
        try:
            # 실제 출석 데이터 조회
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            user_attendance = attendance_df[attendance_df['username'] == user['username']]

            if not user_attendance.empty:
                total_days = len(user_attendance)
                present_days = len(user_attendance[user_attendance['status'] == '출석'])
                rate = (present_days / total_days * 100) if total_days > 0 else 0

                if rate >= 90:
                    return f"와! 출석률이 {rate:.1f}%네요! 정말 성실하시군요! 🌟 이 조자로 계속 유지해주세요!"
                elif rate >= 80:
                    return f"출석률이 {rate:.1f}%입니다. 좋은 편이에요! 조금만 더 노력하면 90% 달성 가능해요! 💪"
                elif rate >= 70:
                    return f"출석률이 {rate:.1f}%입니다. 개선이 필요해 보여요. 알림 설정을 활용해보시는 건 어떨까요? 📱"
                else:
                    return f"출석률이 {rate:.1f}%입니다. 함께 개선 계획을 세워볼까요? 작은 목표부터 시작해보세요! 🎯"
            else:
                return "아직 출석 기록이 없네요! 첫 출석을 시작해보시는 건 어떨까요? 시작이 반이에요! 🚀"
        except Exception:
            return "출석 데이터를 불러올 수 없습니다. 출석 탭에서 출석 체크를 해보세요! 📅"

    def get_study_response(self, user):
        """학습 관련 응답"""
        try:
            # 과제 및 퀴즈 데이터 조회
            assignments_df = st.session_state.data_manager.load_csv('assignments')
            quizzes_df = st.session_state.data_manager.load_csv('quizzes')

            pending_assignments = len(assignments_df) if not assignments_df.empty else 0
            total_quizzes = len(quizzes_df) if not quizzes_df.empty else 0

            responses = [
                f"현재 {pending_assignments}개의 과제가 있어요. 계획적으로 진행해보세요! 📚",
                "학습할 때는 25분 집중 + 5분 휴식 방법을 써보세요! (포모도로 기법) 🍅",
                "동아리 친구들과 함께 스터디하면 더 효과적일 거예요! 👥",
                "어려운 내용은 작은 단위로 나누어 학습해보세요! 🧩"
            ]

            return random.choice(responses)
        except Exception:
            return "학습 데이터를 불러올 수 없습니다. 과제나 퀴즈 탭을 확인해보세요! 📖"

    def get_schedule_response(self, user):
        """일정 관련 응답"""
        try:
            schedule_df = st.session_state.data_manager.load_csv('schedules')
            today = datetime.now().date()

            if not schedule_df.empty:
                today_schedules = schedule_df[schedule_df['date'] == today.strftime('%Y-%m-%d')]
                upcoming_count = len(today_schedules)

                if upcoming_count > 0:
                    return f"오늘 {upcoming_count}개의 일정이 있어요! 미리 준비하셨나요? 📅✨"
                else:
                    return "오늘은 예정된 일정이 없네요. 개인 학습 시간으로 활용해보시는 건 어떨까요? 📖"

            return "일정 관리는 성공의 열쇠예요! 우선순위를 정해서 계획을 세워보세요! 🗓️"
        except Exception:
            return "일정 데이터를 불러올 수 없습니다. 일정 탭에서 스케줄을 확인해보세요! 📅"

    def get_club_response(self, user):
        """동아리 관련 응답"""
        try:
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])

            if not user_clubs.empty:
                club_count = len(user_clubs)
                return f"{club_count}개 동아리에서 활동 중이시군요! 다양한 경험이 소중한 자산이 될 거예요! 🌟"
            else:
                return "동아리 활동을 시작해보세요! 새로운 친구들과 흥미로운 경험을 할 수 있어요! 🎭"
        except Exception:
            return "동아리 데이터를 불러올 수 없습니다. 홈 탭에서 동아리 현황을 확인해보세요! 🏠"

    def get_help_response(self, user_input):
        """도움 요청에 대한 응답"""
        help_topics = {
            "출석": "출석 관련 질문이시군요! '내 출석률은?' 또는 '출석 개선 방법'을 물어보세요.",
            "과제": "과제 관련 도움이 필요하시군요! '과제 관리 방법' 또는 '학습 조언'을 요청해보세요.",
            "일정": "일정 관리 도움이 필요하시군요! '일정 정리 방법' 또는 '시간 관리'를 물어보세요.",
            "동아리": "동아리 활동 관련 질문이시군요! '동아리 참여 방법' 등을 물어보세요."
        }

        for topic, suggestion in help_topics.items():
            if topic in user_input:
                return f"💡 {suggestion}"

        return "🤖 다음과 같은 도움을 드릴 수 있어요:\n• 📊 출석률 분석\n• 📚 학습 조언\n• 📅 일정 관리\n• 🔍 정보 검색\n• 💡 아이디어 제안\n\n구체적으로 무엇을 도와드릴까요?"

    def get_general_response(self, user_input, user):
        """일반적인 응답 (개선된 버전)"""
        # 입력 분석
        if '?' in user_input or '뭐' in user_input or '어떻게' in user_input:
            return f"🤔 '{user_input}'에 대해 더 구체적으로 설명해주시면 정확한 답변을 드릴 수 있어요! 예를 들어:\n• 출석률을 알고 싶으시면 '내 출석률은?'\n• 학습 방법을 원하시면 '공부 방법 추천해줘'\n• 정보 검색을 원하시면 '파이썬 검색해줘'"

        general_responses = [
            f"안녕하세요 {user['name']}님! 흥미로운 질문이네요! 더 구체적으로 설명해주시면 도움을 드릴 수 있어요! 🤔",
            f"{user['name']}님, 좋은 생각이에요! 함께 해결 방법을 찾아볼까요? 💡",
            f"그 부분에 대해 더 자세히 알려주시면 {user['name']}님께 맞춤형 조언을 드릴 수 있어요! 📋",
            "멋진 아이디어네요! 실행 계획을 함께 세워볼까요? 🚀 검색이 필요하시면 '검색해줘'라고 말씀해주세요!"
        ]

        return random.choice(general_responses)

    def show_personal_analysis(self, user):
        """개인 분석 표시"""
        st.markdown("##### 🎯 개인 맞춤 분석")

        try:
            # 출석 패턴 분석
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            user_attendance = attendance_df[attendance_df['username'] == user['username']]

            if not user_attendance.empty:
                total_records = len(user_attendance)
                present_count = len(user_attendance[user_attendance['status'] == '출석'])
                attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0

                error_handler.wrap_streamlit_component(st.metric, "출석률", f"{attendance_rate:.1f}%")
                error_handler.wrap_streamlit_component(st.metric, "총 출석일", f"{present_count}일")

                if attendance_rate >= 90:
                    st.success("🌟 우수한 출석률을 유지하고 계시네요!")
                elif attendance_rate >= 70:
                    st.info("📈 출석률이 양호합니다. 조금만 더 노력해보세요!")
                else:
                    st.warning("📊 출석률 개선이 필요합니다.")
            else:
                st.info("아직 출석 기록이 없습니다.")

            # 학습 활동 분석
            submissions_df = st.session_state.data_manager.load_csv('submissions')
            user_submissions = submissions_df[submissions_df['username'] == user['username']] if not submissions_df.empty else pd.DataFrame()

            if not user_submissions.empty:
                st.markdown("**📚 학습 활동**")
                total_submissions = len(user_submissions)
                error_handler.wrap_streamlit_component(st.metric, "과제 제출", f"{total_submissions}회")
            else:
                st.info("아직 과제 제출 기록이 없습니다.")

        except Exception as e:
            st.error("데이터를 불러오는 중 오류가 발생했습니다.")

    def show_trend_prediction(self, user):
        """추세 예측 표시"""
        st.markdown("##### 📈 AI 추세 예측")

        try:
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            user_attendance = attendance_df[attendance_df['username'] == user['username']]

            if len(user_attendance) >= 5:
                recent_attendance = user_attendance.tail(10)
                present_count = len(recent_attendance[recent_attendance['status'] == '출석'])
                recent_rate = (present_count / len(recent_attendance)) * 100

                error_handler.wrap_streamlit_component(st.metric, "최근 출석률", f"{recent_rate:.1f}%")

                if recent_rate >= 80:
                    st.success("📈 좋은 출석 추세를 보이고 있어요!")
                else:
                    st.warning("📉 출석률 개선이 필요해 보여요!")
            else:
                st.info("더 많은 데이터가 축적되면 정확한 예측을 제공할 수 있어요!")

        except Exception:
            st.error("추세 분석 중 오류가 발생했습니다.")

    def show_personalized_recommendations(self, user):
        """개인 맞춤 추천"""
        st.markdown("##### 💡 AI 맞춤 추천")

        recommendations = [
            "⏰ 매일 일정한 시간에 출석 체크하는 습관을 만들어보세요!",
            "📚 과제는 미리미리 준비해서 여유롭게 제출해보세요!",
            "👥 동아리 친구들과 함께 스터디 그룹을 만들어보세요!",
            "🎯 주간 목표를 설정하고 달성해보세요!",
            "📱 알림 기능을 활용해서 중요한 일정을 놓치지 마세요!"
        ]

        for i, rec in enumerate(recommendations[:3]):
            st.write(f"{i+1}. {rec}")

    def show_goal_suggestions(self, user):
        """목표 설정 제안"""
        st.markdown("##### 🏆 AI 목표 설정 도우미")

        goal_suggestions = [
            "🎯 이번 주 출석률 95% 달성하기",
            "📚 과제 정시 제출 100% 달성하기",
            "👥 동아리 활동 적극 참여하기",
            "📈 개인 학습 목표 설정하고 달성하기"
        ]

        st.markdown("**추천 목표:**")
        for goal in goal_suggestions:
            st.write(f"• {goal}")

        if st.button("목표 설정하기"):
            st.success("목표가 설정되었습니다! 화이팅! 💪")

    def get_smart_response(self, status, username):
        """상황에 맞는 스마트 응답 생성"""
        if status in self.responses:
            return random.choice(self.responses[status])
        return "좋은 하루 되세요! 😊"

    def analyze_attendance_pattern(self, username):
        """출석 패턴 분석 및 조언"""
        try:
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            user_data = attendance_df[attendance_df['username'] == username]

            if user_data.empty:
                return "아직 출석 기록이 없어 분석할 수 없습니다."

            recent_data = user_data.tail(10)
            present_rate = (recent_data['status'] == '출석').mean() * 100

            if present_rate >= 90:
                return "🌟 완벽한 출석률입니다! 이 상태를 유지하세요!"
            elif present_rate >= 70:
                return "📈 출석률이 괜찮지만 더 개선할 수 있어요!"
            else:
                return "⚠️ 출석률 개선이 필요합니다. 목표를 세워보세요!"
        except Exception:
            return "출석 데이터를 분석할 수 없습니다."

    def suggest_improvement(self, username):
        """개선 제안"""
        suggestions = [
            "매일 같은 시간에 알림을 설정해보세요! ⏰",
            "출석 목표를 세우고 달성해보세요! 🎯",
            "친구와 함께 출석 챌린지를 해보는 건 어떨까요? 👥",
            "출석할 때마다 작은 보상을 정해보세요! 🎁"
        ]
        return random.choice(suggestions)
    
    def get_ai_response(self, question):
        """Generate AI response for user question"""
        try:
            # Simple rule-based responses for common questions
            question_lower = question.lower()

            # Check if question requires web search
            search_keywords = ["최신", "뉴스", "정보", "검색", "찾아줘", "알려줘"]
            needs_search = any(keyword in question_lower for keyword in search_keywords)

            if needs_search:
                return self.search_web_info(question)

            responses = {
                "안녕": "안녕하세요! 무엇을 도와드릴까요? 웹 검색이 필요하시면 '검색'이라는 키워드를 포함해서 질문해 주세요.",
                "동아리": "동아리 관련 질문이시군요! 어떤 동아리에 대해 알고 싶으신가요?",
                "과제": "과제 관련 도움이 필요하시군요. 구체적으로 어떤 도움이 필요한지 말씀해 주세요.",
                "출석": "출석 관리에 대해 궁금하시군요. 출석체크 방법이나 출석률 확인에 대해 도움을 드릴 수 있습니다.",
                "공지": "공지사항 관련 질문이시군요. 최신 공지사항을 확인하거나 공지사항 작성에 대해 도움을 드릴 수 있습니다.",
                "검색": "웹 검색 기능을 사용하시려면 구체적인 검색어와 함께 질문해 주세요. 예: '파이썬 최신 정보 검색해줘'"
            }

            for keyword, response in responses.items():
                if keyword in question_lower:
                    return response

            return "죄송합니다. 구체적인 질문을 해주시면 더 정확한 답변을 드릴 수 있습니다. 웹 검색이 필요하시면 '검색'이라는 키워드를 포함해서 질문해 주세요."

        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {e}"

    def search_web_info(self, query):
        """Search web for information (simulated)"""
        try:
            # 실제 웹 검색 기능은 API 키가 필요하므로 시뮬레이션
            search_results = {
                "파이썬": "🔍 파이썬 최신 정보: Python 3.12가 최신 버전이며, 새로운 기능들이 추가되었습니다. 성능 개선과 타입 힌팅 기능이 강화되었습니다.",
                "streamlit": "🔍 Streamlit 정보: Streamlit은 데이터 앱을 쉽게 만들 수 있는 Python 라이브러리입니다. 최신 버전에서는 멀티페이지 앱 기능이 개선되었습니다.",
                "AI": "🔍 AI 최신 동향: ChatGPT, Claude, Gemini 등 다양한 AI 모델들이 계속 발전하고 있으며, 교육 분야에서의 활용도가 증가하고 있습니다.",
                "교육": "🔍 교육 기술 동향: AI를 활용한 개인화 학습, 메타버스 교육, 디지털 리터러시 교육이 주목받고 있습니다."
            }

            query_lower = query.lower()
            for keyword, result in search_results.items():
                if keyword in query_lower:
                    return f"{result}\n\n💡 더 구체적인 정보가 필요하시면 관련 키워드로 다시 검색해 보세요!"

            return "🔍 웹 검색 결과: 해당 키워드에 대한 구체적인 정보를 찾지 못했습니다. 다른 키워드로 다시 검색해 보시거나, 더 구체적인 질문을 해주세요."

        except Exception as e:
            return f"웹 검색 중 오류가 발생했습니다: {e}"