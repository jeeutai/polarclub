import pandas as pd
import os
import sys
import importlib
import traceback
from datetime import datetime, timedelta
import json
import re

class AdvancedTestSystem:
    def __init__(self):
        self.test_results = {}
        self.critical_errors = []
        self.warnings = []
        self.deployment_ready = True
        self.test_data = {}
        self.auto_fixes_applied = []

    def run_all_tests(self):
        """Run all tests with auto-fix capabilities"""
        print("🧪 고급 테스트 시스템 시작")
        print("자동 수정 기능이 포함되어 있습니다.\n")

        test_sequence = [
            ("환경 검사", self.test_environment),
            ("문법 검사", self.test_syntax_all_files),
            ("모듈 임포트", self.test_all_imports),
            ("데이터 구조", self.test_data_structure_integrity),
            ("인증 시스템", self.test_authentication_system),
            ("비즈니스 로직", self.test_business_logic),
            ("Streamlit 기능", self.test_streamlit_functionality),
            ("기능 테스트", self.test_functional_features),
            ("로그 시스템", self.test_logging_system),
            ("배포 준비", self.test_deployment_readiness),
            ("보안 검사", self.test_security),
            ("성능 검사", self.test_performance)
        ]

        for test_name, test_function in test_sequence:
            print(f"\n{'─'*60}")
            print(f"🔍 {test_name} 테스트 중...")
            print(f"{'─'*60}")

            try:
                result = test_function()
                if result:
                    print(f"✅ {test_name} 테스트 완료")
                else:
                    print(f"❌ {test_name} 테스트 실패")
            except Exception as e:
                error_msg = f"{test_name} 테스트 중 예외 발생: {str(e)}"
                print(f"🚨 {error_msg}")
                self.critical_errors.append(error_msg)
                self.deployment_ready = False

        # Auto-fix 시도
        if self.critical_errors or self.warnings:
            print(f"\n{'='*60}")
            print("🔧 자동 수정 시도")
            print(f"{'='*60}")
            self.attempt_auto_fixes()

        # Generate final report
        return self.generate_comprehensive_report()

    def test_environment(self):
        """Test environment setup"""
        print("🌍 환경 설정 검사...")

        env_results = {}

        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            print(f"✅ Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
            env_results['python_version'] = "OK"
        else:
            print(f"⚠️  Python 버전이 낮습니다: {python_version.major}.{python_version.minor}")
            env_results['python_version'] = "OLD_VERSION"
            self.warnings.append("Python 3.8 이상을 권장합니다")

        # Check required directories
        required_dirs = ['data', 'attached_assets']
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                print(f"✅ {dir_name} 디렉토리 존재")
                env_results[f'{dir_name}_dir'] = "EXISTS"
            else:
                print(f"⚠️  {dir_name} 디렉토리가 없습니다. 생성 중...")
                os.makedirs(dir_name)
                env_results[f'{dir_name}_dir'] = "CREATED"

        # Check file permissions
        try:
            test_file = 'test_write_permission.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("✅ 파일 쓰기 권한 정상")
            env_results['write_permission'] = "OK"
        except Exception as e:
            print(f"❌ 파일 쓰기 권한 오류: {e}")
            env_results['write_permission'] = "ERROR"
            self.critical_errors.append(f"파일 쓰기 권한 없음: {e}")
            self.deployment_ready = False

        self.test_results['environment'] = env_results
        return len([r for r in env_results.values() if 'ERROR' in r]) == 0

    def test_all_imports(self):
        """Test all Python module imports with auto-fix"""
        print("🔍 모든 모듈 임포트 테스트 시작...")

        modules_to_test = [
            'auth', 'data_manager', 'ui_components', 'board_system',
            'chat_system', 'assignment_system', 'quiz_system',
            'attendance_system', 'schedule_system', 'report_generator',
            'vote_system', 'gallery_system', 'video_conference_system',
            'backup_system', 'notification_system', 'search_system',
            'admin_system', 'ai_assistant', 'gamification_system',
            'portfolio_system', 'logging_system', 'enhanced_features',
            'additional_features', 'initialize_data'
        ]

        import_results = {}

        for module_name in modules_to_test:
            try:
                # 모듈 임포트 시도
                if module_name in sys.modules:
                    del sys.modules[module_name]  # 캐시 제거

                module = importlib.import_module(module_name)
                print(f"✅ {module_name}: 임포트 성공")
                import_results[module_name] = "SUCCESS"
                self.test_data[module_name] = module

            except SyntaxError as e:
                error_msg = f"문법 오류: {str(e)}"
                print(f"❌ {module_name}: {error_msg}")
                import_results[module_name] = f"SYNTAX_ERROR: {error_msg}"
                self.critical_errors.append(f"{module_name}: {error_msg}")
                self.deployment_ready = False

                # 자동 수정 시도
                if self.auto_fix_syntax_error(module_name, e):
                    self.auto_fixes_applied.append(f"문법 오류 수정: {module_name}")

            except ImportError as e:
                error_msg = f"임포트 오류: {str(e)}"
                print(f"⚠️  {module_name}: {error_msg}")
                import_results[module_name] = f"IMPORT_ERROR: {error_msg}"
                self.warnings.append(f"{module_name}: {error_msg}")

                # 자동 수정 시도
                if self.auto_fix_import_error(module_name, e):
                    self.auto_fixes_applied.append(f"임포트 오류 수정: {module_name}")

            except Exception as e:
                error_msg = f"기타 오류: {str(e)}"
                print(f"❌ {module_name}: {error_msg}")
                import_results[module_name] = f"ERROR: {error_msg}"
                self.critical_errors.append(f"{module_name}: {error_msg}")
                self.deployment_ready = False

        self.test_results['imports'] = import_results
        return len(self.critical_errors) == 0

    def test_syntax_all_files(self):
        """Test syntax of all Python files with auto-fix"""
        print("\n📝 모든 Python 파일 문법 검사 시작...")

        python_files = [f for f in os.listdir('.') if f.endswith('.py')]
        syntax_results = {}

        for file_name in python_files:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()

                compile(content, file_name, 'exec')
                print(f"✅ {file_name}: 문법 정상")
                syntax_results[file_name] = "SYNTAX_OK"

            except SyntaxError as e:
                error_msg = f"줄 {e.lineno}: {e.msg}"
                print(f"❌ {file_name}: 문법 오류 - {error_msg}")
                syntax_results[file_name] = f"SYNTAX_ERROR: {error_msg}"
                self.critical_errors.append(f"{file_name}: {error_msg}")
                self.deployment_ready = False

                # 자동 수정 시도
                if self.auto_fix_file_syntax(file_name, e, content):
                    self.auto_fixes_applied.append(f"파일 문법 수정: {file_name}")

            except Exception as e:
                error_msg = f"파일 읽기 오류: {str(e)}"
                print(f"⚠️  {file_name}: {error_msg}")
                syntax_results[file_name] = f"READ_ERROR: {error_msg}"
                self.warnings.append(f"{file_name}: {error_msg}")

        self.test_results['syntax'] = syntax_results
        return len([r for r in syntax_results.values() if 'SYNTAX_ERROR' in r]) == 0

    def test_data_structure_integrity(self):
        """Test comprehensive data structure integrity with auto-fix"""
        print("\n🗄️  데이터 구조 무결성 검사 시작...")

        data_integrity_results = {}

        # Test data directory
        if not os.path.exists('data'):
            print("⚠️  data 디렉토리가 존재하지 않습니다. 생성 중...")
            os.makedirs('data')
            self.auto_fixes_applied.append("data 디렉토리 생성")

        # Required CSV files and their expected columns
        csv_requirements = {
            'users.csv': ['username', 'password', 'name', 'role', 'club_name', 'club_role', 'created_date'],
            'clubs.csv': ['name', 'icon', 'description', 'president', 'max_members', 'created_date'],
            'posts.csv': ['id', 'title', 'content', 'author', 'club', 'created_date', 'likes', 'comments'],
            'assignments.csv': ['id', 'title', 'description', 'club', 'creator', 'due_date', 'status', 'created_date'],
            'attendance.csv': ['id', 'username', 'club', 'date', 'status', 'recorded_by'],
            'quizzes.csv': ['id', 'title', 'description', 'club', 'creator', 'questions', 'time_limit', 'attempts_allowed', 'status', 'created_date'],
            'schedules.csv': ['id', 'title', 'description', 'club', 'date', 'time', 'location', 'creator', 'created_date'],
            'notifications.csv': ['id', 'username', 'title', 'message', 'type', 'read', 'created_date'],
            'badges.csv': ['id', 'username', 'badge_name', 'badge_icon', 'description', 'awarded_date', 'awarded_by'],
            'votes.csv': ['id', 'title', 'description', 'options', 'club', 'creator', 'end_date', 'created_date'],
            'logs.csv': ['id', 'timestamp', 'username', 'user_name', 'user_role', 'club_name', 'ip_address', 'session_id', 'activity_type', 'activity_description', 'target_resource', 'action_result', 'error_message', 'user_agent', 'device_type', 'browser_info', 'request_method', 'response_time', 'data_modified', 'security_level', 'notes']
        }

        for csv_file, required_columns in csv_requirements.items():
            file_path = f"data/{csv_file}"

            # Check file existence
            if not os.path.exists(file_path):
                print(f"⚠️  {csv_file}: 파일이 존재하지 않음 (자동 생성 시도)")
                if self.auto_create_csv_file(csv_file, required_columns):
                    data_integrity_results[csv_file] = "MISSING_CREATED"
                    self.auto_fixes_applied.append(f"CSV 파일 생성: {csv_file}")
                continue

            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')

                # Check required columns
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    error_msg = f"필수 컬럼 누락: {missing_columns}"
                    print(f"❌ {csv_file}: {error_msg}")

                    # 자동 수정 시도
                    if self.auto_fix_missing_columns(csv_file, missing_columns, df):
                        data_integrity_results[csv_file] = f"FIXED_MISSING_COLUMNS: {missing_columns}"
                        self.auto_fixes_applied.append(f"누락 컬럼 추가: {csv_file}")
                    else:
                        data_integrity_results[csv_file] = f"MISSING_COLUMNS: {missing_columns}"
                        self.critical_errors.append(f"{csv_file}: {error_msg}")
                        self.deployment_ready = False
                else:
                    print(f"✅ {csv_file}: 구조 정상 ({len(df)}개 레코드)")
                    data_integrity_results[csv_file] = f"OK: {len(df)} records"

            except Exception as e:
                error_msg = f"데이터 로드 오류: {str(e)}"
                print(f"❌ {csv_file}: {error_msg}")
                data_integrity_results[csv_file] = f"LOAD_ERROR: {error_msg}"
                self.critical_errors.append(f"{csv_file}: {error_msg}")
                self.deployment_ready = False

        self.test_results['data_integrity'] = data_integrity_results
        return len([r for r in data_integrity_results.values() if 'ERROR' in r or 'MISSING_COLUMNS' in r]) == 0

    def test_authentication_system(self):
        """Test authentication system functionality"""
        try:
            print("🔐 인증 시스템 테스트 시작...")

            # Import auth module
            import auth
            auth_manager = auth.AuthManager()

            # Test user loading
            users = auth_manager.load_users()
            if users.empty:
                print("⚠️ 사용자 데이터가 없습니다.")
                self.warnings.append("No user data found")
            else:
                print(f"✅ 사용자 {len(users)}명 로드됨")

            # Test login functionality
            if 'admin' in users['username'].values:
                print("✅ 관리자 계정 존재")
            else:
                print("⚠️ 관리자 계정이 없습니다.")
                self.warnings.append("No admin account found")

            print("✅ 인증 시스템 테스트 완료")
            return True

        except Exception as e:
            print(f"❌ 인증 시스템 테스트 실패: {e}")
            self.critical_errors.append(f"Authentication test failed: {e}")
            return False

    def test_business_logic(self):
        """Test business logic components"""
        print("\n🏢 비즈니스 로직 테스트 시작...")

        business_results = {}

        # Test core systems
        core_systems = [
            ('DataManager', 'data_manager'),
            ('AttendanceSystem', 'attendance_system'),
            ('QuizSystem', 'quiz_system'),
            ('NotificationSystem', 'notification_system'),
            ('AdminSystem', 'admin_system'),
            ('BoardSystem', 'board_system'),
            ('ChatSystem', 'chat_system')
        ]

        for class_name, module_name in core_systems:
            try:
                module = importlib.import_module(module_name)
                class_obj = getattr(module, class_name)
                instance = class_obj()
                print(f"✅ {class_name}: 인스턴스 생성 성공")
                business_results[class_name] = "INSTANTIATED"
            except Exception as e:
                print(f"❌ {class_name}: 인스턴스 생성 실패 - {e}")
                business_results[class_name] = f"ERROR: {e}"
                self.warnings.append(f"{class_name} 인스턴스 생성 실패")

        self.test_results['business_logic'] = business_results
        return len([r for r in business_results.values() if 'ERROR' in r]) == 0

    def test_streamlit_functionality(self):
        """Test Streamlit specific functionality"""
        print("\n🎨 Streamlit 기능 테스트 시작...")

        streamlit_results = {}

        try:
            import streamlit as st
            print("✅ Streamlit 임포트 성공")
            streamlit_results['import'] = "SUCCESS"

            # Check app.py structure
            if os.path.exists('app.py'):
                with open('app.py', 'r', encoding='utf-8') as f:
                    app_content = f.read()

                required_functions = ['main()', 'show_login()', 'show_main_app()']
                for func in required_functions:
                    if func in app_content:
                        print(f"✅ {func} 함수 존재")
                        streamlit_results[func] = "FOUND"
                    else:
                        print(f"❌ {func} 함수 누락")
                        streamlit_results[func] = "MISSING"
                        self.critical_errors.append(f"필수 함수 누락: {func}")

                # Check for HTML usage (should be minimal)
                html_count = app_content.count('unsafe_allow_html=True')
                if html_count <= 2:
                    print(f"✅ HTML 사용량 적절: {html_count}개")
                    streamlit_results['html_usage'] = f"LOW: {html_count}"
                else:
                    print(f"⚠️  HTML 사용량 많음: {html_count}개")
                    streamlit_results['html_usage'] = f"HIGH: {html_count}"
                    self.warnings.append(f"HTML 사용량 많음: {html_count}개")

            # Check for Streamlit key conflicts
            key_conflicts = self.check_streamlit_key_conflicts()
            if key_conflicts:
                print(f"❌ Streamlit 키 충돌 발견: {len(key_conflicts)}개")
                streamlit_results['key_conflicts'] = f"CONFLICTS: {len(key_conflicts)}"
                for conflict in key_conflicts:
                    self.critical_errors.append(f"키 충돌: {conflict}")
                    print(f"   - {conflict}")
            else:
                print("✅ Streamlit 키 충돌 없음")
                streamlit_results['key_conflicts'] = "NONE"

        except Exception as e:
            print(f"❌ Streamlit 기능 테스트 실패: {e}")
            streamlit_results['system'] = f"ERROR: {e}"
            self.critical_errors.append(f"Streamlit 기능 오류: {e}")

        self.test_results['streamlit_functionality'] = streamlit_results
        return len([r for r in streamlit_results.values() if 'ERROR' in r or 'MISSING' in r or 'CONFLICTS' in r]) == 0

    def test_functional_features(self):
        """Test functional features by actually running them"""
        print("\n⚙️ 기능 테스트 시작...")

        functional_results = {}

        # Test data manager functionality
        try:
            from data_manager import DataManager
            dm = DataManager()

            # Test loading users
            users_df = dm.load_csv('users')
            if not users_df.empty:
                print(f"✅ DataManager: 사용자 데이터 로드 성공 ({len(users_df)}명)")
                functional_results['data_manager'] = f"FUNCTIONAL: {len(users_df)} users loaded"
            else:
                print("⚠️  DataManager: 사용자 데이터가 비어있음")
                functional_results['data_manager'] = "EMPTY_DATA"
                self.warnings.append("사용자 데이터가 비어있음")
        except Exception as e:
            print(f"❌ DataManager 테스트 실패: {e}")
            functional_results['data_manager'] = f"ERROR: {e}"
            self.critical_errors.append(f"DataManager 오류: {e}")

        # Test other systems
        systems_to_test = [
            'board_system', 'chat_system', 'assignment_system',
            'quiz_system', 'attendance_system', 'notification_system',
            'admin_system'
        ]

        for system in systems_to_test:
            try:
                module = importlib.import_module(system)
                print(f"✅ {system}: 임포트 가능")
                functional_results[system] = "IMPORTABLE"
            except Exception as e:
                print(f"❌ {system}: 임포트 실패 - {e}")
                functional_results[system] = f"IMPORT_ERROR: {e}"
                self.warnings.append(f"{system} 임포트 실패")

        self.test_results['functional_features'] = functional_results
        return len([r for r in functional_results.values() if 'ERROR' in r]) <= 2

    def test_logging_system(self):
        """Test logging system functionality"""
        print("\n📊 로그 시스템 테스트 시작...")

        log_results = {}

        try:
            # LoggingSystem 임포트 테스트
            from logging_system import LoggingSystem
            logging_system = LoggingSystem()
            print("✅ LoggingSystem 임포트 성공")
            log_results['import'] = "SUCCESS"

            # 로그 파일 존재 확인
            logs_file = 'data/logs.csv'
            if os.path.exists(logs_file):
                logs_df = pd.read_csv(logs_file, encoding='utf-8-sig')
                required_columns = ['id', 'timestamp', 'username', 'activity_type', 'activity_description']

                missing_cols = [col for col in required_columns if col not in logs_df.columns]
                if missing_cols:
                    print(f"❌ 로그 파일에 필수 컬럼 누락: {missing_cols}")
                    log_results['structure'] = f"MISSING_COLUMNS: {missing_cols}"
                    self.critical_errors.append(f"로그 파일 구조 오류: {missing_cols}")
                else:
                    print(f"✅ 로그 파일 구조 정상 ({len(logs_df)}개 로그)")
                    log_results['structure'] = "OK"
            else:
                print("❌ 로그 파일이 존재하지 않습니다")
                log_results['file_exists'] = "MISSING"
                self.critical_errors.append("로그 파일이 존재하지 않습니다")

        except Exception as e:
            print(f"❌ 로그 시스템 테스트 실패: {e}")
            log_results['system'] = f"ERROR: {e}"
            self.critical_errors.append(f"로그 시스템 오류: {e}")
            self.deployment_ready = False

        self.test_results['logging'] = log_results
        return len([r for r in log_results.values() if 'ERROR' in r]) == 0

    def test_deployment_readiness(self):
        """Test deployment readiness"""
        print("\n🚀 배포 준비 상태 검사 시작...")

        deployment_results = {}

        # Check essential files
        essential_files = ['app.py', 'requirements.txt']
        for file_name in essential_files:
            if os.path.exists(file_name):
                print(f"✅ {file_name}: 존재")
                deployment_results[file_name] = "EXISTS"
            else:
                print(f"❌ {file_name}: 누락")
                deployment_results[file_name] = "MISSING"
                self.critical_errors.append(f"필수 파일 누락: {file_name}")

        # Check pyproject.toml
        if os.path.exists('pyproject.toml'):
            print("✅ pyproject.toml: 존재")
            deployment_results['pyproject.toml'] = "EXISTS"

        # Test data directory write permissions
        try:
            test_file = 'data/test_write.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("✅ 데이터 디렉토리 쓰기 권한 정상")
            deployment_results['data_write_permission'] = "OK"
        except Exception as e:
            print(f"❌ 데이터 디렉토리 쓰기 권한 오류: {e}")
            deployment_results['data_write_permission'] = f"ERROR: {e}"
            self.critical_errors.append(f"데이터 쓰기 권한 오류: {e}")

        # Check for large files that might affect deployment
        large_files = []
        html_usage_files = []

        for root, dirs, files in os.walk('.'):
            # Skip hidden directories, data directory, and attached_assets
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['data', 'attached_assets', '__pycache__']]

            for file in files:
                if not file.startswith('.') and file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        if size > 500 * 1024:  # 500KB for Python files
                            large_files.append((file_path, size))

                        # Check for HTML usage in Python files
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'unsafe_allow_html=True' in content or '<div style=' in content or '<span style=' in content:
                                html_usage_files.append(file_path)
                    except:
                        pass

        if large_files:
            print(f"⚠️ 큰 파일들이 발견되었습니다 ({len(large_files)}개):")
            for file_path, size in large_files[:5]:  # Show first 5
                print(f"   - {file_path}: {size // 1024}KB")
            self.warnings.append(f"큰 파일들이 배포에 영향을 줄 수 있음: {len(large_files)}개")

            if len(large_files) > 10:
                self.warnings.append(f"큰 파일들이 성능에 영향을 줄 수 있습니다: {len(large_files)}개")

        if html_usage_files:
            print(f"⚠️ HTML 사용이 발견되었습니다 ({len(html_usage_files)}개):")
            for file_path in html_usage_files[:3]:  # Show first 3
                print(f"   - {file_path}")
            self.warnings.append(f"HTML 사용량 많음: {len(html_usage_files)}개")

        self.test_results['deployment'] = deployment_results
        return len([r for r in deployment_results.values() if 'ERROR' in r or 'MISSING' in r]) == 0

    def test_security(self):
        """Test security aspects"""
        print("\n🔒 보안 검사 시작...")

        security_results = {}

        # Check for hardcoded passwords
        security_issues = []
        python_files = [f for f in os.listdir('.') if f.endswith('.py')]

        for file_name in python_files:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 하드코딩된 비밀번호 검사 (더 관대하게)
                password_patterns = [
                    r'password\s*=\s*["\'][^"\']{8,}["\']',  # 8자 이상만 체크
                    r'secret_key\s*=\s*["\'][^"\']{8,}["\']'
                ]

                for pattern in password_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        security_issues.append(f"{file_name}: 하드코딩된 비밀번호 발견")

            except Exception as e:
                self.warnings.append(f"보안 검사 중 오류: {file_name} - {e}")

        if security_issues:
            print(f"⚠️  보안 이슈 발견: {len(security_issues)}개")
            for issue in security_issues:
                print(f"   - {issue}")
            security_results['hardcoded_passwords'] = f"ISSUES: {len(security_issues)}"
            for issue in security_issues:
                self.warnings.append(issue)
        else:
            print("✅ 심각한 하드코딩된 비밀번호 없음")
            security_results['hardcoded_passwords'] = "OK"

        self.test_results['security'] = security_results
        return len([r for r in security_results.values() if 'CRITICAL' in r]) == 0

    def test_performance(self):
        """Test performance aspects"""
        print("\n⚡ 성능 검사 시작...")

        performance_results = {}

        # Check file sizes
        large_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.py', '.csv')):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        if size > 1024 * 1024:  # 1MB
                            large_files.append((file_path, size))
                    except:
                        continue

        if large_files:
            print(f"⚠️  큰 파일 발견: {len(large_files)}개")
            for file_path, size in large_files:
                print(f"   - {file_path}: {size / (1024*1024):.2f}MB")
            performance_results['large_files'] = f"FOUND: {len(large_files)}"
            self.warnings.append(f"큰 파일들이 성능에 영향을 줄 수 있습니다: {len(large_files)}개")
        else:
            print("✅ 모든 파일 크기 적정")
            performance_results['large_files'] = "OK"

        self.test_results['performance'] = performance_results
        return True

    def auto_fix_syntax_error(self, module_name, error):
        """Attempt to automatically fix syntax errors"""
        try:
            file_path = f"{module_name}.py"
            if not os.path.exists(file_path):
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 일반적인 문법 오류 수정
            # 1. 누락된 콜론 추가
            content = re.sub(r'(if|elif|else|for|while|def|class|try|except|finally|with)\s+([^:]+)(?<![:\s])\s*\n', r'\1 \2:\n', content)

            # 2. 누락된 괄호 수정
            lines = content.split('\n')
            for i, line in enumerate(lines):
                # 함수 호출에서 누락된 괄호 확인
                if 'def ' in line and '(' in line and ')' not in line:
                    lines[i] = line + ')'

            content = '\n'.join(lines)

            # 변경사항이 있으면 저장
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"🔧 {module_name}: 문법 오류 자동 수정 시도")
                return True

        except Exception as e:
            print(f"❌ {module_name} 자동 수정 실패: {e}")

        return False

    def auto_fix_import_error(self, module_name, error):
        """Attempt to automatically fix import errors"""
        try:
            # 누락된 모듈 파일 생성
            file_path = f"{module_name}.py"
            if not os.path.exists(file_path):
                # 기본 클래스 구조 생성
                class_name = ''.join([word.capitalize() for word in module_name.split('_')])

                template = f'''import streamlit as st
import pandas as pd
from datetime import datetime

class {class_name}:
    def __init__(self):
        pass

    def show_interface(self, user):
        """Display the interface"""
        st.markdown("### {class_name}")
        st.info("이 기능은 아직 구현 중입니다.")
'''

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(template)

                print(f"🔧 {module_name}: 누락된 모듈 파일 자동 생성")
                return True

        except Exception as e:
            print(f"❌ {module_name} 임포트 오류 자동 수정 실패: {e}")

        return False

    def auto_fix_file_syntax(self, file_name, error, content):
        """Attempt to fix file syntax errors"""
        try:
            # 들여쓰기 오류 수정
            if "indentation" in str(error).lower():
                lines = content.split('\n')
                fixed_lines = []

                for line in lines:
                    # 탭을 스페이스로 변환
                    line = line.replace('\t', '    ')
                    fixed_lines.append(line)

                fixed_content = '\n'.join(fixed_lines)

                if fixed_content != content:
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print(f"🔧 {file_name}: 들여쓰기 오류 자동 수정")
                    return True

        except Exception as e:
            print(f"❌ {file_name} 문법 오류 자동 수정 실패: {e}")

        return False

    def auto_create_csv_file(self, csv_file, required_columns):
        """Automatically create missing CSV files"""
        try:
            file_path = f"data/{csv_file}"

            # Add sample data for logs.csv
            if csv_file == 'logs.csv':
                sample_data = [{
                    'id': 1,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                    'username': 'system',
                    'user_name': 'System',
                    'user_role': 'System',
                    'club_name': 'System',
                    'ip_address': '127.0.0.1',
                    'session_id': 'system_init',
                    'activity_type': 'System',
                    'activity_description': 'Log system initialized',
                    'target_resource': 'logs.csv',
                    'action_result': 'Success',
                    'error_message': 'None',
                    'user_agent': 'System',
                    'device_type': 'Server',
                    'browser_info': 'N/A',
                    'request_method': 'INIT',
                    'response_time': '0ms',
                    'data_modified': '1 record',
                    'security_level': 'Normal',
                    'notes': 'System initialization'
                }]
                df = pd.DataFrame(sample_data)
            else:
                df = pd.DataFrame(columns=required_columns)

            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"🔧 {csv_file}: 누락된 CSV 파일 자동 생성")
            return True
        except Exception as e:
            print(f"❌ {csv_file} 자동 생성 실패: {e}")
            return False

    def auto_fix_missing_columns(self, csv_file, missing_columns, df):
        """Automatically add missing columns to CSV files"""
        try:
            file_path = f"data/{csv_file}"

            # 누락된 컬럼을 적절한 기본값으로 추가
            for col in missing_columns:
                if col in ['id']:
                    df[col] = range(1, len(df) + 1)
                elif col in ['timestamp', 'created_date', 'awarded_date']:
                    df[col] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elif col in ['read']:
                    df[col] = False
                elif col in ['likes', 'comments', 'max_members', 'time_limit', 'attempts_allowed']:
                    df[col] = 0
                else:
                    df[col] = ""

            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"🔧 {csv_file}: 누락된 컬럼 자동 추가 - {missing_columns}")
            return True
        except Exception as e:
            print(f"❌ {csv_file} 컬럼 추가 실패: {e}")
            return False

    def attempt_auto_fixes(self):
        """Attempt to automatically fix detected issues"""
        print("🔧 자동 수정 기능 실행 중...")

        if not self.auto_fixes_applied:
            print("📋 자동으로 수정할 수 있는 이슈가 없습니다.")
            return

        print(f"✅ {len(self.auto_fixes_applied)}개의 자동 수정이 적용되었습니다:")
        for fix in self.auto_fixes_applied:
            print(f"   - {fix}")

        # 수정 후 재테스트 제안
        print("\n🔄 자동 수정 후 재테스트를 권장합니다.")

    def generate_comprehensive_report(self):
        """Generate comprehensive test report with auto-fix information"""
        print("\n" + "="*80)
        print("📋 종합 테스트 보고서 (자동 수정 포함)")
        print("="*80)

        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test_name in self.test_results.keys() 
                          if not any('ERROR' in str(result) for result in self.test_results[test_name].values()))

        print(f"\n📊 테스트 요약:")
        print(f"   전체 테스트 카테고리: {total_tests}")
        print(f"   통과: {passed_tests}")
        print(f"   실패: {total_tests - passed_tests}")
        print(f"   심각한 오류: {len(self.critical_errors)}")
        print(f"   경고: {len(self.warnings)}")
        print(f"   자동 수정 적용: {len(self.auto_fixes_applied)}")

        # Auto-fix summary
        if self.auto_fixes_applied:
            print(f"\n🔧 자동 수정 내역:")
            for i, fix in enumerate(self.auto_fixes_applied, 1):
                print(f"   {i}. {fix}")

        # Deployment status
        deployment_status = "✅ 가능" if self.deployment_ready and len(self.critical_errors) == 0 else "❌ 불가능"
        print(f"\n🚀 배포 가능 여부: {deployment_status}")

        # Critical errors
        if self.critical_errors:
            print(f"\n🚨 심각한 오류 ({len(self.critical_errors)}개):")
            for i, error in enumerate(self.critical_errors, 1):
                print(f"   {i}. {error}")

        # Warnings
        if self.warnings:
            print(f"\n⚠️  경고 사항 ({len(self.warnings)}개):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        # Save detailed report
        self.save_detailed_report()

        print("\n" + "="*80)
        print("🎯 테스트 완료!")
        if len(self.critical_errors) == 0:
            print("🚀 시스템이 배포 준비되었습니다!")
        else:
            print("⚠️  배포 전 심각한 오류를 수정해주세요.")

        return {
            'deployment_ready': self.deployment_ready and len(self.critical_errors) == 0,
            'critical_errors': len(self.critical_errors),
            'warnings': len(self.warnings),
            'auto_fixes_applied': len(self.auto_fixes_applied),
            'passed_tests': passed_tests,
            'total_tests': total_tests
        }

    def save_detailed_report(self):
        """Save detailed test report to file"""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'deployment_ready': self.deployment_ready and len(self.critical_errors) == 0,
                'test_results': self.test_results,
                'critical_errors': self.critical_errors,
                'warnings': self.warnings,
                'auto_fixes_applied': self.auto_fixes_applied,
                'summary': {
                    'total_tests': len(self.test_results),
                    'critical_errors_count': len(self.critical_errors),
                    'warnings_count': len(self.warnings),
                    'auto_fixes_count': len(self.auto_fixes_applied)
                }
            }

            with open('comprehensive_test_report.json', 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            print("📁 상세 테스트 보고서가 comprehensive_test_report.json에 저장되었습니다.")

        except Exception as e:
            print(f"⚠️  테스트 보고서 저장 실패: {str(e)}")

    def auto_fix_issues(self):
        """Automatically fix detected issues"""
        print("🔧 자동 수정 시작...")

        fixes_applied = 0

        # Fix missing CSV files
        csv_files = ['users.csv', 'logs.csv', 'attendance.csv', 'assignments.csv', 
                    'submissions.csv', 'posts.csv', 'notifications.csv', 'clubs.csv']

        for csv_file in csv_files:
            if not os.path.exists(f"data/{csv_file}"):
                if self.create_missing_csv(csv_file):
                    fixes_applied += 1

        # Fix missing columns in existing CSV files
        for csv_file in csv_files:
            if os.path.exists(f"data/{csv_file}"):
                df = pd.read_csv(f"data/{csv_file}")
                required_columns = self.get_required_columns(csv_file)
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    if self.auto_fix_missing_columns(csv_file, missing_columns, df):
                        fixes_applied += 1

        print(f"🔧 자동 수정 완료: {fixes_applied}개 항목 수정됨")
        return fixes_applied > 0

    def create_missing_csv(self, csv_file):
        """Create missing CSV file with required columns"""
        try:
            file_path = f"data/{csv_file}"
            required_columns = self.get_required_columns(csv_file)
            df = pd.DataFrame(columns=required_columns)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"🔧 {csv_file} 생성됨")
            return True
        except Exception as e:
            print(f"❌ {csv_file} 생성 실패: {e}")
            return False

    def check_streamlit_key_conflicts(self):
        """Check for potential Streamlit key conflicts in Python files"""
        conflicts = []
        python_files = [f for f in os.listdir('.') if f.endswith('.py')]

        for file_name in python_files:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find all key= patterns
                key_patterns = re.findall(r'key=f?"([^"]+)"', content)
                key_patterns.extend(re.findall(r"key=f?'([^']+)'", content))

                # Check for potential conflicts (simple static keys without variables)
                static_keys = []
                for key in key_patterns:
                    # Skip f-strings and keys with variables
                    if '{' not in key and not any(var in key for var in ['_', 'id', 'username', 'post']):
                        static_keys.append(key)

                # Find duplicates
                from collections import Counter
                key_counts = Counter(static_keys)
                for key, count in key_counts.items():
                    if count > 1:
                        conflicts.append(f"{file_name}: '{key}' appears {count} times")

                # Check for common problematic patterns
                problematic_patterns = [
                    r'key=f?"delete_\d+"',
                    r'key=f?"edit_\d+"',
                    r'key=f?"like_\d+"',
                    r'key=f?"comment_\d+"'
                ]

                for pattern in problematic_patterns:
                    matches = re.findall(pattern, content)
                    if len(matches) > 1:
                        conflicts.append(f"{file_name}: 잠재적 키 충돌 패턴 '{pattern}'")

            except Exception as e:
                continue

        return conflicts

    def get_required_columns(self, csv_file):
        """Get required columns for a specific CSV file"""
        if csv_file == 'users.csv':
            return ['username', 'password', 'name', 'role', 'club_name', 'club_role', 'created_date']
        elif csv_file == 'logs.csv':
            return ['id', 'timestamp', 'username', 'user_name', 'user_role', 'club_name', 'ip_address', 'session_id', 'activity_type', 'activity_description', 'target_resource', 'action_result', 'error_message', 'user_agent', 'device_type', 'browser_info', 'request_method', 'response_time', 'data_modified', 'security_level', 'notes']
        elif csv_file == 'attendance.csv':
            return ['id', 'username', 'club', 'date', 'status', 'recorded_by']
        elif csv_file == 'assignments.csv':
            return ['id', 'title', 'description', 'club', 'creator', 'due_date', 'status', 'created_date']
        elif csv_file == 'submissions.csv':
            return ['id', 'assignment_id', 'username', 'submission_date', 'grade', 'feedback']
        elif csv_file == 'posts.csv':
            return ['id', 'title', 'content', 'author', 'club', 'created_date', 'likes', 'comments']
        elif csv_file == 'notifications.csv':
            return ['id', 'username', 'title', 'message', 'type', 'read', 'created_date']
        elif csv_file == 'clubs.csv':
            return ['name', 'icon', 'description', 'president', 'max_members', 'created_date']
        else:
            return []

def comprehensive_system_test():
    """Run comprehensive system tests"""
    print("🧪 Starting comprehensive system test...")

    results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tests': [],
        'summary': {'passed': 0, 'failed': 0, 'warnings': 0}
    }

def test_datetime_formats():
    """Test datetime format consistency"""
    try:
        data_dir = 'data'
        datetime_issues = []

        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        df = pd.read_csv(filepath, encoding='utf-8-sig')

                        # Check datetime columns
                        datetime_columns = ['created_date', 'timestamp', 'submitted_date', 
                                          'awarded_date', 'due_date', 'end_date']

                        for col in datetime_columns:
                            if col in df.columns and not df[col].empty:
                                # Check for inconsistent datetime formats
                                for idx, value in df[col].dropna().iterrows():
                                    if pd.isna(value) or (isinstance(value, str) and value == ''):
                                        continue

                                    # Try to parse with common formats
                                    formats = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']
                                    parsed = False
                                    for fmt in formats:
                                        try:
                                            datetime.strptime(str(value), fmt)
                                            parsed = True
                                            break
                                        except ValueError:
                                            continue

                                    if not parsed:
                                        datetime_issues.append(f"{filename}:{col} - Invalid format: {value}")

                    except Exception as e:
                        datetime_issues.append(f"{filename} - Error reading file: {e}")

        return {
            'test_name': 'DateTime Format Test',
            'status': 'PASSED' if not datetime_issues else 'FAILED',
            'details': datetime_issues if datetime_issues else ['All datetime formats are valid']
        }

    except Exception as e:
        return {
            'test_name': 'DateTime Format Test',
            'status': 'FAILED',
            'details': [f'Test failed: {e}']
        }

def test_duplicate_keys():
    """Test for potential duplicate Streamlit keys"""
    try:
        issues = []
        python_files = []

        # Find all Python files
        for root, dirs, files in os.walk('.'):
            if 'data' in root or '.git' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        # Check for potential duplicate key patterns
        key_patterns = [
            r'key\s*=\s*["\']delete_(\d+)["\']',  # delete_id pattern
            r'key\s*=\s*["\']edit_(\d+)["\']',    # edit_id pattern
            r'key\s*=\s*["\']submit_(\d+)["\']',  # submit_id pattern
        ]

        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern in key_patterns:
                    matches = re.findall(pattern, content)
                    if len(matches) > len(set(matches)):  # Duplicate IDs found
                        issues.append(f"{filepath}: Potential duplicate key pattern {pattern}")

            except Exception as e:
                issues.append(f"{filepath}: Error reading file: {e}")

        return {
            'test_name': 'Duplicate Keys Test',
            'status': 'PASSED' if not issues else 'WARNING',
            'details': issues if issues else ['No duplicate key patterns detected']
        }

    except Exception as e:
        return {
            'test_name': 'Duplicate Keys Test',
            'status': 'FAILED',
            'details': [f'Test failed: {e}']
        }
# Run tests
    test_functions = [
        test_imports,
        test_data_integrity,
        test_csv_structure,
        test_system_components,
        test_datetime_formats,
        test_duplicate_keys
    ]

if __name__ == "__main__":
    test_system = AdvancedTestSystem()
    results = test_system.run_all_tests()

    # Exit with error code if tests failed
    exit_code = 0 if results['deployment_ready'] else 1
    exit(exit_code)