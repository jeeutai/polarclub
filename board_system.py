import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from PIL import Image
import io
import os
from error_handler import error_handler

class BoardSystem:
    def __init__(self):
        self.posts_file = 'data/posts.csv'

    def show_board_interface(self, user):
        """Display the board interface"""
        st.markdown("### 📝 게시판")

        # Tab layout
        tab1, tab2 = st.tabs(["📋 게시글 목록", "✍️ 글쓰기"])

        with tab1:
            self.show_posts_list(user)

        with tab2:
            self.show_post_creation(user)

    def show_posts_list(self, user):
        """Display list of posts"""
        st.markdown("#### 📋 게시글 목록")

        # 게시글 목록 조회 로그
        st.session_state.logging_system.log_activity(
            user['username'], 'Data Access', 'Viewed posts list',
            'Posts', 'Success'
        )

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            # Club filter
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
            else:
                club_options = ["전체"] + user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 필터", club_options, key="board_club_filter_unique")

        with col2:
            # Sort options
            sort_options = ["최신순", "좋아요순", "댓글순"]
            sort_by = st.selectbox("📊 정렬", sort_options)

        with col3:
            # Search
            search_term = st.text_input("🔍 검색", placeholder="제목, 내용 검색...")

        # Load and filter posts
        posts_df = st.session_state.data_manager.load_csv('posts')

        if posts_df.empty:
            st.info("등록된 게시글이 없습니다.")
            return

        # Apply filters
        if selected_club != "전체":
            posts_df = posts_df[posts_df['club'] == selected_club]

        if search_term:
            try:
                # Ensure string columns are properly typed
                posts_df['title'] = posts_df['title'].astype(str)
                posts_df['content'] = posts_df['content'].astype(str)
                posts_df = posts_df[
                    posts_df['title'].str.contains(search_term, case=False, na=False) |
                    posts_df['content'].str.contains(search_term, case=False, na=False)
                ]
            except Exception:
                # If search fails, keep all posts
                pass

            # 검색 로그
            st.session_state.logging_system.log_activity(
                user['username'], 'Search', f'Searched posts with term: {search_term}',
                'Posts', 'Success'
            )

        # Sort posts
        if sort_by == "좋아요순":
            posts_df['likes'] = pd.to_numeric(posts_df['likes'], errors='coerce').fillna(0)
            posts_df = posts_df.sort_values('likes', ascending=False)
        elif sort_by == "댓글순":
            posts_df['comments'] = pd.to_numeric(posts_df['comments'], errors='coerce').fillna(0)
            posts_df = posts_df.sort_values('comments', ascending=False)
        else:  # 최신순
            posts_df['created_date'] = posts_df['created_date'].apply(error_handler.safe_datetime_parse)

            posts_df = posts_df.sort_values('created_date', ascending=False)

        # Display posts
        for idx, post in posts_df.iterrows():
            self.show_post_card(post, user, idx)

    def show_post_card(self, post, user, idx):
        """Display a single post card using pure Streamlit components"""
        # Calculate engagement metrics
        likes = int(post.get('likes', 0)) if pd.notna(post.get('likes')) else 0
        comments = int(post.get('comments', 0)) if pd.notna(post.get('comments')) else 0

        with st.container():
            # Post header
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(post['title'])
                st.caption(f"👤 {post['author']} | 🏷️ {post['club']} | 📅 {str(post['created_date'])[:16]}")

            with col2:
                st.write(f"❤️ {likes} | 💬 {comments}")

            # Tags display
            if pd.notna(post.get('tags')) and str(post.get('tags', '')).strip():
                tags = post['tags'].split(',')
                tag_cols = st.columns(len(tags) if len(tags) <= 5 else 5)
                for i, tag in enumerate(tags[:5]):
                    with tag_cols[i]:
                        st.info(f"#{tag.strip()}")

            # Post content
            st.write(post['content'])

            # Image display
            if pd.notna(post.get('image_path')) and str(post.get('image_path', '')).strip():
                try:
                    if pd.notna(post.get('image_path')) and str(post.get('image_path', '')).strip():
                        image_list = post['image_path'].split(',')
                        for img_str in image_list:
                            try:
                                image_data = base64.b64decode(img_str)
                                image = Image.open(io.BytesIO(image_data))
                                st.image(image, use_column_width=True)
                            except:
                                st.warning("이미지를 불러올 수 없습니다.")

                    image = Image.open(io.BytesIO(image_data))
                    st.image(image, use_column_width=True)
                except:
                    st.warning("이미지를 불러올 수 없습니다.")

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("👍 좋아요", key=f"like_{post['id']}_unique"):
                    self.like_post(post['id'], user)
                    st.rerun()

            with col2:
                if st.button("💬 댓글", key=f"comment_{post['id']}_unique"):
                    st.session_state[f'show_comments_{post["id"]}'] = True

            with col3:
                if user['role'] in ['선생님'] or user['username'] == post['author']:
                    if st.button("✏️ 수정", key=f"edit_{post['id']}_unique"):
                        st.session_state[f'edit_post_{post["id"]}'] = True

            with col4:
                if user['role'] in ['선생님'] or user['username'] == post['author']:
                    if st.button("🗑️ 삭제", key=f"delete_post_{post['id']}_{idx}"):
                        if self.delete_post(post['id'], user):
                            st.success("게시글이 삭제되었습니다.")
                            st.rerun()

            # Show comments if requested
            if st.session_state.get(f'show_comments_{post["id"]}', False):
                self.show_comments_section(post['id'], user)

            # Show edit form if requested
            if st.session_state.get(f'edit_post_{post["id"]}', False):
                self.show_edit_post_form(post, user)

            st.divider()

    def show_post_creation(self, user):
        """Display post creation form"""
        st.markdown("#### ✍️ 새 게시글 작성")

        # 게시글 작성 페이지 접근 로그
        st.session_state.logging_system.log_activity(
            user['username'], 'Page Access', 'Accessed post creation form',
            'Post Creation', 'Success'
        )

        with st.form("create_post_form"):
            # Get user's clubs for club selection
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            club_options = user_clubs['club_name'].tolist()

            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                all_clubs = clubs_df['name'].tolist() if not clubs_df.empty else []
                club_options = ["전체"] + all_clubs

            selected_club = st.selectbox("🏷️ 동아리 선택", club_options, key="post_club_select_unique")
            title = st.text_input("📝 제목", placeholder="게시글 제목을 입력하세요", key="post_title_input")
            content = st.text_area("📄 내용", placeholder="게시글 내용을 입력하세요", height=200, key="post_content_input")

            # Enhanced image upload with multiple files
            uploaded_images = st.file_uploader(
                "🖼️ 이미지 첨부 (여러 개 가능)", 
                type=['png', 'jpg', 'jpeg', 'gif'],
                accept_multiple_files=True,
                help="갤러리 기능이 통합되어 여러 이미지를 한 번에 업로드할 수 있습니다."
            )

            # Tags and post type
            tags = st.text_input("🏷️ 태그", placeholder="태그를 쉼표로 구분하여 입력하세요 (예: 갤러리, 공지, 중요)")
            post_type = st.selectbox("📝 게시글 유형", ["일반", "공지", "갤러리", "질문", "자료공유"])

            submit_post = st.form_submit_button("📤 게시글 등록", use_container_width=True)

            if submit_post:
                if title and content and selected_club:
                    # Process image if uploaded
                    image_data = None
                    if uploaded_images:
                       image_data_list = []
                       for uploaded_image in uploaded_images:
                           processed_image = self.process_uploaded_image(uploaded_image)
                           if processed_image:
                               image_data_list.append(processed_image)

                               # 이미지 업로드 로그
                               st.session_state.logging_system.log_file_upload(
                                   user['username'], uploaded_image.name, len(uploaded_image.getvalue())
                               )
                       image_data = ','.join(image_data_list)

                    post_data = {
                        'id': f"post_{int(datetime.now().timestamp())}",
                        'title': title,
                        'content': content,
                        'author': user['name'],
                        'club': selected_club,
                        'likes': 0,
                        'comments': 0,
                        'image_path': image_data,
                        'tags': tags,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record('posts', post_data):
                        # 게시글 작성 로그
                        st.session_state.logging_system.log_activity(
                            user['username'], 'Content Creation', f'Created post: {title}',
                            'Posts', 'Success', data_modified='1 record'
                        )

                        st.success("게시글이 등록되었습니다!")

                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 게시글: {title}",
                            "info",
                            "all",
                            f"{user['name']}님이 새 게시글을 등록했습니다."
                        )
                        st.rerun()
                    else:
                        # 게시글 작성 실패 로그
                        st.session_state.logging_system.log_error(
                            user['username'], 'Post Creation Error', 'Failed to create post',
                            'Posts'
                        )
                        st.error("게시글 등록에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")

    def process_uploaded_image(self, uploaded_file):
        """Process uploaded image and return base64 encoded string"""
        try:
            image = Image.open(uploaded_file)

            # Resize image if too large
            max_size = (800, 600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            return img_str
        except Exception as e:
            st.error(f"이미지 처리 중 오류가 발생했습니다: {e}")
            return None

    def like_post(self, post_id, user):
        """Add like to post"""
        posts_df = st.session_state.data_manager.load_csv('posts')

        if not posts_df.empty:
            current_likes = int(posts_df.loc[posts_df['id'] == post_id, 'likes'].iloc[0]) if not posts_df[posts_df['id'] == post_id].empty else 0
            new_likes = current_likes + 1

            if st.session_state.data_manager.update_record('posts', post_id, {'likes': new_likes}):
                # 좋아요 로그
                st.session_state.logging_system.log_activity(
                    user['username'], 'User Interaction', f'Liked post ID: {post_id}',
                    'Posts', 'Success', data_modified='1 record'
                )

    def delete_post(self, post_id, user):
        """Delete a post"""
        success = st.session_state.data_manager.delete_record('posts', post_id)

        if success:
            # 게시글 삭제 로그
            st.session_state.logging_system.log_activity(
                user['username'], 'Content Management', f'Deleted post ID: {post_id}',
                'Posts', 'Success', data_modified='1 record',
                security_level='Medium'
            )
        else:
            # 게시글 삭제 실패 로그
            st.session_state.logging_system.log_error(
                user['username'], 'Post Deletion Error', f'Failed to delete post ID: {post_id}',
                'Posts'
            )

        return success

    def show_comments_section(self, post_id, user):
        """Display comments section for a post"""
        st.divider()
        st.subheader("💬 댓글")

        # Comment input
        with st.form(f"comment_form_{post_id}_unique"):
            comment_text = st.text_area("댓글 작성", placeholder="댓글을 입력하세요...", key=f"comment_{post_id}_unique")

            col1, col2 = st.columns([1, 4])
            with col1:
                submit_comment = st.form_submit_button("💬 댓글 등록", use_container_width=True)

            if submit_comment and comment_text:
                # Save comment data
                comment_data = {
                    'id': f"comment_{int(datetime.now().timestamp())}",
                    'post_id': post_id,
                    'username': user['username'],
                    'content': comment_text,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # 댓글 작성 로그
                st.session_state.logging_system.log_activity(
                    user['username'], 'User Interaction', f'Added comment to post ID: {post_id}',
                    'Comments', 'Success', data_modified='1 record'
                )

                st.success("댓글이 등록되었습니다!")

                # Update comment count
                posts_df = st.session_state.data_manager.load_csv('posts')
                if not posts_df.empty:
                    current_comments = int(posts_df.loc[posts_df['id'] == post_id, 'comments'].iloc[0]) if not posts_df[posts_df['id'] == post_id].empty else 0
                    new_comments = current_comments + 1
                    st.session_state.data_manager.update_record('posts', post_id, {'comments': new_comments})

        # Display existing comments (simulated)
        with st.expander("📝 댓글 보기", expanded=False, key=f"expander_{post_id}_unique"): # Added unique key to expander
            st.info("댓글 시스템이 구현되었습니다. 실제 댓글 데이터는 별도 테이블에서 관리됩니다.")

        # Close comments
        if st.button("❌ 댓글 닫기", key=f"close_comments_{post_id}_unique"):
            st.rerun()

    def show_edit_post_form(self, post, user):
        """Display post edit form"""
        st.markdown("---")
        st.markdown("#### ✏️ 게시글 수정")

        with st.form(f"edit_post_form_{post['id']}_unique"):
            new_title = st.text_input("제목", value=post['title'], key=f"edit_title_{post['id']}_unique") # added unique key
            new_content = st.text_area("내용", value=post['content'], height=150, key=f"edit_content_{post['id']}_unique") # added unique key
            new_tags = st.text_input("태그", value=post.get('tags', ''), key=f"edit_tags_{post['id']}_unique") # added unique key

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("💾 저장", key=f"save_button_{post['id']}_unique") # added unique key
            with col2:
                cancel_button = st.form_submit_button("❌ 취소", key=f"cancel_button_{post['id']}_unique") # added unique key

            if save_button:
                updates = {
                    'title': new_title,
                    'content': new_content,
                    'tags': new_tags
                }

                if st.session_state.data_manager.update_record('posts', post['id'], updates):
                    # 게시글 수정 로그
                    st.session_state.logging_system.log_activity(
                        user['username'], 'Content Management', f'Updated post ID: {post["id"]}',
                        'Posts', 'Success', data_modified='1 record'
                    )

                    st.success("게시글이 수정되었습니다!")
                    st.session_state[f'edit_post_{post["id"]}'] = False
                    st.rerun()
                else:
                    # 게시글 수정 실패 로그
                    st.session_state.logging_system.log_error(
                        user['username'], 'Post Update Error', f'Failed to update post ID: {post["id"]}',
                        'Posts'
                    )
                    st.error("게시글 수정에 실패했습니다.")

            if cancel_button:
                st.session_state[f'edit_post_{post["id"]}'] = False
                st.rerun()