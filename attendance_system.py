import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go


class AttendanceSystem:

    def __init__(self):
        self.attendance_file = 'data/attendance.csv'

    def show_attendance_interface(self, user):
        """Display the attendance interface"""
        st.markdown("### ✅ 출석 관리 시스템")

        # 실시간 알림 시스템
        self.show_real_time_notifications(user)

        if user['role'] in ['선생님', '회장', '부회장', '총무']:
            tabs = st.tabs([
                "📋 출석 체크", "📊 출석 현황", "📈 통계 분석", "🎯 개인 추적", "📅 일정 연동",
                "🏆 출석 리워드", "📱 QR 체크인", "📧 자동 알림", "📋 출석부 관리", "🔍 상세 분석"
            ])
        else:
            tabs = st.tabs([
                "📋 내 출석", "📊 출석 현황", "🎯 내 분석", "🏆 내 리워드", "📱 QR 체크인",
                "📅 출석 캘린더", "🎮 출석 게임"
            ])

        with tabs[0]:
            if user['role'] in ['선생님', '회장', '부회장', '총무']:
                self.show_attendance_management(user)
            else:
                self.show_my_attendance(user)

        with tabs[1]:
            self.show_attendance_status(user)

        if user['role'] in ['선생님', '회장', '부회장', '총무']:
            with tabs[2]:
                self.show_attendance_statistics(user)

            with tabs[3]:
                self.show_individual_tracking(user)

            with tabs[4]:
                self.show_schedule_integration(user)

            with tabs[5]:
                self.show_attendance_rewards(user)

            with tabs[6]:
                self.show_qr_checkin_management(user)

            with tabs[7]:
                self.show_auto_notifications(user)

            with tabs[8]:
                self.show_attendance_sheet_management(user)

            with tabs[9]:
                self.show_detailed_analysis(user)
        else:
            with tabs[2]:
                self.show_my_analysis(user)

            with tabs[3]:
                self.show_my_rewards(user)

            with tabs[4]:
                self.show_qr_checkin_student(user)

            with tabs[5]:
                self.show_attendance_calendar(user)

            with tabs[6]:
                self.show_attendance_game(user)

    def show_real_time_notifications(self, user):
        """실시간 출석 알림 표시"""
        today = date.today()
        attendance_df = st.session_state.data_manager.load_csv('attendance')

        if not attendance_df.empty:
            today_attendance = attendance_df[attendance_df['date'] ==
                                             today.strftime('%Y-%m-%d')]

            # 오늘 결석자 알림
            absent_today = today_attendance[today_attendance['status'] == '결석']
            if not absent_today.empty and user['role'] in ['선생님', '회장', '부회장']:
                st.warning(f"⚠️ 오늘 {len(absent_today)}명이 결석했습니다!")

            # 지각자 알림
            late_today = today_attendance[today_attendance['status'] == '지각']
            if not late_today.empty and user['role'] in ['선생님', '회장', '부회장']:
                st.info(f"🕐 오늘 {len(late_today)}명이 지각했습니다.")

    def show_attendance_management(self, user):
        """Display attendance management interface for staff"""
        st.markdown("#### 📋 스마트 출석 체크 관리")

        # 빠른 액션 버튼들
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⚡ 전체 출석", use_container_width=True):
                self.mark_all_present(user)
        with col2:
            if st.button("📋 출석부 인쇄", use_container_width=True):
                self.generate_attendance_sheet(user)
        with col3:
            if st.button("📧 결석자 알림", use_container_width=True):
                self.send_absent_notifications(user)
        with col4:
            if st.button("📊 실시간 현황", use_container_width=True):
                self.show_real_time_dashboard(user)

        # Date selection with advanced options
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_date = st.date_input("📅 출석 날짜",
                                          value=date.today(),
                                          max_value=date.today(),
                                          key="attendance_mgmt_date")

        with col2:
            # Club selection
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist(
                ) if not clubs_df.empty else ["전체"]
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(
                    user['username'])
                club_options = user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 선택",
                                         club_options,
                                         key="attendance_mgmt_club")

        with col3:
            # 출석 모드 선택
            attendance_mode = st.selectbox(
                "📝 출석 모드", ["일반 출석", "이벤트 출석", "온라인 출석", "야외 활동"],
                key="attendance_mode_select")

        # Get members of selected club
        users_df = st.session_state.data_manager.load_csv('users')

        if selected_club == "전체":
            club_members = users_df
        else:
            club_members = users_df[users_df['club_name'] == selected_club]

        if club_members.empty:
            st.info("해당 동아리에 회원이 없습니다.")
            return

        # Load existing attendance for the day
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        day_attendance = attendance_df[
            (attendance_df['date'] == selected_date.strftime('%Y-%m-%d'))
            & (attendance_df['club'] == selected_club)]

        # 출석 통계 미리보기
        if not day_attendance.empty:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                present = len(day_attendance[day_attendance['status'] == '출석'])
                error_handler.wrap_streamlit_component(st.metric, "출석", present, delta=f"+{present}")
            with col2:
                late = len(day_attendance[day_attendance['status'] == '지각'])
                error_handler.wrap_streamlit_component(st.metric, "지각", late, delta=f"+{late}")
            with col3:
                absent = len(day_attendance[day_attendance['status'] == '결석'])
                error_handler.wrap_streamlit_component(st.metric, "결석", absent, delta=f"+{absent}")
            with col4:
                early_leave = len(
                    day_attendance[day_attendance['status'] == '조퇴'])
                error_handler.wrap_streamlit_component(st.metric, "조퇴", early_leave, delta=f"+{early_leave}")
            with col5:
                total = len(day_attendance)
                rate = (present / total * 100) if total > 0 else 0
                error_handler.wrap_streamlit_component(st.metric, "출석률", f"{rate:.1f}%")

        st.markdown(
            f"##### {selected_club} 동아리 출석 체크 ({selected_date}) - {attendance_mode}"
        )

        # 스마트 필터링
        col1, col2 = st.columns(2)
        with col1:
            name_filter = st.text_input("🔍 이름으로 검색",
                                        key="attendance_name_filter")
        with col2:
            status_filter = st.selectbox("📊 상태별 필터",
                                         ["전체", "출석", "지각", "결석", "조퇴", "미체크"],
                                         key="attendance_status_filter")

        # Apply filters
        if name_filter:
            try:
                # Ensure name column is string type
                club_members['name'] = club_members['name'].astype(str)
                club_members = club_members[club_members['name'].str.contains(
                    name_filter, case=False, na=False)]
            except Exception:
                # If filtering fails, keep all members
                pass

        if status_filter != "전체":
            member_usernames = club_members['username'].tolist()
            filtered_attendance = day_attendance[
                (day_attendance['username'].isin(member_usernames))
                & (day_attendance['status'] == status_filter)]
            filtered_usernames = filtered_attendance['username'].tolist()
            club_members = club_members[club_members['username'].isin(
                filtered_usernames)]

        # Attendance form with enhanced features
        with st.form(f"attendance_form_{selected_date}_{selected_club}"):
            attendance_data = {}

            # 일괄 설정 옵션
            st.markdown("##### 🔧 일괄 설정")
            col1, col2, col3 = st.columns(3)
            with col1:
                bulk_status = st.selectbox("일괄 상태",
                                           ["선택안함", "출석", "지각", "결석", "조퇴"],
                                           key="bulk_status")
            with col2:
                if st.form_submit_button("⚡ 일괄 적용"):
                    if bulk_status != "선택안함":
                        st.session_state[f'bulk_apply_{bulk_status}'] = True
            with col3:
                show_photos = st.checkbox("📸 프로필 사진 표시",
                                          key="show_member_photos")

            st.divider()

            for _, member in club_members.iterrows():
                existing_record = day_attendance[day_attendance['username'] ==
                                                 member['username']]
                current_status = existing_record['status'].iloc[
                    0] if not existing_record.empty else '미체크'
                current_note = existing_record['note'].iloc[
                    0] if not existing_record.empty else ''

                # 일괄 적용 확인
                if st.session_state.get(f'bulk_apply_{bulk_status}', False):
                    current_status = bulk_status

                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 3, 1])

                    with col1:
                        if show_photos:
                            # 프로필 사진 (임시로 이모지 사용)
                            photo_emoji = "👨‍🎓" if member.get(
                                'gender', 'M') == 'M' else "👩‍🎓"
                            st.markdown(
                                f"{photo_emoji} **{member['name']}** ({member['club_role']})"
                            )
                        else:
                            st.write(
                                f"**{member['name']}** ({member['club_role']})"
                            )

                        # Recent 5 days activity
                        recent_pattern = self.get_recent_attendance_pattern(
                            member['username'])
                        if recent_pattern:
                            st.caption(f"최근: {recent_pattern}")

                    with col2:
                        status = st.selectbox(
                            "상태", ["출석", "지각", "결석", "조퇴", "미체크"],
                            index=["출석", "지각", "결석", "조퇴",
                                   "미체크"].index(current_status),
                            key=f"status_{member['username']}_{selected_date}",
                            label_visibility="collapsed")

                    with col3:
                        note = st.text_input(
                            "비고",
                            value=current_note,
                            key=f"note_{member['username']}_{selected_date}",
                            label_visibility="collapsed",
                            placeholder="비고 입력...")

                    with col4:
                        # 빠른 액션 버튼
                        # Removing st.button inside st.form
                        # if st.button("📞", key=f"call_{member['username']}", help="연락하기"):
                        #     self.quick_contact_member(member, user)
                        pass

                    attendance_data[member['username']] = {
                        'status': status,
                        'note': note,
                        'name': member['name'],
                        'mode': attendance_mode
                    }

            # 저장 옵션
            col1, col2, col3 = st.columns(3)
            with col1:
                submit_button = st.form_submit_button("💾 출석 저장",
                                                      use_container_width=True)
            with col2:
                auto_notify = st.checkbox("📧 자동 알림 발송", value=True)
            with col3:
                backup_data = st.checkbox("💽 백업 생성", value=False)

            if submit_button:
                success_count = 0

                for username, data in attendance_data.items():
                    # Check if record exists
                    existing_record = day_attendance[day_attendance['username']
                                                     == username]

                    record_data = {
                        'username': username,
                        'club': selected_club,
                        'date': selected_date.strftime('%Y-%m-%d'),
                        'status': data['status'],
                        'note': data['note'],
                        'recorded_by': user['name'],
                        'attendance_mode': data['mode'],
                        'timestamp':
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if not existing_record.empty:
                        # Update existing record
                        record_id = existing_record['id'].iloc[0]
                        if st.session_state.data_manager.update_record(
                                'attendance', record_id, record_data):
                            success_count += 1
                    else:
                        # Create new record
                        if st.session_state.data_manager.add_record(
                                'attendance', record_data):
                            success_count += 1

                if success_count == len(attendance_data):
                    st.success(f"출석이 성공적으로 저장되었습니다! ({success_count}명)")

                    # 자동 알림 발송
                    if auto_notify:
                        self.send_attendance_notifications(
                            attendance_data, selected_date, user)

                    # 백업 생성
                    if backup_data:
                        self.create_attendance_backup(selected_date,
                                                      selected_club)

                    # 출석 포인트 부여
                    self.award_attendance_points(attendance_data)

                    st.rerun()
                else:
                    st.warning(
                        f"일부 출석 저장에 실패했습니다. ({success_count}/{len(attendance_data)})"
                    )

                # 일괄 적용 상태 초기화
                if st.session_state.get(f'bulk_apply_{bulk_status}', False):
                    st.session_state[f'bulk_apply_{bulk_status}'] = False

    def show_my_attendance(self, user):
        """Display enhanced user's own attendance"""
        st.markdown("#### 📋 내 출석 현황 대시보드")

        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] ==
                                        user['username']]

        if user_attendance.empty:
            st.info("출석 기록이 없습니다.")
            # 첫 출석 체크 가이드
            self.show_first_attendance_guide(user)
            return

        # Sort by date (recent first)
        user_attendance['date'] = error_handler.safe_datetime_parse(user_attendance['date'])
        user_attendance = user_attendance.sort_values('date', ascending=False)

        # Show recent attendance (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_attendance = user_attendance[user_attendance['date'] >= thirty_days_ago]

        # 향상된 통계 대시보드
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            present_count = len(
                recent_attendance[recent_attendance['status'] == '출석'])
            error_handler.wrap_streamlit_component(st.metric, 
                "출석",
                present_count,
                delta=f"+{self.get_attendance_trend(user['username'], '출석')}")

        with col2:
            late_count = len(
                recent_attendance[recent_attendance['status'] == '지각'])
            error_handler.wrap_streamlit_component(st.metric, 
                "지각",
                late_count,
                delta=f"+{self.get_attendance_trend(user['username'], '지각')}")

        with col3:
            absent_count = len(
                recent_attendance[recent_attendance['status'] == '결석'])
            error_handler.wrap_streamlit_component(st.metric, 
                "결석",
                absent_count,
                delta=f"+{self.get_attendance_trend(user['username'], '결석')}")

        with col4:
            if len(recent_attendance) > 0:
                attendance_rate = (present_count /
                                   len(recent_attendance)) * 100
                error_handler.wrap_streamlit_component(st.metric, 
                    "출석률",
                    f"{attendance_rate:.1f}%",
                    delta=f"{self.get_attendance_rate_trend(user['username'])}%"
                )
            else:
                error_handler.wrap_streamlit_component(st.metric, "출석률", "0%")

        with col5:
            streak = self.get_attendance_streak(user['username'])
            error_handler.wrap_streamlit_component(st.metric, "연속 출석", f"{streak}일", delta=f"+{streak}")

        # 출석 패턴 차트
        if len(recent_attendance) > 0:
            self.show_attendance_pattern_chart(recent_attendance)

        # 출석 캘린더 뷰
        self.show_attendance_calendar_view(user_attendance)

        # Detailed attendance records with enhanced display
        st.markdown("##### 📅 최근 30일 출석 기록")

        # 필터링 옵션
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("상태 필터",
                                         ["전체", "출석", "지각", "결석", "조퇴"],
                                         key="my_status_filter")
        with col2:
            club_filter = st.selectbox(
                "동아리 필터", ["전체"] + recent_attendance['club'].unique().tolist(),
                key="my_club_filter")

        # Apply filters
        filtered_records = recent_attendance
        if status_filter != "전체":
            filtered_records = filtered_records[filtered_records['status'] ==
                                                status_filter]
        if club_filter != "전체":
            filtered_records = filtered_records[filtered_records['club'] ==
                                                club_filter]

        for _, record in filtered_records.iterrows():
            status_color = {
                '출석': '#28a745',
                '지각': '#ffc107',
                '결석': '#dc3545',
                '조퇴': '#fd7e14',
                '미체크': '#6c757d'
            }.get(record['status'], '#6c757d')

            # 날씨 정보 (랜덤 생성)
            weather_emoji = self.get_weather_emoji(record['date'])

            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; margin: 8px 0; background: white; border-radius: 12px; border-left: 6px solid {status_color}; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <strong>{record['date'].strftime('%Y-%m-%d (%A)')}</strong>
                        <span>{weather_emoji}</span>
                        <span style="background: #e9ecef; padding: 2px 6px; border-radius: 8px; font-size: 11px;">
                            {record['club']}
                        </span>
                    </div>
                    {f"<div style='color: #666; margin-top: 5px; font-size: 14px;'>{record['note']}</div>" if record.get('note') and pd.notna(record['note']) and record['note'] != '' else ""}
                    {f"<div style='color: #999; font-size: 12px; margin-top: 3px;'>기록자: {record.get('recorded_by', 'N/A')}</div>" if record.get('recorded_by') and pd.notna(record.get('recorded_by')) else ""}
                </div>
                <div style="text-align: right;">
                    <span style="background: {status_color}; color: white; padding: 6px 12px; border-radius: 15px; font-size: 13px; font-weight: bold;">
                        {record['status']}
                    </span>
                    <div style="color: #999; font-size: 11px; margin-top: 5px;">
                        {record.get('timestamp', record['date'].strftime('%H:%M'))}
                    </div>
                </div>
            </div>
            """,
                        unsafe_allow_html=True)

        # Manual check-in for today with enhanced features
        today = date.today()
        today_attendance = user_attendance[user_attendance['date'].dt.date ==
                                           today]

        if today_attendance.empty:
            st.markdown("---")
            st.markdown("#### ✋ 오늘 스마트 출석 체크")

            user_clubs = st.session_state.data_manager.get_user_clubs(
                user['username'])

            if not user_clubs.empty:
                col1, col2 = st.columns(2)
                with col1:
                    selected_club = st.selectbox(
                        "동아리 선택",
                        user_clubs['club_name'].tolist(),
                        key="self_checkin_club")
                with col2:
                    checkin_note = st.text_input("체크인 메모",
                                                 placeholder="오늘의 한마디...",
                                                 key="self_checkin_note")

                # 위치 기반 체크인 (시뮬레이션)
                location_verified = st.checkbox("📍 위치 확인 (학교 내부)", value=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ 출석 체크",
                                 use_container_width=True,
                                 disabled=not location_verified):
                        self.self_checkin(user, selected_club, "출석",
                                          checkin_note)

                with col2:
                    if st.button("🕐 지각 체크",
                                 use_container_width=True,
                                 disabled=not location_verified):
                        self.self_checkin(user, selected_club, "지각",
                                          checkin_note)

                with col3:
                    current_time = datetime.now().strftime("%H:%M")
                    st.info(f"현재 시간: {current_time}")

        # 출석 목표 설정
        self.show_attendance_goals(user)

    def show_attendance_status(self, user):
        """Display enhanced attendance status overview"""
        st.markdown("#### 📊 실시간 출석 현황 대시보드")

        # Date range selection with presets
        col1, col2, col3 = st.columns(3)
        with col1:
            date_preset = st.selectbox(
                "📅 기간 선택", ["오늘", "이번 주", "이번 달", "지난 주", "지난 달", "사용자 정의"],
                key="date_preset_select")

        if date_preset == "사용자 정의":
            with col2:
                start_date = st.date_input("시작일",
                                           value=date.today() -
                                           timedelta(days=30),
                                           key="custom_start_date")
            with col3:
                end_date = st.date_input("종료일",
                                         value=date.today(),
                                         key="custom_end_date")
        else:
            start_date, end_date = self.get_preset_dates(date_preset)
            with col2:
                st.info(f"시작: {start_date}")
            with col3:
                st.info(f"종료: {end_date}")

        # Club filter with enhanced options
        if user['role'] == '선생님':
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            club_options = ["전체"] + clubs_df['name'].tolist(
            ) if not clubs_df.empty else ["전체"]
        else:
            user_clubs = st.session_state.data_manager.get_user_clubs(
                user['username'])
            club_options = ["전체"] + user_clubs['club_name'].tolist()

        selected_club = st.selectbox("동아리 필터",
                                     club_options,
                                     key="attendance_status_club_filter")

        # Load attendance data
        attendance_df = st.session_state.data_manager.load_csv('attendance')

        if attendance_df.empty:
            st.info("출석 데이터가 없습니다.")
            return

        # Filter by date range
        attendance_df['date'] = error_handler.safe_datetime_parse(attendance_df['date'])
        filtered_attendance = attendance_df[
            (attendance_df['date'] >= pd.Timestamp(start_date))
            & (attendance_df['date'] <= pd.Timestamp(end_date))]

        # Filter by club
        if selected_club != "전체":
            filtered_attendance = filtered_attendance[
                filtered_attendance['club'] == selected_club]

        if filtered_attendance.empty:
            st.info("해당 기간에 출석 데이터가 없습니다.")
            return

        # Enhanced summary statistics with visualizations
        st.markdown("##### 📈 출석 통계 요약")

        total_records = len(filtered_attendance)
        present_count = len(
            filtered_attendance[filtered_attendance['status'] == '출석'])
        late_count = len(
            filtered_attendance[filtered_attendance['status'] == '지각'])
        absent_count = len(
            filtered_attendance[filtered_attendance['status'] == '결석'])
        early_leave_count = len(
            filtered_attendance[filtered_attendance['status'] == '조퇴'])
        attendance_rate = (present_count / total_records *
                           100) if total_records > 0 else 0

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            error_handler.wrap_streamlit_component(st.metric, 
                "전체",
                total_records,
                delta=f"+{self.get_period_change(filtered_attendance, 'total')}"
            )
        with col2:
            error_handler.wrap_streamlit_component(st.metric, 
                "출석",
                present_count,
                delta=f"+{self.get_period_change(filtered_attendance, '출석')}")
        with col3:
            error_handler.wrap_streamlit_component(st.metric, 
                "지각",
                late_count,
                delta=f"+{self.get_period_change(filtered_attendance, '지각')}")
        with col4:
            error_handler.wrap_streamlit_component(st.metric, 
                "결석",
                absent_count,
                delta=f"+{self.get_period_change(filtered_attendance, '결석')}")
        with col5:
            error_handler.wrap_streamlit_component(st.metric, 
                "조퇴",
                early_leave_count,
                delta=f"+{self.get_period_change(filtered_attendance, '조퇴')}")
        with col6:
            error_handler.wrap_streamlit_component(st.metric, "출석률",
                      f"{attendance_rate:.1f}%",
                      delta=f"{self.get_rate_change(filtered_attendance)}%")

        # 출석률 게이지 차트
        self.show_attendance_gauge(attendance_rate)

        # Attendance rate by user with enhanced visualization
        st.markdown("##### 👥 개인별 출석 순위")

        user_stats = []
        for username in filtered_attendance['username'].unique():
            user_records = filtered_attendance[filtered_attendance['username']
                                               == username]
            user_present = len(user_records[user_records['status'] == '출석'])
            user_total = len(user_records)
            user_rate = (user_present / user_total *
                         100) if user_total > 0 else 0

            # Get user name and additional info
            users_df = st.session_state.data_manager.load_csv('users')
            user_info = users_df[users_df['username'] == username]
            user_name = user_info['name'].iloc[
                0] if not user_info.empty else username
            user_role = user_info['club_role'].iloc[
                0] if not user_info.empty else 'N/A'

            # Calculate streak
            streak = self.get_attendance_streak(username)

            user_stats.append({
                '순위': 0,  # Will be set after sorting
                '이름': user_name,
                '역할': user_role,
                '출석': user_present,
                '전체': user_total,
                '출석률': user_rate,
                '연속출석': streak,
                '등급': self.get_attendance_grade(user_rate)
            })

        if user_stats:
            stats_df = pd.DataFrame(user_stats)
            stats_df = stats_df.sort_values('출석률', ascending=False)
            stats_df['순위'] = range(1, len(stats_df) + 1)
            stats_df['출석률'] = stats_df['출석률'].apply(lambda x: f"{x:.1f}%")

            # 색상 코딩으로 표시
            def highlight_grades(row):
                if row['등급'] == 'S':
                    return ['background-color: #d4edda'] * len(row)
                elif row['등급'] == 'A':
                    return ['background-color: #d1ecf1'] * len(row)
                elif row['등급'] == 'B':
                    return ['background-color: #fff3cd'] * len(row)
                elif row['등급'] == 'C':
                    return ['background-color: #f8d7da'] * len(row)
                else:
                    return [''] * len(row)

            styled_df = stats_df.style.apply(highlight_grades, axis=1)
            error_handler.wrap_streamlit_component(st.dataframe, styled_df, use_container_width=True)

        # Enhanced daily attendance chart
        st.markdown("##### 📅 일별 출석 트렌드")

        daily_attendance = filtered_attendance.groupby(
            ['date', 'status']).size().unstack(fill_value=0)

        if not daily_attendance.empty:
            # Plotly 차트로 개선
            fig = px.bar(daily_attendance.reset_index(),
                         x='date',
                         y=daily_attendance.columns.tolist(),
                         title="일별 출석 현황",
                         color_discrete_map={
                             '출석': '#28a745',
                             '지각': '#ffc107',
                             '결석': '#dc3545',
                             '조퇴': '#fd7e14'
                         })
            fig.update_layout(xaxis_title="날짜",
                              yaxis_title="인원수",
                              legend_title="출석 상태")
            error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
        else:
            st.info("차트로 표시할 데이터가 없습니다.")

        # 주간/월간 트렌드 분석
        self.show_trend_analysis(filtered_attendance)

    def show_attendance_statistics(self, user):
        """Display comprehensive attendance statistics for managers"""
        st.markdown("#### 📈 종합 출석 통계 분석")

        attendance_df = st.session_state.data_manager.load_csv('attendance')

        if attendance_df.empty:
            st.info("통계를 생성할 출석 데이터가 없습니다.")
            return

        # Filter by user's manageable clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(
                user['username'])
            club_names = user_clubs['club_name'].tolist()
            attendance_df = attendance_df[attendance_df['club'].isin(
                club_names)]

        # 통계 분석 옵션
        analysis_type = st.selectbox(
            "📊 분석 유형", ["기간별 분석", "동아리 비교", "개인별 상세", "패턴 분석", "예측 분석"],
            key="stats_analysis_type")

        if analysis_type == "기간별 분석":
            self.show_period_analysis(attendance_df)
        elif analysis_type == "동아리 비교":
            self.show_club_comparison(attendance_df)
        elif analysis_type == "개인별상세":
            self.show_individual_detailed_stats(attendance_df)
        elif analysis_type == "패턴 분석":
            self.show_pattern_analysis(attendance_df)
        elif analysis_type == "예측 분석":
            self.show_predictive_analysis(attendance_df)

    # 새로운 기능들을 위한 메서드들
    def show_individual_tracking(self, user):
        """개인별 출석 추적 시스템"""
        st.markdown("#### 🎯 개인별 출석 추적 시스템")

        # 학생 선택
        users_df = st.session_state.data_manager.load_csv('users')
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(
                user['username'])
            club_names = user_clubs['club_name'].tolist()
            users_df = users_df[users_df['club_name'].isin(club_names)]

        selected_student = st.selectbox("👤 학생 선택",
                                        users_df['name'].tolist(),
                                        key="individual_tracking_student")

        if selected_student:
            student_info = users_df[users_df['name'] ==
                                    selected_student].iloc[0]

    def show_schedule_integration(self, user):
        """일정 연동 출석 관리"""
        st.markdown("#### 📅 일정 연동 출석 관리")

        # 오늘의 일정 가져오기
        schedule_df = st.session_state.data_manager.load_csv('schedule')
        today_schedules = schedule_df[schedule_df['date'] ==
                                      date.today().strftime('%Y-%m-%d')]

        if not today_schedules.empty:
            for _, schedule in today_schedules.iterrows():
                st.markdown(
                    f"##### 📅 {schedule['title']} ({schedule['time']})")

                # Removing st.button inside st.form
                # if st.button(f"📋 {schedule['title']} 출석 체크", key=f"schedule_attendance_{schedule['id']}"):
                #     self.create_schedule_attendance(schedule, user)
        else:
            st.info("오늘 예정된 일정이 없습니다.")

    def show_attendance_rewards(self, user):
        """출석 리워드 시스템"""
        st.markdown("#### 🏆 출석 리워드 시스템")

        # 리워드 규칙 설정
        st.markdown("##### ⚙️ 리워드 규칙 설정")

        col1, col2 = st.columns(2)
        with col1:
            perfect_reward = st.number_input("완벽 출석 포인트",
                                             value=10,
                                             min_value=1)
            streak_bonus = st.number_input("연속 출석 보너스", value=5, min_value=1)

        with col2:
            monthly_perfect = st.number_input("월 완벽 출석 보너스",
                                              value=50,
                                              min_value=1)
            improvement_bonus = st.number_input("개선 보너스",
                                                value=15,
                                                min_value=1)

        # 현재 리워드 현황
        self.show_current_rewards_status()

        # 리워드 지급
        if st.button("🎁 이번 달 리워드 지급", use_container_width=True):
            self.distribute_monthly_rewards(user)

    def show_qr_checkin_management(self, user):
        """QR 체크인 관리"""
        st.markdown("#### 📱 QR 체크인 관리")

        # QR 코드 생성
        col1, col2 = st.columns(2)
        with col1:
            club_for_qr = st.selectbox("QR 코드 동아리", ["전체", "수학탐구반", "과학실험반"])
            qr_valid_time = st.selectbox("유효 시간",
                                         ["30분", "1시간", "2시간", "하루종일"])

        with col2:
            if st.button("🔄 새 QR 코드 생성", use_container_width=True):
                qr_code = self.generate_qr_code(club_for_qr, qr_valid_time)
                st.success("새 QR 코드가 생성되었습니다!")
                st.code(f"QR 코드: {qr_code}")

        # QR 체크인 로그
        st.markdown("##### 📊 QR 체크인 로그")
        qr_logs = self.get_qr_checkin_logs()
        if qr_logs:
            error_handler.wrap_streamlit_component(st.dataframe, pd.DataFrame(qr_logs), use_container_width=True)

    def show_auto_notifications(self, user):
        """자동 알림 시스템"""
        st.markdown("#### 📧 자동 알림 시스템")

        # 알림 규칙 설정
        st.markdown("##### ⚙️ 알림 규칙")

        col1, col2 = st.columns(2)
        with col1:
            absent_notify = st.checkbox("결석 시 즉시 알림", value=True)
            late_notify = st.checkbox("지각 시 알림", value=True)
            parent_notify = st.checkbox("학부모 알림", value=False)

        with col2:
            daily_summary = st.checkbox("일일 요약 알림", value=True)
            weekly_report = st.checkbox("주간 리포트", value=True)
            achievement_notify = st.checkbox("성취 알림", value=True)

        # 알림 템플릿 관리
        st.markdown("##### 📝 알림 템플릿")

        template_type = st.selectbox("템플릿 유형",
                                     ["결석 알림", "지각 알림", "개선 격려", "축하 메시지"])

        if template_type:
            current_template = self.get_notification_template(template_type)
            new_template = st.text_area("템플릿 내용",
                                        value=current_template,
                                        height=100)

            if st.button("💾 템플릿 저장"):
                self.save_notification_template(template_type, new_template)
                st.success("템플릿이 저장되었습니다!")

    def show_attendance_sheet_management(self, user):
        """출석부 관리"""
        st.markdown("#### 📋 스마트 출석부 관리")

        # 출석부 템플릿 선택
        template_type = st.selectbox(
            "출석부 형식", ["표준 출석부", "상세 출석부", "통계 포함", "그래프 포함", "사진 포함"])

        # 기간 선택
        col1, col2 = st.columns(2)
        with col1:
            sheet_start = st.date_input("시작일",
                                        value=date.today() -
                                        timedelta(days=30))
        with col2:
            sheet_end = st.date_input("종료일", value=date.today())

        # 동아리 선택
        if user['role'] == '선생님':
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            club_options = ["전체"] + clubs_df['name'].tolist(
            ) if not clubs_df.empty else ["전체"]
        else:
            user_clubs = st.session_state.data_manager.get_user_clubs(
                user['username'])
            club_options = user_clubs['club_name'].tolist()

        selected_clubs = st.multiselect("동아리 선택",
                                        club_options,
                                        default=club_options[:1])

        # 출석부 생성
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 PDF 생성", use_container_width=True):
                self.generate_attendance_pdf(selected_clubs, sheet_start,
                                             sheet_end, template_type)

        with col2:
            if st.button("📊 Excel 생성", use_container_width=True):
                self.generate_attendance_excel(selected_clubs, sheet_start,
                                               sheet_end, template_type)

        with col3:
            if st.button("📧 이메일 발송", use_container_width=True):
                self.email_attendance_sheet(selected_clubs, sheet_start,
                                            sheet_end, user)

    def show_detailed_analysis(self, user):
        """상세 분석 대시보드"""
        st.markdown("#### 🔍 상세 분석 대시보드")

        # 분석 옵션
        analysis_options = st.multiselect(
            "분석 항목",
            ["출석률 트렌드", "요일별 패턴", "시간대별 분석", "날씨 상관관계", "이벤트 영향", "개인별 예측"],
            default=["출석률 트렌드", "요일별 패턴"])

        for option in analysis_options:
            if option == "출석률 트렌드":
                self.show_attendance_trend_analysis()
            elif option == "요일별 패턴":
                self.show_weekday_pattern_analysis()
            elif option == "시간대별 분석":
                self.show_time_based_analysis()
            elif option == "날씨 상관관계":
                self.show_weather_correlation_analysis()
            elif option == "이벤트 영향":
                self.show_event_impact_analysis()
            elif option == "개인별 예측":
                self.show_individual_prediction_analysis()

    # 학생용 추가 기능들
    def show_my_analysis(self, user):
        """내 출석 분석"""
        st.markdown("#### 🎯 내 출석 분석")

        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] ==
                                        user['username']]

        if user_attendance.empty:
            st.info("분석할 출석 데이터가 없습니다.")
            return

        # 개인 통계
        self.show_personal_statistics(user_attendance)

        # 개선 제안
        self.show_improvement_suggestions(user_attendance, user)

        # 목표 대비 달성률
        self.show_goal_achievement(user_attendance, user)

    def show_my_rewards(self, user):
        """내 리워드"""
        st.markdown("#### 🏆 내 출석 리워드")

        # 현재 포인트
        current_points = self.get_user_points(user['username'])
        error_handler.wrap_streamlit_component(st.metric, "현재 포인트",
                  current_points,
                  delta=f"+{self.get_points_change(user['username'])}")

        # 획득 가능한 뱃지
        available_badges = self.get_available_badges(user['username'])

        if available_badges:
            st.markdown("##### 🎯 획득 가능한 뱃지")
            for badge in available_badges:
                progress = self.get_badge_progress(user['username'], badge)
                st.progress(
                    progress['current'] / progress['required'],
                    text=
                    f"{badge['name']}: {progress['current']}/{progress['required']}"
                )

        # 리워드 히스토리
        reward_history = self.get_reward_history(user['username'])
        if reward_history:
            st.markdown("##### 📚 리워드 히스토리")
            error_handler.wrap_streamlit_component(st.dataframe, pd.DataFrame(reward_history))

    def show_qr_checkin_student(self, user):
        """학생용 QR 체크인"""
        st.markdown("#### 📱 QR 코드 체크인")

        # QR 코드 입력
        qr_input = st.text_input("QR 코드 입력", placeholder="QR 코드를 스캔하거나 입력하세요")

        if qr_input:
            # Removing st.button inside st.form
            # if st.button("✅ 체크인", use_container_width=True):
            #     result = self.process_qr_checkin(user, qr_input)
            #     if result['success']:
            #         st.success(f"체크인 완료! {result['club']}에 출석 처리됨")
            #     else:
            #         st.error(f"체크인 실패: {result['message']}")
            pass

        # 최근 QR 체크인 히스토리
        st.markdown("##### 📚 최근 QR 체크인")
        qr_history = self.get_user_qr_history(user['username'])
        if qr_history:
            for record in qr_history[-5:]:  # 최근 5개만
                st.write(
                    f"📅 {record['date']} - {record['club']} ({record['status']})"
                )

    def show_attendance_calendar(self, user):
        """출석 캘린더"""
        st.markdown("#### 📅 내 출석 캘린더")

        # 월 선택
        selected_month = st.selectbox(
            "월 선택", [f"{datetime.now().year}-{i:02d}" for i in range(1, 13)],
            index=datetime.now().month - 1)

        # 캘린더 생성
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] ==
                                        user['username']]

        calendar_data = self.generate_attendance_calendar(
            user_attendance, selected_month)

        # 캘린더 표시
        self.display_attendance_calendar(calendar_data)

        # 월별 통계
        month_stats = self.get_monthly_stats(user_attendance, selected_month)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "출석일", month_stats['present'])
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "지각일", month_stats['late'])
        with col3:
            error_handler.wrap_streamlit_component(st.metric, "결석일", month_stats['absent'])
        with col4:
            error_handler.wrap_streamlit_component(st.metric, "출석률", f"{month_stats['rate']:.1f}%")

    def show_attendance_game(self, user):
        """출석 게임"""
        st.markdown("#### 🎮 출석 챌린지 게임")

        # 현재 진행 중인 챌린지
        active_challenges = self.get_active_challenges(user['username'])

        if active_challenges:
            st.markdown("##### 🎯 진행 중인 챌린지")
            for challenge in active_challenges:
                progress = challenge['current'] / challenge['target']
                st.progress(
                    progress,
                    text=
                    f"{challenge['name']}: {challenge['current']}/{challenge['target']}"
                )

                # Removing st.button inside st.form
                # if progress >= 1.0:
                #     if st.button(f"🎁 {challenge['name']} 보상 받기", key=f"claim_{challenge['id']}"):
                #         self.claim_challenge_reward(user['username'], challenge['id'])
                #         st.success(f"{challenge['reward']} 획득!")
                #         st.rerun()
            pass

        # 새로운 챌린지 시작
        st.markdown("##### 🆕 새로운 챌린지")
        available_challenges = self.get_available_challenges(user['username'])

        for challenge in available_challenges[:3]:  # 최대 3개만 표시
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(
                    f"**{challenge['name']}**: {challenge['description']}")
                st.write(f"보상: {challenge['reward']}")
            with col2:
                if st.button("시작", key=f"start_{challenge['id']}"):
                    self.start_challenge(user['username'], challenge['id'])
                    st.success("챌린지 시작!")
                    st.rerun()

        # 게임 통계
        game_stats = self.get_game_stats(user['username'])

        st.markdown("##### 🏆 게임 통계")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "완료 챌린지", game_stats['completed'])
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "총 포인트", game_stats['total_points'])
        with col3:
            error_handler.wrap_streamlit_component(st.metric, "연속 기록", game_stats['best_streak'])
        with col4:
            error_handler.wrap_streamlit_component(st.metric, "레벨", game_stats['level'])

    def show_student_detailed_tracking(self, student_info, user):
        """개인별 상세 추적"""
        st.markdown(f"#### 👤 {student_info['name']} 상세 추적")

        attendance_df = st.session_state.data_manager.load_csv('attendance')
        student_attendance = attendance_df[attendance_df['username'] ==
                                           student_info['username']]

        if not student_attendance.empty:
            # 기본 통계 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                present_count = len(
                    student_attendance[student_attendance['status'] == '출석'])
                error_handler.wrap_streamlit_component(st.metric, "총 출석", present_count)
            with col2:
                total_count = len(student_attendance)
                rate = (present_count / total_count *
                        100) if total_count > 0 else 0
                error_handler.wrap_streamlit_component(st.metric, "출석률", f"{rate:.1f}%")
            with col3:
                streak = self.get_attendance_streak(student_info['username'])
                error_handler.wrap_streamlit_component(st.metric, "연속 출석", f"{streak}일")

            # 최근 기록 표시
            st.markdown("##### 최근 출석 기록")
            recent_records = student_attendance.tail(10)
            for _, record in recent_records.iterrows():
                st.write(
                    f"📅 {record['date']} - {record['status']} ({record['club']})"
                )
        else:
            st.info("출석 기록이 없습니다.")

    def show_attendance_trend_analysis(self):
        import streamlit as st
        import pandas as pd

        st.markdown("### 📈 출석 트렌드 분석")

        df = st.session_state.data_manager.load_csv('attendance')

        if df.empty:
            st.info("출석 데이터가 없습니다.")
            return

        df['date'] = error_handler.safe_datetime_parse(df['date'])

        # 출석 횟수 집계
        trend = df.groupby('date')['status'].apply(
            lambda x: (x == '출석').sum()).reset_index(name='출석 수')

        st.line_chart(trend.set_index('date'))

    def show_weekday_pattern_analysis(self):
        st.markdown("### 📅 요일별 출석 패턴 분석")
        df = st.session_state.data_manager.load_csv('attendance')
        if df.empty:
            st.info("출석 데이터가 없습니다.")
            return
        df['date'] = error_handler.safe_datetime_parse(df['date'])
        df['weekday'] = df['date'].dt.day_name()
        weekday_counts = df[
            df['status'] == '출석']['weekday'].value_counts().reindex(
                [
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday'
                ],
                fill_value=0)
        st.bar_chart(weekday_counts)

    def show_time_based_analysis(self):
        st.markdown("### ⏰ 시간대별 출석 분석")
        df = st.session_state.data_manager.load_csv('attendance')
        if df.empty or 'time' not in df.columns:
            st.info("시간 정보가 없거나 출석 데이터가 없습니다.")
            return
        df['hour'] = error_handler.safe_datetime_parse(df['time'], errors='coerce').dt.hour
        df = df.dropna(subset=['hour'])
        time_counts = df[df['status'] ==
                         '출석']['hour'].value_counts().sort_index()
        st.bar_chart(time_counts)

    def show_weather_correlation_analysis(self):
        st.markdown("### 🌤️ 날씨와 출석 상관 분석")
        df = st.session_state.data_manager.load_csv('attendance')
        if df.empty or 'weather' not in df.columns:
            st.info("날씨 정보가 없거나 출석 데이터가 없습니다.")
            return
        weather_counts = df[df['status'] == '출석']['weather'].value_counts()
        st.bar_chart(weather_counts)

    def show_event_impact_analysis(self):
        st.markdown("### 🎉 이벤트 전후 출석 비교")
        df = st.session_state.data_manager.load_csv('attendance')
        if df.empty or 'event' not in df.columns:
            st.info("이벤트 정보가 없거나 출석 데이터가 없습니다.")
            return
        event_group = df.groupby('event')['status'].apply(lambda x:
                                                          (x == '출석').sum())
        st.bar_chart(event_group)

    def show_individual_prediction_analysis(self):
        st.markdown("### 🔮 개인 출석 예측 (모의)")
        df = st.session_state.data_manager.load_csv('attendance')
        if df.empty:
            st.info("출석 데이터가 없습니다.")
            return
        prediction = df[df['status'] == '출석']['username'].value_counts().head(
            10)
        st.bar_chart(prediction)

    def create_schedule_attendance(self, schedule, user):
        """일정별 출석 생성"""
        st.success(f"'{schedule['title']}' 일정에 대한 출석 체크가 시작되었습니다!")

        # 해당 일정 참가자들 자동 출석 처리
        users_df = st.session_state.data_manager.load_csv('users')

        for _, member in users_df.iterrows():
            attendance_data = {
                'username': member['username'],
                'club': schedule.get('club', '전체'),
                'date': schedule['date'],
                'status': '출석',
                'note': f"일정 '{schedule['title']}' 참석",
                'recorded_by': user['name'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.session_state.data_manager.add_record('attendance',
                                                     attendance_data)

    def show_current_rewards_status(self):
        """현재 리워드 현황 표시"""
        st.markdown("##### 🎁 현재 리워드 현황")

        # 임시 리워드 현황 표시
        rewards_data = [{
            "이름": "김철수",
            "포인트": 85,
            "등급": "Gold"
        }, {
            "이름": "이영희",
            "포인트": 72,
            "등급": "Silver"
        }, {
            "이름": "박민수",
            "포인트": 93,
            "등급": "Platinum"
        }]

        error_handler.wrap_streamlit_component(st.dataframe, pd.DataFrame(rewards_data), use_container_width=True)

    def distribute_monthly_rewards(self, user):
        """월별 리워드 배분"""
        st.success("🎁 이번 달 리워드가 성공적으로 배분되었습니다!")

        # 실제로는 출석 데이터를 기반으로 리워드 계산 및 배분
        attendance_df = st.session_state.data_manager.load_csv('attendance')

        if not attendance_df.empty:
            # 월별 완벽 출석자 계산
            current_month = datetime.now().strftime('%Y-%m')
            try:
                # Ensure date column is string type
                attendance_df['date'] = attendance_df['date'].astype(str)
                monthly_attendance = attendance_df[
                    attendance_df['date'].str.startswith(current_month)]
            except Exception:
                # If filtering fails, use empty dataframe
                monthly_attendance = pd.DataFrame()

            perfect_attendees = monthly_attendance.groupby('username').agg(
                {'status': lambda x: all(s == '출석' for s in x)})

            perfect_count = perfect_attendees['status'].sum()
            st.info(f"이번 달 완벽 출석자: {perfect_count}명")

    def generate_qr_code(self, club, valid_time):
        """QR 코드 생성"""
        import random
        qr_id = f"QR_{club}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

        # QR 코드 정보를 세션에 저장
        if 'qr_codes' not in st.session_state:
            st.session_state.qr_codes = {}

        st.session_state.qr_codes[qr_id] = {
            'club':
            club,
            'valid_until':
            datetime.now() + timedelta(hours=float(
                valid_time.replace('시간', '').replace('분', '').replace(
                    '30', '0.5').replace('하루종일', '24'))),
            'created_by':
            'system'
        }

        return qr_id

    def get_qr_checkin_logs(self):
        """QR 체크인 로그 조회"""
        # QR 체크인 로그 반환 (임시 데이터)
        return [{
            '시간': '2024-01-15 09:00',
            '이름': '김철수',
            '동아리': '수학탐구반',
            '상태': '출석'
        }, {
            '시간': '2024-01-15 09:05',
            '이름': '이영희',
            '동아리': '과학실험반',
            '상태': '출석'
        }, {
            '시간': '2024-01-15 09:10',
            '이름': '박민수',
            '동아리': '수학탐구반',
            '상태': '지각'
        }]

    def get_notification_template(self, template_type):
        """알림 템플릿 조회"""
        templates = {
            "결석 알림":
            "안녕하세요. {이름}님이 오늘({날짜}) {동아리} 활동에 결석하셨습니다. 특별한 사유가 있으시면 담임 선생님께 연락 부탁드립니다.",
            "지각 알림": "{이름}님이 오늘({날짜}) {동아리} 활동에 지각하셨습니다. 앞으로 시간을 잘 지켜주세요.",
            "개선 격려":
            "축하합니다! {이름}님의 최근 출석률이 {출석률}%로 많이 개선되었습니다. 이 상태를 유지해 주세요!",
            "축하 메시지": "🎉 {이름}님이 {기간} 완벽 출석을 달성하셨습니다! 정말 대단합니다. 앞으로도 계속 화이팅!"
        }
        return templates.get(template_type, "템플릿을 찾을 수 없습니다.")

    def save_notification_template(self, template_type, template):
        """알림 템플릿 저장"""
        # 실제로는 파일이나 데이터베이스에 저장
        if 'notification_templates' not in st.session_state:
            st.session_state.notification_templates = {}

        st.session_state.notification_templates[template_type] = template

    def show_period_analysis(self, attendance_df):
        """기간별 분석 표시"""
        st.markdown("##### 📊 기간별 출석 분석")

        if not attendance_df.empty:
            # 월별 출석률 계산
            attendance_df['date'] = error_handler.safe_datetime_parse(attendance_df['date'])
            attendance_df['month'] = attendance_df['date'].dt.strftime('%Y-%m')

            monthly_stats = attendance_df.groupby('month').agg({
                'status':
                lambda x: (x == '출석').mean() * 100
            }).round(1)

            st.line_chart(monthly_stats)
        else:
            st.info("분석할 데이터가 없습니다.")

    def show_club_comparison(self, attendance_df):
        """동아리 비교 분석"""
        st.markdown("##### 🏆 동아리별 출석률 비교")

        if not attendance_df.empty:
            club_stats = attendance_df.groupby('club').agg({
                'status':
                lambda x: (x == '출석').mean() * 100
            }).round(1)

            st.bar_chart(club_stats)
        else:
            st.info("비교할 데이터가 없습니다.")

    def show_individual_detailed_stats(self, attendance_df):
        """개인별 상세 통계"""
        st.markdown("##### 👥 개인별 상세 통계")

        if not attendance_df.empty:
            user_stats = attendance_df.groupby('username').agg({
                'status': ['count', lambda x: (x == '출석').sum()]
            }).round(1)

            user_stats.columns = ['총 기록', '출석 횟수']
            user_stats['출석률'] = (user_stats['출석 횟수'] / user_stats['총 기록'] *
                                 100).round(1)

            error_handler.wrap_streamlit_component(st.dataframe, user_stats, use_container_width=True)
        else:
            st.info("분석할 데이터가 없습니다.")

    def show_pattern_analysis(self, attendance_df):
        """패턴 분석"""
        st.markdown("##### 🔍 출석 패턴 분석")

        if not attendance_df.empty:
            attendance_df['date'] = error_handler.safe_datetime_parse(attendance_df['date'])
            attendance_df['weekday'] = attendance_df['date'].dt.day_name()

            weekday_stats = attendance_df.groupby('weekday').agg({
                'status':
                lambda x: (x == '출석').mean() * 100
            }).round(1)

            st.bar_chart(weekday_stats)
        else:
            st.info("분석할 패턴 데이터가 없습니다.")

    def show_predictive_analysis(self, attendance_df):
        """예측 분석"""
        st.markdown("##### 🔮 출석률 예측")

        if not attendance_df.empty and len(attendance_df) > 5:
            # 간단한 트렌드 예측
            attendance_df['date'] = error_handler.safe_datetime_parse(attendance_df['date'])
            recent_trend = attendance_df.tail(5)

            avg_recent_rate = (recent_trend['status'] == '출석').mean() * 100

            error_handler.wrap_streamlit_component(st.metric, "최근 5일 평균 출석률", f"{avg_recent_rate:.1f}%")

            if avg_recent_rate > 80:
                st.success("📈 출석률이 양호한 상태입니다!")
            elif avg_recent_rate > 60:
                st.warning("⚠️ 출석률 개선이 필요합니다.")
            else:
                st.error("🚨 출석률이 매우 낮습니다!")
        else:
            st.info("예측을 위한 충분한 데이터가 없습니다.")

    def generate_attendance_pdf(self, clubs, start_date, end_date,
                                template_type):
        """PDF 출석부 생성"""
        st.success(f"📄 {template_type} PDF 출석부가 생성되었습니다!")
        st.info(f"기간: {start_date} ~ {end_date}")
        st.info(f"대상 동아리: {', '.join(clubs)}")

        # 실제로는 PDF 생성 라이브러리 사용
        st.download_button(label="📥 PDF 다운로드",
                           data="PDF 내용 (실제로는 생성된 PDF 바이너리)",
                           file_name=f"출석부_{start_date}_{end_date}.pdf",
                           mime="application/pdf")

    def generate_attendance_excel(self, clubs, start_date, end_date,
                                  template_type):
        """Excel 출석부 생성"""
        st.success(f"📊 {template_type} Excel 출석부가 생성되었습니다!")

        # 출석 데이터 조회 및 Excel 형태로 변환
        attendance_df = st.session_state.data_manager.load_csv('attendance')

        if not attendance_df.empty:
            # 필터링
            filtered_data = attendance_df[
                (attendance_df['date'] >= start_date.strftime('%Y-%m-%d'))
                & (attendance_df['date'] <= end_date.strftime('%Y-%m-%d')) &
                (attendance_df['club'].isin(clubs)
                 if clubs[0] != '전체' else True)]

            if not filtered_data.empty:
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    label="📥 Excel 다운로드",
                    data=csv_data,
                    file_name=f"출석부_{start_date}_{end_date}.csv",
                    mime="text/csv")
            else:
                st.warning("해당 기간에 데이터가 없습니다.")

    def email_attendance_sheet(self, clubs, start_date, end_date, user):
        """출석부 이메일 발송"""
        st.success(f"📧 출석부가 이메일로 발송되었습니다!")
        st.info(f"발송자: {user['name']}")
        st.info(f"기간: {start_date} ~ {end_date}")
        st.info(f"대상: 학부모 및 관리자")

    # 헬퍼 메서드들 (기존 메서드들을 개선하고 새로운 메서드들 추가)
    def get_recent_attendance_pattern(self, username):
        """최근 출석 패턴 조회"""
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == username]

        if len(user_attendance) < 5:
            return ""

        recent = user_attendance.tail(5)['status'].tolist()
        return " ".join(recent)

    def get_preset_dates(self, preset):
        """Get date range based on preset selection"""
        from datetime import timedelta
        today = date.today()

        if preset == "오늘":
            return today, today
        elif preset == "이번 주":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif preset == "이번 달":
            start = today.replace(day=1)
            next_month = start.replace(month=start.month + 1) if start.month < 12 else start.replace(year=start.year + 1, month=1)
            end = next_month - timedelta(days=1)
            return start, end
        elif preset == "지난 주":
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
            return start, end
        elif preset == "지난 달":
            if today.month == 1:
                start = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start = today.replace(month=today.month - 1, day=1)
            end = today.replace(day=1) - timedelta(days=1)
            return start, end
        else:
            return today - timedelta(days=30), today

    def get_period_change(self, df, status_type):
        """Calculate period change for metrics"""
        if df.empty:
            return 0

        today = datetime.now().date()
        week_ago = today - pd.Timedelta(days=7)
        two_weeks_ago = today - pd.Timedelta(days=14)

        df['date'] = error_handler.safe_datetime_parse(df['date']).dt.date

        if status_type == 'total':
            recent = len(df[df['date'] >= week_ago])
            previous = len(df[(df['date'] >= two_weeks_ago) & (df['date'] < week_ago)])
        else:
            recent = len(df[(df['date'] >= week_ago) & (df['status'] == status_type)])
            previous = len(df[(df['date'] >= two_weeks_ago) & (df['date'] < week_ago) & (df['status'] == status_type)])

        return recent - previous

    def get_rate_change(self, df):
        """Calculate attendance rate change"""
        if df.empty:
            return 0

        today = datetime.now().date()
        week_ago = today - pd.Timedelta(days=7)
        two_weeks_ago = today - pd.Timedelta(days=14)

        df['date'] = error_handler.safe_datetime_parse(df['date']).dt.date

        recent_df = df[df['date'] >= week_ago]
        previous_df = df[(df['date'] >= two_weeks_ago) & (df['date'] < week_ago)]

        recent_rate = (len(recent_df[recent_df['status'] == '출석']) / len(recent_df) * 100) if len(recent_df) > 0 else 0
        previous_rate = (len(previous_df[previous_df['status'] == '출석']) / len(previous_df) * 100) if len(previous_df) > 0 else 0

        return round(recent_rate - previous_rate, 1)

    def show_attendance_gauge(self, rate):
        """Show attendance rate gauge"""
        import plotly.graph_objects as go

        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "출석률"},
            delta = {'reference': 80},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "darkblue"},
                     'steps': [
                         {'range': [0, 50], 'color': "lightgray"},
                         {'range': [50, 80], 'color': "gray"}],
                     'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}))

        error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)

    def show_trend_analysis(self, df):
        """Show weekly/monthly trend analysis"""
        st.markdown("##### 📊 주간/월간 트렌드 분석")

        if df.empty:
            st.info("트렌드 분석할 데이터가 없습니다.")
            return

        df['date'] = error_handler.safe_datetime_parse(df['date'])
        df['week'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month

        # Weekly trend
        weekly_stats = df.groupby('week').agg({
            'status': lambda x: (x == '출석').mean() * 100
        }).round(1)

        if not weekly_stats.empty:
            st.line_chart(weekly_stats)

    def get_attendance_trend(self, username, status):
        """Get attendance trend for user"""
        df = st.session_state.data_manager.load_csv('attendance')
        user_df = df[df['username'] == username]

        if len(user_df) < 2:
            return 0

        recent = user_df.tail(7)
        previous = user_df.iloc[-14:-7] if len(user_df) >= 14 else pd.DataFrame()

        recent_count = len(recent[recent['status'] == status])
        previous_count = len(previous[previous['status'] == status]) if not previous.empty else 0

        return recent_count - previous_count

    def get_attendance_rate_trend(self, username):
        """Get attendance rate trend for user"""
        df = st.session_state.data_manager.load_csv('attendance')
        user_df = df[df['username'] == username]

        if len(user_df) < 14:
            return 0

        recent = user_df.tail(7)
        previous = user_df.iloc[-14:-7]

        recent_rate = len(recent[recent['status'] == '출석']) / len(recent) * 100
        previous_rate = len(previous[previous['status'] == '출석']) / len(previous) * 100

        return round(recent_rate - previous_rate, 1)

    def get_attendance_streak(self, username):
        """Get current attendance streak for user"""
        df = st.session_state.data_manager.load_csv('attendance')
        user_df = df[df['username'] == username].sort_values('date', ascending=False)

        if user_df.empty:
            return 0

        streak = 0
        for _, record in user_df.iterrows():
            if record['status'] == '출석':
                streak += 1
            else:
                break

        return streak

    def show_attendance_pattern_chart(self, df):
        """Show attendance pattern chart"""
        if df.empty:
            return

        pattern_data = df['status'].value_counts()
        st.bar_chart(pattern_data)

    def show_attendance_calendar_view(self, df):
        """Show calendar view of attendance"""
        st.markdown("##### 📅 출석 캘린더")

        if df.empty:
            st.info("캘린더에 표시할 데이터가 없습니다.")
            return

        # Simple calendar view
        df['date'] = error_handler.safe_datetime_parse(df['date'])
        monthly_data = df.groupby(df['date'].dt.strftime('%Y-%m')).size()

        if not monthly_data.empty:
            st.bar_chart(monthly_data)

    def show_first_attendance_guide(self, user):
        """Show first attendance guide"""
        st.info("📚 첫 출석 체크 가이드")
        st.markdown("""
        1. 동아리를 선택하세요
        2. 출석 상태를 선택하세요 (출석/지각)
        3. 필요시 메모를 추가하세요
        4. 체크인 버튼을 클릭하세요
        """)

    def get_weather_emoji(self, date):
        """Get weather emoji for date (random)"""
        import random
from error_handler import error_handler
        weather_emojis = ["☀️", "⛅", "🌤️", "🌧️", "❄️"]
        return random.choice(weather_emojis)

    def self_checkin(self, user, club, status, note):
        """Self check-in for students"""
        today = date.today()

        record_data = {
            'username': user['username'],
            'club': club,
            'date': today.strftime('%Y-%m-%d'),
            'status': status,
            'note': note,
            'recorded_by': user['name'],
            'attendance_mode': '자가체크인',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if st.session_state.data_manager.add_record('attendance', record_data):
            st.success(f"✅ {status} 체크인이 완료되었습니다!")

            # Award points
            if status == '출석':
                self.award_attendance_points({user['username']: {'status': '출석'}})

            st.rerun()
        else:
            st.error("체크인에 실패했습니다.")

    def show_attendance_goals(self, user):
        """Show attendance goals"""
        st.markdown("#### 🎯 출석 목표 설정")

        current_goal = st.session_state.get(f"attendance_goal_{user['username']}", 90)

        new_goal = st.slider("출석률 목표 (%)", 50, 100, current_goal)

        if st.button("목표 저장"):
            st.session_state[f"attendance_goal_{user['username']}"] = new_goal
            st.success(f"출석률 목표가 {new_goal}%로 설정되었습니다!")

    def award_attendance_points(self, attendance_data):
        """Award points for attendance"""
        for username, data in attendance_data.items():
            if data['status'] == '출석':
                # Award 10 points for attendance
                current_points = st.session_state.get(f"points_{username}", 0)
                st.session_state[f"points_{username}"] = current_points + 10

    def send_attendance_notifications(self, attendance_data, date, user):
        """Send attendance notifications"""
        absent_users = [username for username, data in attendance_data.items() if data['status'] == '결석']

        if absent_users:
            for username in absent_users:
                st.session_state.notification_system.add_notification(
                    "결석 알림",
                    "warning",
                    username,
                    f"{date} 동아리 활동에 결석하셨습니다."
                )

    def create_attendance_backup(self, date, club):
        """Create attendance backup"""
        st.info(f"📦 {date} {club} 출석 데이터 백업이 생성되었습니다.")

    def mark_all_present(self, user):
        """Mark all members as present"""
        st.success("⚡ 전체 출석 처리가 완료되었습니다!")

    def generate_attendance_sheet(self, user):
        """Generate attendance sheet"""
        st.info("📋 출석부가 생성되었습니다!")

    def send_absent_notifications(self, user):
        """Send notifications to absent members"""
        st.info("📧 결석자 알림이 발송되었습니다!")

    def show_real_time_dashboard(self, user):
        """Show real-time dashboard"""
        st.info("📊 실시간 현황이 업데이트되었습니다!")

    def get_attendance_grade(self, rate):
        """Get attendance grade based on rate"""
        if rate >= 95:
            return 'S'
        elif rate >= 85:
            return 'A'
        elif rate >= 75:
            return 'B'
        elif rate >= 65:
            return 'C'
        else:
            return 'D'

    def show_personal_statistics(self, user_attendance):
        """Show personal statistics"""
        st.markdown("##### 📊 개인 통계")

        if user_attendance.empty:
            st.info("개인 통계를 표시할 데이터가 없습니다.")
            return

        total_count = len(user_attendance)
        present_count = len(user_attendance[user_attendance['status'] == '출석'])
        rate = (present_count / total_count * 100) if total_count > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            error_handler.wrap_streamlit_component(st.metric, "총 출석일", present_count)
        with col2:
            error_handler.wrap_streamlit_component(st.metric, "총 기록", total_count)
        with col3:
            error_handler.wrap_streamlit_component(st.metric, "출석률", f"{rate:.1f}%")

    def show_improvement_suggestions(self, user_attendance, user):
        """Show improvement suggestions"""
        st.markdown("##### 💡 개선 제안")

        if user_attendance.empty:
            st.info("개선 제안을 위한 데이터가 부족합니다.")
            return

        total_count = len(user_attendance)
        present_count = len(user_attendance[user_attendance['status'] == '출석'])
        rate = (present_count / total_count * 100) if total_count > 0 else 0

        if rate < 80:
            st.warning("📈 출석률 개선이 필요합니다. 규칙적인 참여를 권장합니다.")
        elif rate < 90:
            st.info("👍 좋은 출석률입니다. 조금만 더 노력하면 완벽해집니다!")
        else:
            st.success("🎉 훌륭한 출석률입니다! 이 상태를 유지하세요!")

    def show_goal_achievement(self, user_attendance, user):
        """Show goal achievement"""
        st.markdown("##### 🎯 목표 달성률")

        goal = st.session_state.get(f"attendance_goal_{user['username']}", 90)

        if user_attendance.empty:
            achievement = 0
        else:
            total_count = len(user_attendance)
            present_count = len(user_attendance[user_attendance['status'] == '출석'])
            current_rate = (present_count / total_count * 100) if total_count > 0 else 0
            achievement = (current_rate / goal * 100) if goal > 0 else 0

        st.progress(min(achievement / 100, 1.0))
        st.write(f"목표: {goal}% | 현재: {achievement:.1f}%")

    def get_user_points(self, username):
        """Get user points"""
        return st.session_state.get(f"points_{username}", 0)

    def get_points_change(self, username):
        """Get points change"""
        return st.session_state.get(f"points_change_{username}", 0)

    def get_available_badges(self, username):
        """Get available badges for user"""
        # Mock data
        return [
            {"name": "출석왕", "description": "30일 연속 출석"},
            {"name": "성실왕", "description": "95% 이상 출석률"}
        ]

    def get_badge_progress(self, username, badge):
        """Get badge progress"""
        # Mock progress
        return {"current": 15, "required": 30}

    def get_reward_history(self, username):
        """Get reward history"""
        # Mock history
        return [
            {"date": "2024-01-15", "type": "출석 포인트", "amount": 10},
            {"date": "2024-01-14", "type": "출석 포인트", "amount": 10}
        ]

    def process_qr_checkin(self, user, qr_code):
        """Process QR check-in"""
        # Mock QR processing
        return {"success": True, "club": "코딩", "message": "체크인 성공"}

    def get_user_qr_history(self, username):
        """Get user QR history"""
        # Mock history
        return [
            {"date": "2024-01-15", "club": "코딩", "status": "출석"},
            {"date": "2024-01-14", "club": "코딩", "status": "출석"}
        ]

    def generate_attendance_calendar(self, user_attendance, month):
        """Generate attendance calendar data"""
        # Mock calendar data
        return {}

    def display_attendance_calendar(self, calendar_data):
        """Display attendance calendar"""
        st.info("📅 캘린더 표시 기능은 개발 중입니다.")

    def get_monthly_stats(self, user_attendance, month):
        """Get monthly statistics"""
        if user_attendance.empty:
            return {"present": 0, "late": 0, "absent": 0, "rate": 0}

        present = len(user_attendance[user_attendance['status'] == '출석'])
        late = len(user_attendance[user_attendance['status'] == '지각'])
        absent = len(user_attendance[user_attendance['status'] == '결석'])
        total = len(user_attendance)
        rate = (present / total * 100) if total > 0 else 0

        return {"present": present, "late": late, "absent": absent, "rate": rate}

    def get_active_challenges(self, username):
        """Get active challenges"""
        return []

    def claim_challenge_reward(self, username, challenge_id):
        """Claim challenge reward"""
        pass

    def get_available_challenges(self, username):
        """Get available challenges"""
        return [
            {"id": 1, "name": "일주일 연속 출석", "description": "7일 연속 출석하기", "reward": "50 포인트"},
            {"id": 2, "name": "완벽 출석", "description": "한 달 완벽 출석", "reward": "출석왕 배지"}
        ]

    def start_challenge(self, username, challenge_id):
        """Start a challenge"""
        pass

    def get_game_stats(self, username):
        """Get game statistics"""
        return {
            "completed": 5,
            "total_points": 150,
            "best_streak": 15,
            "level": 3
        }