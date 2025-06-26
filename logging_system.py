import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import hashlib
import socket
import numpy as np
import os
from error_handler import error_handler


class LoggingSystem:
    def __init__(self):
        self.logs_file = 'data/logs.csv'
        self._is_logging = False  # 재귀 방지 플래그
        # 세션 상태 확인 후 초기화
        if hasattr(st.session_state, 'data_manager'):
            self.initialize_logs()

    def initialize_logs(self):
        """Initialize logs CSV file"""
        if not hasattr(st.session_state, 'data_manager'):
            return

        logs_df = st.session_state.data_manager.load_csv('logs')
        if logs_df.empty:
            # Create logs with all required columns
            logs_structure = [
                'id', 'timestamp', 'username', 'user_name', 'user_role', 'club_name',
                'ip_address', 'session_id', 'activity_type', 'activity_description',
                'target_resource', 'action_result', 'error_message', 'user_agent',
                'device_type', 'browser_info', 'request_method', 'response_time',
                'data_modified', 'security_level', 'notes'
            ]
            empty_df = pd.DataFrame(columns=logs_structure)
            st.session_state.data_manager.save_csv('logs', empty_df)

    def get_client_info(self):
        """Get client information for logging"""
        try:
            # Get IP address (simplified for Streamlit)
            ip_address = "127.0.0.1"  # Default for local development

            # Generate session ID
            session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]

            # Device and browser info (simplified)
            user_agent = "Streamlit App"
            device_type = "Desktop"
            browser_info = "Browser Detection N/A"

            return {
                'ip_address': ip_address,
                'session_id': session_id,
                'user_agent': user_agent,
                'device_type': device_type,
                'browser_info': browser_info
            }
        except Exception:
            return {
                'ip_address': '127.0.0.1',
                'session_id': 'unknown',
                'user_agent': 'Unknown',
                'device_type': 'Unknown',
                'browser_info': 'Unknown'
            }

    def log_activity(self, username, activity_type, description, 
                    target_resource='', action_result='Success', error_message='None',
                    data_modified='', security_level='Normal', notes=''):
        """Log user activity with comprehensive details"""
        if not hasattr(st.session_state, 'data_manager') or self._is_logging:
            return False

        # 재귀 방지
        self._is_logging = True

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Get user info safely without causing recursion
            user_info = None
            try:
                if os.path.exists('data/users.csv'):
                    users_df = pd.read_csv('data/users.csv', encoding='utf-8-sig')
                    if not users_df.empty and username in users_df['username'].values:
                        user_info = users_df[users_df['username'] == username].iloc[0]
            except Exception:
                pass

            # Generate session ID if not exists
            if 'session_id' not in st.session_state:
                st.session_state.session_id = f"sess_{int(datetime.now().timestamp())}"

            log_entry = {
                'timestamp': timestamp,
                'username': username,
                'user_name': user_info['name'] if user_info is not None else 'Unknown',
                'user_role': user_info['role'] if user_info is not None else 'Unknown',
                'club_name': user_info.get('club_name', 'None') if user_info is not None else 'None',
                'ip_address': '127.0.0.1',
                'session_id': st.session_state.session_id,
                'activity_type': activity_type,
                'activity_description': description,
                'target_resource': target_resource,
                'action_result': action_result,
                'error_message': error_message,
                'user_agent': 'Streamlit App',
                'device_type': 'Web',
                'browser_info': 'Chrome/Safari',
                'request_method': 'POST',
                'response_time': f"{np.random.randint(50, 500)}ms",
                'data_modified': data_modified,
                'security_level': security_level,
                'notes': notes
            }

            # 직접 CSV에 저장하여 재귀 방지
            logs_df = pd.read_csv(self.logs_file, encoding='utf-8-sig') if os.path.exists(self.logs_file) else pd.DataFrame()

            # ID 생성
            log_entry['id'] = len(logs_df) + 1

            # 새 로그 추가
            new_log_df = pd.DataFrame([log_entry])
            if not logs_df.empty:
                logs_df = pd.concat([logs_df, new_log_df], ignore_index=True)
            else:
                logs_df = new_log_df

            # CSV 저장
            logs_df.to_csv(self.logs_file, index=False, encoding='utf-8-sig')

            # Also log to console for debugging
            if activity_type in ['Authentication', 'System', 'Admin']:
                print(f"🔍 LOG: {username} | {activity_type} | {description} | {action_result}")

            return True

        except Exception as e:
            print(f"로그 기록 오류: {e}")
            return False
        finally:
            self._is_logging = False

    def log_login(self, username, success):
        """Log login attempts"""
        try:
            self.log_activity(
                username,
                'Authentication',
                f"Login {'successful' if success else 'failed'}",
                'Login System',
                'Success' if success else 'Failed',
                error_message='Invalid credentials' if not success else 'None',
                security_level='High' if not success else 'Normal'
            )
        except Exception as e:
            print(f"로그 기록 실패: {e}")

    def log_page_visit(self, username, page_name):
        """Log page visits"""
        return self.log_activity(
            username, 'Navigation', f'Visited {page_name} page',
            page_name, 'Success', notes=f'Page navigation to {page_name}'
        )

    def log_data_operation(self, username, operation, table_name, record_id='', result='Success'):
        """Log data operations (CRUD)"""
        return self.log_activity(
            username, 'Data Operation', f'{operation} on {table_name}',
            table_name, result, data_modified=f'{operation} record {record_id}'
        )

    def log_system_event(self, event_description, event_type='System'):
        """Log system events"""
        return self.log_activity(
            'system', event_type, event_description,
            'System', 'Success', security_level='High'
        )

    def log_data_access(self, username, resource, operation, records_affected=0):
        """Log data access operations"""
        self.log_activity(
            username=username,
            activity_type="Data Access",
            description=f"{operation} operation on {resource}",
            target_resource=resource,
            action_result="Success",
            data_modified=f"{records_affected} records" if records_affected > 0 else "None",
            notes=f"Data {operation.lower()} operation"
        )

    def log_error(self, username, error_type, error_message, context=""):
        """Log system errors"""
        self.log_activity(
            username=username,
            activity_type="System Error",
            description=f"{error_type}: {error_message}",
            target_resource=context,
            action_result="Error",
            error_message=error_message,
            security_level="High",
            notes=f"System error in context: {context}"
        )

    def log_security_event(self, username, event_type, description, severity="Medium"):
        """Log security events"""
        self.log_activity(
            username=username,
            activity_type="Security Event",
            description=description,
            target_resource="Security System",
            action_result="Alert",
            security_level=severity,
            notes=f"Security event: {event_type}"
        )

    def load_logs(self):
        """Load logs from CSV file with safe datetime parsing"""
        try:
            logs_df = st.session_state.data_manager.load_csv('logs')
            if not logs_df.empty and 'timestamp' in logs_df.columns:
                # Safe datetime conversion
                def safe_parse_timestamp(ts):
                    if pd.isna(ts) or not ts:
                        return None
                    try:
                        # Try multiple formats
                        formats = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']
                        for fmt in formats:
                            try:
                                return datetime.strptime(str(ts), fmt)
                            except ValueError:
                                continue
                        # If all fail, use pandas parsing
                        return pd.to_datetime(ts, errors='coerce')
                    except:
                        return None

                logs_df['timestamp'] = logs_df['timestamp'].apply(safe_parse_timestamp)
                logs_df = logs_df.dropna(subset=['timestamp'])
            return logs_df
        except Exception as e:
            # Return empty dataframe instead of error
            return pd.DataFrame()

    def show_logs_interface(self, user):
        """Display comprehensive logs interface"""
        if not hasattr(st.session_state, 'data_manager'):
            st.error("데이터 매니저가 초기화되지 않았습니다.")
            return

        # Initialize logs if needed
        self.initialize_logs()

        st.markdown("### 📊 시스템 로그")

        if user['role'] not in ['선생님', '회장', '부회장']:
            st.warning("로그 조회 권한이 없습니다.")
            return

        # Load logs
        logs_df = self.load_logs()

        if logs_df.empty:
            st.info("로그 데이터가 없습니다.")
            return

        # Log summary statistics
        self.show_log_statistics(logs_df)

        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 전체 로그", "🔍 필터링", "📊 분석", "⚠️ 보안", "📈 실시간"])

        with tab1:
            self.show_all_logs(logs_df, user)

        with tab2:
            self.show_filtered_logs(logs_df, user)

        with tab3:
            self.show_log_analytics(logs_df, user)

        with tab4:
            self.show_security_logs(logs_df, user)

        with tab5:
            self.show_realtime_logs(logs_df, user)

    def show_log_statistics(self, logs_df):
        """Display log statistics"""
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_logs = len(logs_df)
            error_handler.wrap_streamlit_component(st.metric, "📊 총 로그", total_logs)

        with col2:
            today_logs = len(logs_df[logs_df['timestamp'].astype(str).str.contains(datetime.now().strftime('%Y-%m-%d'))])
            error_handler.wrap_streamlit_component(st.metric, "📅 오늘 로그", today_logs)

        with col3:
            error_logs = len(logs_df[logs_df['action_result'] == 'Error'])
            error_handler.wrap_streamlit_component(st.metric, "❌ 오류 로그", error_logs)

        with col4:
            security_logs = len(logs_df[logs_df['security_level'] == 'High'])
            error_handler.wrap_streamlit_component(st.metric, "🔒 보안 로그", security_logs)

        with col5:
            unique_users = logs_df['username'].nunique()
            error_handler.wrap_streamlit_component(st.metric, "👥 활성 사용자", unique_users)

    def show_all_logs(self, logs_df, user):
        """Display all logs with pagination"""
        st.markdown("#### 📋 전체 로그")

        # Pagination
        items_per_page = st.selectbox("페이지당 항목", [10, 25, 50, 100], index=1)
        total_pages = (len(logs_df) - 1) // items_per_page + 1

        if total_pages > 1:
            page = st.selectbox("페이지", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_logs = logs_df.iloc[start_idx:end_idx]
        else:
            page_logs = logs_df

        # Display logs
        for _, log in page_logs.iterrows():
            self.display_log_entry(log)

    def show_filtered_logs(self, logs_df, user):
        """Display filtered logs"""
        st.markdown("#### 🔍 로그 필터링")

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            username_filter = st.selectbox("👤 사용자", ["전체"] + list(logs_df['username'].unique()))
            activity_filter = st.selectbox("📝 활동 유형", ["전체"] + list(logs_df['activity_type'].unique()))

        with col2:
            result_filter = st.selectbox("📊 결과", ["전체"] + list(logs_df['action_result'].unique()))
            security_filter = st.selectbox("🔒 보안 수준", ["전체"] + list(logs_df['security_level'].unique()))

        with col3:
            date_filter = st.date_input("📅 날짜 (부터)", value=datetime.now().date() - timedelta(days=7))
            resource_filter = st.text_input("🎯 리소스 (포함)", placeholder="검색할 리소스명")

        # Apply filters
        filtered_df = logs_df.copy()

        if username_filter != "전체":
            filtered_df = filtered_df[filtered_df['username'] == username_filter]

        if activity_filter != "전체":
            filtered_df = filtered_df[filtered_df['activity_type'] == activity_filter]

        if result_filter != "전체":
            filtered_df = filtered_df[filtered_df['action_result'] == result_filter]

        if security_filter != "전체":
            filtered_df = filtered_df[filtered_df['security_level'] == security_filter]

        if resource_filter:
            try:
                # Ensure target_resource column is string type
                filtered_df['target_resource'] = filtered_df['target_resource'].astype(str)
                filtered_df = filtered_df[filtered_df['target_resource'].str.contains(resource_filter, case=False, na=False)]
            except Exception:
                # If filtering fails, keep all records
                pass

        try:
            filtered_df['timestamp'] = filtered_df['timestamp'].astype(str)
            filtered_df = filtered_df[filtered_df['timestamp'].str.contains(date_filter.strftime('%Y-%m-%d'), na=False)]
        except Exception:
            # If filtering fails, keep all records
            pass

        st.markdown(f"**필터된 결과: {len(filtered_df)}개**")

        # Display filtered logs
        for _, log in filtered_df.head(20).iterrows():
            self.display_log_entry(log)

    def show_log_analytics(self, logs_df, user):
        """Display log analytics"""
        st.markdown("#### 📊 로그 분석")

        if logs_df.empty:
            st.info("분석할 로그 데이터가 없습니다.")
            return

        # Convert timestamp to datetime
        # logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])

        # Activity analysis
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📊 활동 유형별 분포")
            activity_counts = logs_df['activity_type'].value_counts()
            if not activity_counts.empty:
                fig = px.pie(values=activity_counts.values, names=activity_counts.index,
                            title="활동 유형 분포")
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
            else:
                st.info("활동 유형 데이터가 없습니다.")

        with col2:
            st.markdown("##### 📈 시간별 활동")
            hourly_activity = logs_df.groupby(logs_df['timestamp'].dt.hour).size()
            if not hourly_activity.empty:
                fig = px.bar(x=hourly_activity.index, y=hourly_activity.values,
                            title="시간대별 활동", labels={'x': '시간', 'y': '활동 수'})
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
            else:
                st.info("시간별 활동 데이터가 없습니다.")

        # User activity analysis
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 👥 사용자별 활동")
            user_activity = logs_df['username'].value_counts().head(10)
            if not user_activity.empty:
                fig = px.bar(x=user_activity.values, y=user_activity.index, orientation='h',
                            title="상위 10명 활동")
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
            else:
                st.info("사용자별 활동 데이터가 없습니다.")

        with col2:
            st.markdown("##### 📅 일별 활동 트렌드")
            daily_activity = logs_df.groupby(logs_df['timestamp'].dt.date).size()
            if not daily_activity.empty:
                fig = px.line(x=daily_activity.index, y=daily_activity.values,
                             title="일별 활동 추이")
                error_handler.wrap_streamlit_component(st.plotly_chart, fig, use_container_width=True)
            else:
                st.info("일별 활동 데이터가 없습니다.")

    def show_security_logs(self, logs_df, user):
        """Display security-related logs"""
        st.markdown("#### ⚠️ 보안 로그")

        # Security events
        security_logs = logs_df[
            (logs_df['security_level'] == 'High') | 
            (logs_df['activity_type'] == 'Security Event') |
            (logs_df['action_result'] == 'Failed')
        ]

        if security_logs.empty:
            st.success("🔒 보안 이벤트가 없습니다.")
            return

        st.warning(f"⚠️ {len(security_logs)}개의 보안 이벤트가 발견되었습니다.")

        # Group by severity
        col1, col2, col3 = st.columns(3)

        with col1:
            high_security = len(security_logs[security_logs['security_level'] == 'High'])
            error_handler.wrap_streamlit_component(st.metric, "🚨 높음", high_security)

        with col2:
            medium_security = len(security_logs[security_logs['security_level'] == 'Medium'])
            error_handler.wrap_streamlit_component(st.metric, "⚠️ 보통", medium_security)

        with col3:
            failed_actions = len(security_logs[security_logs['action_result'] == 'Failed'])
            error_handler.wrap_streamlit_component(st.metric, "❌ 실패", failed_actions)

        # Display security logs
        for _, log in security_logs.head(20).iterrows():
            self.display_security_log_entry(log)

    def show_realtime_logs(self, logs_df, user):
        """Display real-time logs"""
        st.markdown("#### 📈 실시간 로그")

        # Auto-refresh option
        auto_refresh = st.checkbox("🔄 자동 새로고침 (10초)", value=False)

        if auto_refresh:
            st.rerun()

        # Recent logs (last 1 hour)
        recent_logs = logs_df[logs_df['timestamp'] > (datetime.now() - timedelta(hours=1))]

        st.markdown(f"**최근 1시간 로그: {len(recent_logs)}개**")

        # Display recent logs
        for _, log in recent_logs.head(10).iterrows():
            self.display_log_entry(log, realtime=True)

    def display_log_entry(self, log, realtime=False):
        """Display a single log entry"""
        # Determine status color
        status_colors = {
            'Success': '#28a745',
            'Failed': '#dc3545',
            'Error': '#dc3545',
            'Warning': '#ffc107',
            'Info': '#17a2b8'
        }

        status_color = status_colors.get(log['action_result'], '#6c757d')

        # Security level indicator
        security_indicators = {
            'High': '🔴',
            'Medium': '🟡',
            'Normal': '🟢',
            'Low': '🔵'
        }

        security_indicator = security_indicators.get(log.get('security_level', 'Normal'), '⚪')

        # Time formatting
        timestamp = log['timestamp']
        if realtime:
            time_diff = datetime.now() - pd.to_datetime(timestamp)
            time_display = f"{int(time_diff.total_seconds())}초 전"
        else:
            time_display = timestamp

        # 상태별 색상 이모지
        status_emoji = {
            'Success': '✅',
            'Failed': '❌', 
            'Error': '🚨',
            'Warning': '⚠️',
            'Info': 'ℹ️'
        }.get(log['action_result'], '📋')

        with st.container():
            # 헤더 라인
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.write(f"{security_indicator} **{log['activity_type']}**")
            with col2:
                st.write(f"{status_emoji} {log['action_result']}")
            with col3:
                st.caption(time_display)

            # 사용자 정보
            st.write(f"👤 **{log['user_name']} ({log['username']})** - {log['user_role']}")

            # 활동 설명
            st.write(f"📝 {log['activity_description']}")

            # 추가 정보
            st.caption(f"🎯 리소스: {log.get('target_resource', 'N/A')} | 🌐 IP: {log.get('ip_address', 'N/A')} | 📱 {log.get('device_type', 'N/A')}")

            st.divider()

    def display_security_log_entry(self, log):
        """Display a security log entry with enhanced styling"""
        security_colors = {
            'High': '#dc3545',
            'Medium': '#ffc107',
            'Normal': '#28a745'
        }

        security_color = security_colors.get(log.get('security_level', 'Normal'), '#6c757d')

        with st.container():
            # 보안 레벨별 색상
            level_emoji = {
                'High': '🔴',
                'Medium': '🟡', 
                'Normal': '🟢'
            }.get(log.get('security_level', 'Normal'), '⚪')

            # 경고 박스
            if log.get('security_level', 'Normal') == 'High':
                st.error(f"🚨 **보안 이벤트** {level_emoji} {log.get('security_level', 'Normal')}")
            elif log.get('security_level', 'Normal') == 'Medium':
                st.warning(f"🚨 **보안 이벤트** {level_emoji} {log.get('security_level', 'Normal')}")
            else:
                st.info(f"🚨 **보안 이벤트** {level_emoji} {log.get('security_level', 'Normal')}")

            # 사용자 정보
            st.write(f"👤 **{log['user_name']} ({log['username']})**")

            # 활동 설명
            st.write(f"📝 {log['activity_description']}")

            # 시간 및 위치 정보
            st.caption(f"🕐 {log['timestamp']} | 🌐 {log.get('ip_address', 'N/A')} | 🎯 {log.get('target_resource', 'N/A')}")

            # 오류 메시지가 있으면 표시
            if log.get('error_message') and log['error_message'] != 'None':
                st.error(f"**오류:** {log['error_message']}")

            st.divider()

    def export_logs(self, logs_df, format='csv'):
        """Export logs in various formats"""
        if format == 'csv':
            return logs_df.to_csv(index=False)
        elif format == 'json':
            return logs_df.to_json(orient='records', date_format='iso')
        else:
            return logs_df.to_string()

    def cleanup_old_logs(self, days_to_keep=30):
        """Clean up old logs"""
        if not hasattr(st.session_state, 'data_manager'):
            return False

        try:
            logs_df = st.session_state.data_manager.load_csv('logs')
            if logs_df.empty:
                return True

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])

            recent_logs = logs_df[logs_df['timestamp'] >= cutoff_date]

            return st.session_state.data_manager.save_csv('logs', recent_logs)

        except Exception as e:
            self.log_error('system', 'Log Cleanup', str(e), 'cleanup_old_logs')
            return False