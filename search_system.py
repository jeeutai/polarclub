import streamlit as st
import pandas as pd
from datetime import datetime
import trafilatura
import re
from error_handler import error_handler

class SearchSystem:
    def __init__(self):
        pass

    def show_search_interface(self, user):
        """Display search interface"""
        st.markdown("### 🔍 통합 검색")
        
        tabs = st.tabs(["🏠 내부 검색", "🌐 웹 검색", "📊 검색 통계"])
        
        with tabs[0]:
            self.show_internal_search(user)
        
        with tabs[1]:
            self.show_web_search(user)
        
        with tabs[2]:
            self.show_search_stats(user)

    def show_internal_search(self, user):
        """Display internal data search"""
        st.markdown("#### 🏠 내부 데이터 검색")
        
        # Search form
        with st.form("internal_search_form"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_query = st.text_input(
                    "검색어", 
                    placeholder="검색할 내용을 입력하세요...",
                    help="게시글, 과제, 댓글, 사용자 등을 검색할 수 있습니다"
                )
            
            with col2:
                search_button = st.form_submit_button("🔍 검색", use_container_width=True)
        
        # Search filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_categories = st.multiselect(
                "검색 범위",
                ["게시글", "과제", "댓글", "사용자", "동아리", "퀴즈", "투표"],
                default=["게시글", "과제"]
            )
        
        with col2:
            date_range = st.selectbox(
                "기간",
                ["전체", "오늘", "일주일", "한달", "3개월"]
            )
        
        with col3:
            user_filter = st.selectbox(
                "작성자",
                ["전체"] + self.get_all_users()
            )
        
        if search_button and search_query:
            # Log search activity
            st.session_state.logging_system.log_activity(
                user['username'],
                'Search',
                f'Internal search: {search_query}',
                'Search System'
            )
            
            # Perform search
            results = self.perform_internal_search(
                search_query, search_categories, date_range, user_filter, user
            )
            
            # Display results
            self.display_search_results(results, search_query)

    def show_web_search(self, user):
        """Display web search interface"""
        st.markdown("#### 🌐 웹 검색")
        
        # Web search form
        with st.form("web_search_form"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                web_query = st.text_input(
                    "웹 검색어",
                    placeholder="웹에서 검색할 내용을 입력하세요...",
                    help="외부 웹사이트에서 정보를 검색합니다"
                )
            
            with col2:
                web_search_button = st.form_submit_button("🌐 웹 검색", use_container_width=True)
        
        # Web search options
        col1, col2 = st.columns(2)
        
        with col1:
            search_engines = st.multiselect(
                "검색 엔진",
                ["Google", "Naver", "Daum", "Wikipedia"],
                default=["Google", "Naver"]
            )
        
        with col2:
            content_types = st.multiselect(
                "콘텐츠 유형",
                ["뉴스", "학술자료", "블로그", "위키백과"],
                default=["뉴스", "학술자료"]
            )
        
        if web_search_button and web_query:
            # Log web search activity
            st.session_state.logging_system.log_activity(
                user['username'],
                'Web Search',
                f'Web search: {web_query}',
                'Web Search System'
            )
            
            # Perform web search
            with st.spinner("웹에서 검색 중..."):
                web_results = self.perform_web_search(web_query, search_engines, content_types)
                self.display_web_search_results(web_results, web_query)

    def show_search_stats(self, user):
        """Display search statistics"""
        st.markdown("#### 📊 검색 통계")
        
        # Get search logs
        logs_df = st.session_state.data_manager.load_csv('logs')
        search_logs = logs_df[
            (logs_df['activity_type'].isin(['Search', 'Web Search'])) &
            (logs_df['username'] == user['username'])
        ] if not logs_df.empty else pd.DataFrame()
        
        if search_logs.empty:
            st.info("검색 기록이 없습니다.")
            return
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_searches = len(search_logs)
            error_handler.wrap_streamlit_component(st.metric, "총 검색 횟수", total_searches)
        
        with col2:
            internal_searches = len(search_logs[search_logs['activity_type'] == 'Search'])
            error_handler.wrap_streamlit_component(st.metric, "내부 검색", internal_searches)
        
        with col3:
            web_searches = len(search_logs[search_logs['activity_type'] == 'Web Search'])
            error_handler.wrap_streamlit_component(st.metric, "웹 검색", web_searches)
        
        with col4:
            today_searches = len(search_logs[
                search_logs['timestamp'].str.startswith(datetime.now().strftime('%Y-%m-%d'))
            ])
            error_handler.wrap_streamlit_component(st.metric, "오늘 검색", today_searches)
        
        # Recent searches
        st.markdown("##### 🕒 최근 검색어")
        recent_searches = search_logs.sort_values('timestamp', ascending=False).head(10)
        
        for _, search in recent_searches.iterrows():
            search_term = search['activity_description'].split(': ')[-1]
            search_type = "🏠" if search['activity_type'] == 'Search' else "🌐"
            
            search_html = f"""
            <div style="background: white; padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid #FF6B6B;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 16px;">{search_type}</span>
                        <strong>{search_term}</strong>
                    </div>
                    <small style="color: #666;">{search['timestamp'][:16]}</small>
                </div>
            </div>
            """
            st.markdown(search_html, unsafe_allow_html=True)

    def perform_internal_search(self, query, categories, date_range, user_filter, user):
        """Perform internal data search"""
        results = []
        
        # Search in posts
        if "게시글" in categories:
            posts_results = self.search_posts(query, date_range, user_filter)
            results.extend(posts_results)
        
        # Search in assignments
        if "과제" in categories:
            assignment_results = self.search_assignments(query, date_range, user_filter)
            results.extend(assignment_results)
        
        # Search in users
        if "사용자" in categories:
            user_results = self.search_users(query)
            results.extend(user_results)
        
        # Search in quizzes
        if "퀴즈" in categories:
            quiz_results = self.search_quizzes(query, date_range)
            results.extend(quiz_results)
        
        # Search in votes
        if "투표" in categories:
            vote_results = self.search_votes(query, date_range)
            results.extend(vote_results)
        
        return results

    def search_posts(self, query, date_range, user_filter):
        """Search in posts"""
        posts_df = st.session_state.data_manager.load_csv('posts')
        results = []
        
        if posts_df.empty:
            return results
        
        # Apply filters
        filtered_posts = posts_df.copy()
        
        if user_filter != "전체":
            filtered_posts = filtered_posts[filtered_posts['author'] == user_filter]
        
        # Date filter
        if date_range != "전체":
            date_limit = self.get_date_limit(date_range)
            filtered_posts = filtered_posts[
                pd.to_datetime(filtered_posts['created_date']) >= date_limit
            ]
        
        # Search in title and content
        for _, post in filtered_posts.iterrows():
            if (query.lower() in str(post['title']).lower() or 
                query.lower() in str(post['content']).lower()):
                
                results.append({
                    'type': '게시글',
                    'title': post['title'],
                    'content': str(post['content'])[:200] + '...',
                    'author': post['author'],
                    'date': post['created_date'],
                    'id': post['id'],
                    'club': post.get('club', 'N/A')
                })
        
        return results

    def search_assignments(self, query, date_range, user_filter):
        """Search in assignments"""
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        results = []
        
        if assignments_df.empty:
            return results
        
        # Apply filters
        filtered_assignments = assignments_df.copy()
        
        if user_filter != "전체":
            filtered_assignments = filtered_assignments[filtered_assignments['creator'] == user_filter]
        
        # Date filter
        if date_range != "전체":
            date_limit = self.get_date_limit(date_range)
            filtered_assignments = filtered_assignments[
                pd.to_datetime(filtered_assignments['created_date']) >= date_limit
            ]
        
        # Search in title and description
        for _, assignment in filtered_assignments.iterrows():
            if (query.lower() in str(assignment['title']).lower() or 
                query.lower() in str(assignment['description']).lower()):
                
                results.append({
                    'type': '과제',
                    'title': assignment['title'],
                    'content': str(assignment['description'])[:200] + '...',
                    'author': assignment['creator'],
                    'date': assignment['created_date'],
                    'id': assignment['id'],
                    'club': assignment.get('club', 'N/A')
                })
        
        return results

    def search_users(self, query):
        """Search in users"""
        users_df = st.session_state.data_manager.load_csv('users')
        results = []
        
        if users_df.empty:
            return results
        
        # Search in username and name
        for _, user in users_df.iterrows():
            if (query.lower() in str(user['username']).lower() or 
                query.lower() in str(user['name']).lower()):
                
                results.append({
                    'type': '사용자',
                    'title': f"{user['name']} (@{user['username']})",
                    'content': f"역할: {user['role']}, 동아리: {user.get('club_name', 'N/A')}",
                    'author': 'System',
                    'date': user.get('created_date', 'N/A'),
                    'id': user['username'],
                    'club': user.get('club_name', 'N/A')
                })
        
        return results

    def search_quizzes(self, query, date_range):
        """Search in quizzes"""
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        results = []
        
        if quizzes_df.empty:
            return results
        
        # Apply date filter
        filtered_quizzes = quizzes_df.copy()
        if date_range != "전체":
            date_limit = self.get_date_limit(date_range)
            filtered_quizzes = filtered_quizzes[
                pd.to_datetime(filtered_quizzes['created_date']) >= date_limit
            ]
        
        # Search in title and description
        for _, quiz in filtered_quizzes.iterrows():
            if (query.lower() in str(quiz['title']).lower() or 
                query.lower() in str(quiz['description']).lower()):
                
                results.append({
                    'type': '퀴즈',
                    'title': quiz['title'],
                    'content': str(quiz['description'])[:200] + '...',
                    'author': quiz['creator'],
                    'date': quiz['created_date'],
                    'id': quiz['id'],
                    'club': quiz.get('club', 'N/A')
                })
        
        return results

    def search_votes(self, query, date_range):
        """Search in votes"""
        votes_df = st.session_state.data_manager.load_csv('votes')
        results = []
        
        if votes_df.empty:
            return results
        
        # Apply date filter
        filtered_votes = votes_df.copy()
        if date_range != "전체":
            date_limit = self.get_date_limit(date_range)
            filtered_votes = filtered_votes[
                pd.to_datetime(filtered_votes['created_date']) >= date_limit
            ]
        
        # Search in title and description
        for _, vote in filtered_votes.iterrows():
            if (query.lower() in str(vote['title']).lower() or 
                query.lower() in str(vote['description']).lower()):
                
                results.append({
                    'type': '투표',
                    'title': vote['title'],
                    'content': str(vote['description'])[:200] + '...',
                    'author': vote['creator'],
                    'date': vote['created_date'],
                    'id': vote['id'],
                    'club': vote.get('club', 'N/A')
                })
        
        return results

    def perform_web_search(self, query, search_engines, content_types):
        """Perform web search"""
        results = []
        
        # Simulated web search results (in real implementation, use APIs)
        search_urls = {
            "Google": f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=ko",
            "Naver": f"https://search.naver.com/search.naver?query={query.replace(' ', '+')}&where=nexearch",
            "Daum": f"https://search.daum.net/search?q={query.replace(' ', '+')}&DA=YZR",
            "Wikipedia": f"https://ko.wikipedia.org/wiki/{query.replace(' ', '_')}"
        }
        
        for engine in search_engines:
            if engine in search_urls:
                try:
                    url = search_urls[engine]
                    # Try to fetch content using trafilatura
                    downloaded = trafilatura.fetch_url(url)
                    if downloaded:
                        text = trafilatura.extract(downloaded)
                        if text:
                            results.append({
                                'engine': engine,
                                'title': f"{query} - {engine} 검색 결과",
                                'content': text[:500] + '...',
                                'url': url,
                                'type': '웹 검색 결과'
                            })
                except Exception as e:
                    results.append({
                        'engine': engine,
                        'title': f"{engine} 검색 링크",
                        'content': f"{query}에 대한 {engine} 검색을 수행하려면 아래 링크를 클릭하세요.",
                        'url': url,
                        'type': '검색 링크',
                        'error': str(e)
                    })
        
        return results

    def display_search_results(self, results, query):
        """Display internal search results"""
        if not results:
            st.info(f"'{query}'에 대한 검색 결과가 없습니다.")
            return
        
        st.markdown(f"##### 🔍 '{query}' 검색 결과 ({len(results)}개)")
        
        for result in results:
            result_html = f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #FF6B6B; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <span style="background: #FF6B6B; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">
                                {result['type']}
                            </span>
                            <span style="background: #e9ecef; padding: 3px 8px; border-radius: 12px; font-size: 11px;">
                                {result['club']}
                            </span>
                        </div>
                        <h4 style="margin: 0 0 10px 0; color: #333;">{result['title']}</h4>
                        <p style="color: #666; margin: 10px 0; line-height: 1.5;">{result['content']}</p>
                        <div style="font-size: 12px; color: #888;">
                            <span>작성자: {result['author']}</span>
                            <span style="margin-left: 15px;">날짜: {result['date']}</span>
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(result_html, unsafe_allow_html=True)

    def display_web_search_results(self, results, query):
        """Display web search results"""
        if not results:
            st.info(f"'{query}'에 대한 웹 검색 결과가 없습니다.")
            return
        
        st.markdown(f"##### 🌐 '{query}' 웹 검색 결과")
        
        for result in results:
            result_html = f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #17a2b8; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <span style="background: #17a2b8; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">
                                {result['engine']}
                            </span>
                        </div>
                        <h4 style="margin: 0 0 10px 0; color: #333;">{result['title']}</h4>
                        <p style="color: #666; margin: 10px 0; line-height: 1.5;">{result['content']}</p>
                        <a href="{result['url']}" target="_blank" style="color: #17a2b8; text-decoration: none;">
                            🔗 링크에서 더 보기
                        </a>
                    </div>
                </div>
            </div>
            """
            st.markdown(result_html, unsafe_allow_html=True)

    def get_date_limit(self, date_range):
        """Get date limit for filtering"""
        now = datetime.now()
        
        if date_range == "오늘":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "일주일":
            return now - pd.Timedelta(days=7)
        elif date_range == "한달":
            return now - pd.Timedelta(days=30)
        elif date_range == "3개월":
            return now - pd.Timedelta(days=90)
        else:
            return pd.Timestamp.min

    def get_all_users(self):
        """Get list of all users"""
        users_df = st.session_state.data_manager.load_csv('users')
        if users_df.empty:
            return []
        return users_df['username'].tolist()