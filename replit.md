# 폴라리스반 동아리 관리 시스템

## Overview

이 프로젝트는 초등학교 6학년 폴라리스반을 위한 종합적인 동아리 관리 웹 플랫폼입니다. Streamlit을 기반으로 구축되었으며, 모바일 친화적인 UI/UX로 설계되어 학생들과 교사가 동아리 활동을 효율적으로 관리할 수 있도록 지원합니다.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit 기반 웹 애플리케이션
- **Design Philosophy**: 모바일 전용 UI/UX (사이드바 사용 금지)
- **Navigation**: 상단 탭/버튼 기반 인터페이스
- **Responsive Design**: 모바일 우선 설계로 다양한 화면 크기 지원

### Backend Architecture
- **Language**: Python 3.11
- **Application Structure**: 모듈화된 시스템 아키텍처
- **Data Processing**: Pandas를 활용한 데이터 조작 및 분석
- **File Management**: CSV 기반 데이터 저장 및 관리

### Data Storage Architecture
- **Primary Storage**: CSV 파일 기반 데이터 저장
- **Database Policy**: 관계형 데이터베이스 사용 금지
- **Data Location**: `/data/` 디렉터리에 모든 CSV 파일 저장
- **Backup Strategy**: ZIP 파일 기반 백업 시스템

## Key Components

### Core Systems
1. **AuthManager** (`auth.py`): 사용자 인증 및 권한 관리
2. **DataManager** (`data_manager.py`): CSV 데이터 CRUD 작업 관리
3. **UIComponents** (`ui_components.py`): 공통 UI 구성 요소

### Feature Systems
1. **BoardSystem** (`board_system.py`): 게시판 및 공지사항 관리
2. **ChatSystem** (`chat_system.py`): 실시간 채팅 및 커뮤니케이션
3. **AssignmentSystem** (`assignment_system.py`): 과제 생성, 제출, 채점
4. **QuizSystem** (`quiz_system.py`): 퀴즈 생성 및 자동 채점
5. **AttendanceSystem** (`attendance_system.py`): 출석 관리 및 통계
6. **ScheduleSystem** (`schedule_system.py`): 일정 관리 및 캘린더
7. **VoteSystem** (`vote_system.py`): 투표 시스템
8. **GallerySystem** (`gallery_system.py`): 작품 갤러리 및 이미지 관리

### Advanced Features
1. **ReportGenerator** (`report_generator.py`): PDF/DOCX 보고서 자동 생성
2. **GamificationSystem** (`gamification_system.py`): 포인트, 배지, 레벨업 시스템
3. **AIAssistant** (`ai_assistant.py`): AI 기반 학습 도우미
4. **SearchSystem** (`search_system.py`): 통합 검색 기능
5. **LoggingSystem** (`logging_system.py`): 시스템 활동 로그 관리

### Administrative Systems
1. **AdminSystem** (`admin_system.py`): 관리자 도구 및 시스템 관리
2. **BackupSystem** (`backup_system.py`): 데이터 백업 및 복원
3. **NotificationSystem** (`notification_system.py`): 알림 및 메시지 시스템

## Data Flow

### User Authentication Flow
1. 사용자 로그인 요청 → AuthManager 검증
2. 사용자 권한 확인 → 역할별 기능 접근 제어
3. 세션 상태 관리 → Streamlit session_state 활용

### Data Management Flow
1. 사용자 액션 → 해당 시스템 모듈 호출
2. DataManager를 통한 CSV 파일 읽기/쓰기
3. 데이터 검증 및 처리 → UI 업데이트
4. LoggingSystem을 통한 활동 기록

### Role-Based Access Control
- **선생님**: 모든 기능 접근 가능 (시스템 관리자)
- **회장/부회장**: 동아리 관리 및 보고서 작성
- **총무**: 출석 및 과제 관리
- **동아리원**: 기본 학습 및 참여 기능

## External Dependencies

### Python Packages
- **streamlit**: 웹 애플리케이션 프레임워크
- **pandas**: 데이터 조작 및 분석
- **plotly**: 인터랙티브 차트 및 그래프
- **pillow**: 이미지 처리
- **python-docx**: Word 문서 생성
- **reportlab**: PDF 문서 생성
- **trafilatura**: 웹 콘텐츠 추출

### File Format Support
- CSV: 주요 데이터 저장 형식
- PDF: 보고서 및 문서 출력
- DOCX: Word 문서 생성
- Images: JPG, PNG 이미지 파일 지원

## Deployment Strategy

### Platform Configuration
- **Runtime**: Python 3.11 환경
- **Deployment Target**: Replit autoscale 배포
- **Port Configuration**: 5000번 포트 사용
- **Startup Command**: `streamlit run app.py --server.port 5000`

### Data Initialization
- 시스템 첫 실행 시 기본 사용자 계정 자동 생성
- 6개 기본 동아리 (코딩, 댄스, 만들기, 미스테리탐구, 줄넘기, 풍선아트) 설정
- 샘플 데이터를 통한 시스템 기능 검증

### Security Considerations
- 사용자 비밀번호 평문 저장 (교육 환경 특성상)
- 역할 기반 접근 제어 구현
- 활동 로그를 통한 감사 추적

## Recent Changes
- June 25, 2025: Comprehensive error handling system implemented
- June 25, 2025: All datetime operations fixed with safe parsing
- June 25, 2025: Enhanced logging system with recursion prevention
- June 25, 2025: Complete data integrity verification and auto-repair
- June 25, 2025: Performance optimizations and safe wrappers added
- June 25, 2025: All critical errors resolved, system deployment-ready

## Changelog
- June 25, 2025: Initial setup and comprehensive enhancement

## User Preferences

Preferred communication style: Simple, everyday language.