import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import io
from PIL import Image
from error_handler import error_handler

class PortfolioSystem:
    def __init__(self):
        self.portfolio_categories = [
            "프로그래밍 프로젝트",
            "창작 활동",
            "발표/프레젠테이션",
            "팀 프로젝트",
            "개인 작품",
            "학습 기록",
            "수상 내역",
            "자격증/인증서"
        ]

    def show_portfolio_interface(self, user):
        """Display portfolio management interface"""
        st.markdown("### 📁 포트폴리오")

        tabs = st.tabs(["📂 내 포트폴리오", "➕ 작품 추가", "🏆 우수 작품", "📊 통계"])

        with tabs[0]:
            self.show_my_portfolio(user)

        with tabs[1]:
            self.show_add_portfolio_item(user)

        with tabs[2]:
            self.show_featured_portfolios(user)

        with tabs[3]:
            self.show_portfolio_stats(user)

    def show_my_portfolio(self, user):
        """Display user's portfolio"""
        st.markdown("#### 📂 내 포트폴리오")

        # Get user's portfolio items
        portfolio_df = st.session_state.data_manager.load_csv('portfolio')
        if portfolio_df.empty:
            user_portfolio = pd.DataFrame()
        else:
            user_portfolio = portfolio_df[portfolio_df['username'] == user['username']]

        if user_portfolio.empty:
            st.info("아직 포트폴리오 항목이 없습니다. 작품을 추가해보세요!")
            return

        # Category filter
        categories = ["전체"] + self.portfolio_categories
        selected_category = st.selectbox("카테고리 필터", categories)

        # Apply filter
        if selected_category != "전체":
            user_portfolio = user_portfolio[user_portfolio['category'] == selected_category]

        # Sort by date
        if not user_portfolio.empty:
            user_portfolio = user_portfolio.sort_values('created_date', ascending=False)

        # Display portfolio items
        for idx, item in user_portfolio.iterrows():
            self.display_portfolio_item(item, user, editable=True)

    def display_portfolio_item(self, item, user, editable=False):
        """Display a single portfolio item"""
        # Status color
        status_colors = {
            "진행중": "#ffc107",
            "완료": "#28a745",
            "공개": "#17a2b8",
            "비공개": "#6c757d"
        }
        status_color = status_colors.get(item.get('status', ''), "#6c757d")

        # Handle tags safely
        tags = []
        if 'tags' in item and pd.notna(item['tags']) and str(item.get('tags', '')).strip():
            try:
                tags_str = str(item['tags']) if item['tags'] is not None else ""
                if tags_str and tags_str.strip() and tags_str.strip() != 'nan':
                    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            except Exception:
                tags = []

        tags_html = ""
        if tags:
            tags_html = "<div style='margin: 10px 0;'>"
            for tag in tags:
                if tag:
                    tags_html += f"<span style='background: #e9ecef; padding: 2px 6px; border-radius: 10px; font-size: 11px; margin-right: 5px;'>#{tag}</span>"
            tags_html += "</div>"

        # Handle image safely
        image_html = ""
        if 'image_path' in item and pd.notna(item['image_path']) and str(item.get('image_path', '')).strip():
            try:
                image_html = f"<img src='data:image/png;base64,{item['image_path']}' style='max-width: 100%; border-radius: 8px; margin: 10px 0;'>"
            except:
                image_html = ""

        # Handle technologies safely
        technologies_html = ""
        if 'technologies' in item and pd.notna(item['technologies']) and str(item.get('technologies', '')).strip():
            technologies_html = f"<div style='background: #f8f9fa; padding: 10px; border-radius: 8px; margin-top: 10px;'><strong>기술/도구:</strong> {item['technologies']}</div>"

        # Handle project URL safely
        url_html = ""
        if 'project_url' in item and pd.notna(item['project_url']) and str(item.get('project_url', '')).strip():
            url_html = f"<div style='margin-top: 10px;'><strong>🔗 링크:</strong> <a href='{item['project_url']}' target='_blank' style='color: #FF6B6B;'>{item['project_url']}</a></div>"

        portfolio_html = f"""
        <div style="background: white; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 6px solid {status_color}; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #333;">{item.get('title', 'No Title')}</h4>
                    <div style="margin: 10px 0;">
                        <span style="background: {status_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                            {item.get('status', 'Unknown')}
                        </span>
                        <span style="background: #e9ecef; padding: 4px 12px; border-radius: 15px; font-size: 12px; margin-left: 10px;">
                            {item.get('category', 'No Category')}
                        </span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <small style="color: #666;">{str(item.get('created_date', ''))[:10]}</small>
                </div>
            </div>

            <p style="color: #666; line-height: 1.6; margin: 15px 0;">{item.get('description', 'No description')}</p>
            {image_html}
            {tags_html}
            {technologies_html}
            {url_html}
        </div>
        """

        st.markdown(portfolio_html, unsafe_allow_html=True)

        if editable:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("✏️ 편집", key=f"edit_portfolio_{item.get('id', 'unknown')}_{item.get('username', 'unknown')}_{idx}"):
                    st.session_state[f'edit_portfolio_{item.get("id", "unknown")}'] = True

            with col2:
                if st.button("🗑️ 삭제", key=f"delete_portfolio_{item.get('id', 'unknown')}_{item.get('username', 'unknown')}_{idx}"):
                    if self.delete_portfolio_item(item.get('id')):
                        st.success("포트폴리오 항목이 삭제되었습니다.")
                        st.rerun()

            with col3:
                current_status = item.get('status', '비공개')
                new_status = "공개" if current_status == "비공개" else "비공개"
                if st.button(f"🔄 {new_status}", key=f"toggle_portfolio_{item.get('id', 'unknown')}_{item.get('username', 'unknown')}_{idx}"):
                    if hasattr(st.session_state.data_manager, 'update_record'):
                        if st.session_state.data_manager.update_record('portfolio', item.get('id'), {'status': new_status}):
                            st.success(f"상태가 {new_status}으로 변경되었습니다.")
                            st.rerun()

            with col4:
                if st.button("📤 공유", key=f"share_portfolio_{item.get('id', 'unknown')}_{item.get('username', 'unknown')}_{idx}"):
                    st.info(f"공유 링크: /portfolio/{item.get('id', 'unknown')}")

    def show_add_portfolio_item(self, user):
        """Display form to add new portfolio item"""
        st.markdown("#### ➕ 새 포트폴리오 항목 추가")

        with st.form("add_portfolio_form"):
            title = st.text_input("📝 제목", placeholder="프로젝트나 작품의 제목을 입력하세요")
            category = st.selectbox("📁 카테고리", self.portfolio_categories)
            description = st.text_area("📄 설명", placeholder="작품에 대한 상세한 설명을 입력하세요", height=150)

            col1, col2 = st.columns(2)
            with col1:
                technologies = st.text_input("🛠️ 사용 기술/도구", placeholder="Python, Streamlit, 등")
            with col2:
                status = st.selectbox("📊 상태", ["진행중", "완료", "공개", "비공개"])

            project_url = st.text_input("🔗 프로젝트 링크 (선택사항)", placeholder="GitHub, 웹사이트 등")
            tags = st.text_input("🏷️ 태그", placeholder="태그를 쉼표로 구분하여 입력 (예: 웹개발, AI, 팀프로젝트)")

            # Image upload
            uploaded_image = st.file_uploader(
                "🖼️ 대표 이미지", 
                type=['png', 'jpg', 'jpeg'],
                help="작품의 스크린샷이나 대표 이미지를 업로드하세요"
            )

            submit_button = st.form_submit_button("📤 포트폴리오 추가", use_container_width=True)

            if submit_button:
                if title and description and category:
                    # Process image if uploaded
                    image_data = None
                    if uploaded_image:
                        try:
                            image = Image.open(uploaded_image)
                            # Resize image to reasonable size
                            image.thumbnail((800, 600))
                            buffered = io.BytesIO()
                            image.save(buffered, format="PNG")
                            image_data = base64.b64encode(buffered.getvalue()).decode()
                        except Exception as e:
                            st.error(f"이미지 처리 중 오류가 발생했습니다: {e}")
                            image_data = None

                    portfolio_data = {
                        'username': user['username'],
                        'title': title,
                        'category': category,
                        'description': description,
                        'technologies': technologies,
                        'status': status,
                        'project_url': project_url,
                        'tags': tags,
                        'image_path': image_data if image_data else '',
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    try:
                        if st.session_state.data_manager.add_record('portfolio', portfolio_data):
                            st.success("포트폴리오 항목이 추가되었습니다!")

                            # Award badge for first portfolio item
                            portfolio_df = st.session_state.data_manager.load_csv('portfolio')
                            if not portfolio_df.empty:
                                user_portfolio_count = len(portfolio_df[portfolio_df['username'] == user['username']])
                                if user_portfolio_count == 1 and hasattr(st.session_state, 'gamification_system'):
                                    st.session_state.gamification_system.award_badge(user['username'], '창작자')

                            st.rerun()
                        else:
                            st.error("포트폴리오 추가에 실패했습니다.")
                    except Exception as e:
                        st.error(f"포트폴리오 추가 중 오류가 발생했습니다: {e}")
                else:
                    st.error("제목, 설명, 카테고리는 필수 항목입니다.")

    def show_featured_portfolios(self, user):
        """Display featured/public portfolios"""
        st.markdown("#### 🏆 우수 포트폴리오")

        portfolio_df = st.session_state.data_manager.load_csv('portfolio')

        if portfolio_df.empty:
            st.info("아직 공개된 포트폴리오가 없습니다.")
            return

        # Filter public portfolios
        public_portfolios = portfolio_df[portfolio_df['status'] == '공개']

        if public_portfolios.empty:
            st.info("공개된 포트폴리오가 없습니다.")
            return

        # Category filter
        categories = ["전체"] + self.portfolio_categories
        selected_category = st.selectbox("카테고리 필터", categories, key="featured_category")

        if selected_category != "전체":
            public_portfolios = public_portfolios[public_portfolios['category'] == selected_category]

        # Sort by created date
        if not public_portfolios.empty:
            public_portfolios = public_portfolios.sort_values('created_date', ascending=False)

        # Display portfolios
        for idx, item in public_portfolios.iterrows():
            # Get user info
            users_df = st.session_state.data_manager.load_csv('users')
            creator = users_df[users_df['username'] == item['username']] if not users_df.empty else pd.DataFrame()
            creator_name = creator.iloc[0]['name'] if not creator.empty else item['username']

            # Add creator info to item
            item_with_creator = item.copy()
            item_with_creator['creator_name'] = creator_name
            self.display_featured_portfolio_item(item_with_creator, user, idx)

    def display_featured_portfolio_item(self, item, user, idx):
        """Display a featured portfolio item"""
        # Handle tags safely
        tags = []
        if 'tags' in item and pd.notna(item['tags']) and str(item.get('tags', '')).strip():
            try:
                tags_str = str(item['tags']) if item['tags'] is not None else ""
                if tags_str and tags_str.strip() and tags_str.strip() != 'nan':
                    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            except Exception:
                tags = []

        tags_html = ""
        if tags:
            tags_html = "<div style='margin: 10px 0;'>"
            for tag in tags:
                if tag:
                    tags_html += f"<span style='background: #e9ecef; padding: 2px 6px; border-radius: 10px; font-size: 11px; margin-right: 5px;'>#{tag}</span>"
            tags_html += "</div>"

        # Handle image safely
        image_html = ""
        if 'image_path' in item and pd.notna(item['image_path']) and str(item.get('image_path', '')).strip():
            try:
                image_html = f"<img src='data:image/png;base64,{item['image_path']}' style='max-width: 100%; border-radius: 8px; margin: 10px 0;'>"
            except:
                image_html = ""

        # Handle technologies safely
        technologies_html = ""
        if 'technologies' in item and pd.notna(item['technologies']) and str(item.get('technologies', '')).strip():
            technologies_html = f"<div style='background: #f8f9fa; padding: 10px; border-radius: 8px; margin-top: 10px;'><strong>기술/도구:</strong> {item['technologies']}</div>"

        # Handle project URL safely
        url_html = ""
        if 'project_url' in item and pd.notna(item['project_url']) and str(item.get('project_url', '')).strip():
            url_html = f"<div style='margin-top: 10px;'><strong>🔗 링크:</strong> <a href='{item['project_url']}' target='_blank' style='color: #FF6B6B;'>{item['project_url']}</a></div>"

        portfolio_html = f"""
        <div style="background: white; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 6px solid #FF6B6B; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #333;">{item.get('title', 'No Title')}</h4>
                    <div style="margin: 10px 0;">
                        <span style="background: #17a2b8; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                            {item.get('category', 'No Category')}
                        </span>
                        <span style="color: #666; font-size: 14px; margin-left: 10px;">
                            👤 {item.get('creator_name', 'Unknown')}
                        </span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <small style="color: #666;">{str(item.get('created_date', ''))[:10]}</small>
                </div>
            </div>

            <p style="color: #666; line-height: 1.6; margin: 15px 0;">{item.get('description', 'No description')}</p>
            {image_html}
            {tags_html}
            {technologies_html}
            {url_html}
        </div>
        """

        st.markdown(portfolio_html, unsafe_allow_html=True)

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("👍 좋아요", key=f"like_featured_portfolio_{item.get('id', 'unknown')}_{user['username']}_{idx}"):
                st.success("좋아요를 눌렀습니다!")

        with col2:
            if st.button("💬 댓글", key=f"comment_featured_portfolio_{item.get('id', 'unknown')}_{user['username']}_{idx}"):
                st.info("댓글 기능은 준비 중입니다.")

        with col3:
            if st.button("📤 공유", key=f"share_featured_portfolio_{item.get('id', 'unknown')}_{user['username']}_{idx}"):
                st.info(f"공유 링크: /portfolio/{item.get('id', 'unknown')}")

        with col4:
            if user.get('role') == '선생님':
                if st.button("⭐ 추천", key=f"feature_portfolio_{item.get('id', 'unknown')}_{user['username']}_{idx}"):
                    st.success("우수 작품으로 추천되었습니다!")

    def show_portfolio_stats(self, user):
        """Display portfolio statistics"""
        st.markdown("#### 📊 포트폴리오 통계")

        portfolio_df = st.session_state.data_manager.load_csv('portfolio')

        if portfolio_df.empty:
            st.info("포트폴리오 데이터가 없습니다.")
            return

        # Overall stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_portfolios = len(portfolio_df)
            error_handler.wrap_streamlit_component(st.metric, "총 포트폴리오", total_portfolios)

        with col2:
            public_portfolios = len(portfolio_df[portfolio_df['status'] == '공개'])
            error_handler.wrap_streamlit_component(st.metric, "공개 포트폴리오", public_portfolios)

        with col3:
            user_portfolios = len(portfolio_df[portfolio_df['username'] == user['username']])
            error_handler.wrap_streamlit_component(st.metric, "내 포트폴리오", user_portfolios)

        with col4:
            categories_count = len(portfolio_df['category'].unique()) if 'category' in portfolio_df.columns else 0
            error_handler.wrap_streamlit_component(st.metric, "카테고리 수", categories_count)

        # Category distribution
        if 'category' in portfolio_df.columns:
            st.markdown("##### 📈 카테고리별 분포")
            category_counts = portfolio_df['category'].value_counts()

            if not category_counts.empty:
                chart_data = pd.DataFrame({
                    'category': category_counts.index,
                    'count': category_counts.values
                })
                st.bar_chart(chart_data.set_index('category'))

        # User rankings
        st.markdown("##### 🏆 포트폴리오 활발도 순위")
        if 'username' in portfolio_df.columns:
            user_portfolio_counts = portfolio_df['username'].value_counts().head(10)

            for i, (username, count) in enumerate(user_portfolio_counts.items()):
                # Get user info
                users_df = st.session_state.data_manager.load_csv('users')
                user_info = users_df[users_df['username'] == username] if not users_df.empty else pd.DataFrame()
                name = user_info.iloc[0]['name'] if not user_info.empty else username

                rank = i + 1
                is_current = username == user['username']
                rank_style = "background: linear-gradient(135deg, #FF6B6B, #ff8a80);" if is_current else "background: white;"

                rank_html = f"""
                <div style="{rank_style} padding: 15px; border-radius: 10px; margin: 8px 0; border: {'2px solid #FF6B6B' if is_current else '1px solid #dee2e6'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span style="background: #FF6B6B; color: white; padding: 8px 12px; border-radius: 50%; font-weight: bold;">{rank}</span>
                            <div>
                                <strong style="color: {'white' if is_current else '#333'};">{name}</strong>
                                <div style="color: {'rgba(255,255,255,0.8)' if is_current else '#666'}; font-size: 14px;">@{username}</div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: {'white' if is_current else '#28a745'}; font-weight: bold;">{count}개</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(rank_html, unsafe_allow_html=True)

    def delete_portfolio_item(self, item_id):
        """Delete a portfolio item"""
        try:
            return st.session_state.data_manager.delete_record('portfolio', item_id)
        except Exception as e:
            st.error(f"삭제 중 오류가 발생했습니다: {e}")
            return False

    def initialize_portfolio_csv(self):
        """Initialize portfolio CSV file if it doesn't exist"""
        portfolio_headers = [
            'id', 'username', 'title', 'category', 'description', 
            'technologies', 'status', 'project_url', 'tags', 
            'image_path', 'created_date'
        ]
        try:
            portfolio_df = st.session_state.data_manager.load_csv('portfolio')
            if portfolio_df.empty:
                empty_df = pd.DataFrame(columns=portfolio_headers)
                st.session_state.data_manager.save_csv('portfolio', empty_df)
        except Exception as e:
            # 오류가 발생해도 앱이 멈추지 않도록
            pass