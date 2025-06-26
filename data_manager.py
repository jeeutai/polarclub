import pandas as pd
import os
from datetime import datetime
import streamlit as st
import warnings
warnings.filterwarnings('ignore')
from error_handler import error_handler

class DataManager:
    def __init__(self):
        self.data_dir = 'data'
        self.ensure_data_directory()
        self.initialize_csv_files()

    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def initialize_csv_files(self):
        """Initialize all CSV files with headers if they don't exist"""
        csv_structures = {
            'clubs.csv': ['name', 'icon', 'description', 'president', 'max_members', 'created_date', 'meet_link'],
            'posts.csv': ['id', 'title', 'content', 'author', 'club', 'created_date', 'likes', 'comments', 'image_path', 'image_data', 'tags'],
            'chat_logs.csv': ['id', 'username', 'club', 'message', 'timestamp', 'deleted'],
            'assignments.csv': ['id', 'title', 'description', 'club', 'creator', 'due_date', 'status', 'created_date'],
            'submissions.csv': ['id', 'assignment_id', 'username', 'content', 'file_path', 'submitted_date', 'grade', 'feedback'],
            'attendance.csv': ['id', 'username', 'club', 'date', 'status', 'note', 'recorded_by'],
            'schedule.csv': ['id', 'title', 'description', 'club', 'date', 'time', 'location', 'creator', 'created_date'],
            'votes.csv': ['id', 'title', 'description', 'options', 'club', 'creator', 'end_date', 'created_date'],
            'badges.csv': ['id', 'username', 'badge_name', 'badge_icon', 'description', 'awarded_date', 'awarded_by'],
            'notifications.csv': ['id', 'username', 'title', 'message', 'type', 'read', 'created_date']
        }

        for filename, columns in csv_structures.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                df = pd.DataFrame(columns=columns)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')

        # Initialize clubs.csv with default clubs
        self.initialize_clubs()
        
        # Migrate existing CSV files if needed
        self.migrate_csv_files()

    def initialize_clubs(self):
        """Initialize clubs with default data"""
        clubs_file = os.path.join(self.data_dir, 'clubs.csv')
        clubs_df = pd.read_csv(clubs_file, encoding='utf-8-sig')

        if clubs_df.empty:
            default_clubs = [
                {
                    'name': '코딩',
                    'icon': '💻',
                    'description': '프로그래밍과 컴퓨터 과학을 배우는 동아리',
                    'president': '조성우',
                    'max_members': 20,
                    'created_date': '2024-01-15 09:00:00',
                    'meet_link': 'https://meet.google.com/dbx-ozrs-bma'
                },
                {
                    'name': '댄스',
                    'icon': '💃',
                    'description': '다양한 춤을 배우고 공연하는 동아리',
                    'president': '백주아',
                    'max_members': 15,
                    'created_date': '2024-01-15 09:00:00',
                    'meet_link': ''
                },
                {
                    'name': '만들기',
                    'icon': '🔨',
                    'description': '손으로 만드는 모든 것을 탐구하는 동아리',
                    'president': '김보경',
                    'max_members': 12,
                    'created_date': '2024-01-15 09:00:00',
                    'meet_link': ''
                },
                {
                    'name': '미스테리탐구',
                    'icon': '🔍',
                    'description': '신비한 현상과 미스터리를 탐구하는 동아리',
                    'president': '오채윤',
                    'max_members': 10,
                    'created_date': '2024-01-15 09:00:00',
                    'meet_link': ''
                },
                {
                    'name': '줄넘기',
                    'icon': '🪢',
                    'description': '줄넘기 기술을 연마하고 체력을 기르는 동아리',
                    'president': '김제이',
                    'max_members': 25,
                    'created_date': '2024-01-15 09:00:00',
                    'meet_link': ''
                },
                {
                    'name': '풍선아트',
                    'icon': '🎈',
                    'description': '풍선으로 다양한 작품을 만드는 동아리',
                    'president': '최명준',
                    'max_members': 15,
                    'created_date': '2024-01-15 09:00:00',
                    'meet_link': ''
                }
            ]

            df = pd.DataFrame(default_clubs)
            df.to_csv(clubs_file, index=False, encoding='utf-8-sig')

    def migrate_csv_files(self):
        """Migrate existing CSV files to add missing columns"""
        # Add image_data column to posts.csv if missing
        posts_file = os.path.join(self.data_dir, 'posts.csv')
        if os.path.exists(posts_file):
            try:
                posts_df = pd.read_csv(posts_file, encoding='utf-8-sig')
                if 'image_data' not in posts_df.columns:
                    posts_df['image_data'] = ''
                    posts_df.to_csv(posts_file, index=False, encoding='utf-8-sig')
            except Exception:
                pass  # Ignore errors during migration

    def safe_parse_datetime(self, date_string):
        """Safely parse datetime strings with multiple format support"""
        if pd.isna(date_string) or not date_string or date_string == '':
            return datetime.now()
            
        # Convert to string and remove any extra whitespace
        try:
            date_string = str(date_string).strip() if date_string is not None else ""
            if not date_string or date_string == 'nan' or date_string == 'None':
                return datetime.now()
                
            # Try parsing with different formats
            formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            # Try pandas parsing as last resort
            try:
                return pd.to_datetime(date_string)
            except:
                return datetime.now()
                
        except (TypeError, AttributeError):
            return datetime.now()
    
    def safe_string_filter(self, df, column, filter_value, case_sensitive=False):
        """Safely apply string filter to DataFrame column"""
        try:
            if df.empty or column not in df.columns:
                return df
            
            # Ensure column is string type
            df[column] = df[column].astype(str)
            
            if case_sensitive:
                return df[df[column].str.contains(filter_value, na=False)]
            else:
                return df[df[column].str.contains(filter_value, case=False, na=False)]
        except Exception:
            # If filtering fails, return original dataframe
            return df
        
        # Common datetime formats to try
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',  # With microseconds
            '%Y-%m-%d %H:%M:%S',     # Without microseconds
            '%Y-%m-%d',              # Date only
            '%Y/%m/%d %H:%M:%S',     # Alternative separator
            '%Y/%m/%d',              # Alternative date only
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(date_string, format=fmt)
            except (ValueError, TypeError):
                continue
        
        # If all formats fail, try pandas automatic parsing
        try:
            return pd.to_datetime(date_string, errors='coerce')
        except:
            return None

    def load_csv(self, filename):
        """Load CSV file and return DataFrame with safe datetime parsing"""
        return error_handler.safe_execute(
            self._load_csv_internal, filename, 
            default_return=pd.DataFrame(),
            context=f"Loading CSV: {filename}"
        )
    
    def _load_csv_internal(self, filename):
        """Internal CSV loading logic"""
        if not filename.endswith('.csv'):
            filename += '.csv'
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            return pd.DataFrame()

        # Check if file is empty or has only headers
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read().strip()
            lines = content.split('\n')
            
            # If file has only headers or is empty, return empty DataFrame with columns
            if len(lines) <= 1 or (len(lines) == 2 and lines[1].strip() == ''):
                if len(lines) >= 1 and lines[0].strip():
                    columns = [col.strip() for col in lines[0].split(',')]
                    return pd.DataFrame(columns=columns)
                else:
                    return pd.DataFrame()
        
        # Load with safe parsing
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        
        # Handle datetime columns safely
        datetime_columns = ['created_date', 'submitted_date', 'awarded_date', 'timestamp', 'due_date', 'end_date', 'date']
        for col in datetime_columns:
            if col in df.columns and not df.empty:
                df[col] = df[col].apply(error_handler.safe_datetime_parse)
        
        return df

    def save_csv(self, filename, dataframe):
        """Save DataFrame to CSV file"""
        return error_handler.safe_execute(
            self._save_csv_internal, filename, dataframe,
            default_return=False,
            context=f"Saving CSV: {filename}"
        )
    
    def _save_csv_internal(self, filename, dataframe):
        """Internal CSV saving logic"""
        if not filename.endswith('.csv'):
            filename += '.csv'
        filepath = os.path.join(self.data_dir, filename)
        
        # Ensure dataframe is not None
        if dataframe is None:
            dataframe = pd.DataFrame()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        dataframe.to_csv(filepath, index=False, encoding='utf-8-sig')
        return True

    def get_user_clubs(self, username):
        """Get clubs that user belongs to"""
        try:
            users_df = pd.read_csv(os.path.join(self.data_dir, 'users.csv'), encoding='utf-8-sig')
            user_clubs = users_df[users_df['username'] == username][['club_name', 'club_role']]
            user_clubs = user_clubs.rename(columns={'club_role': 'role'})
            return user_clubs
        except:
            return pd.DataFrame()

    def generate_id(self, filename):
        """Generate unique ID for new records"""
        df = self.load_csv(filename)
        if df.empty or 'id' not in df.columns:
            return 1
        return df['id'].max() + 1 if not df['id'].isna().all() else 1

    def add_record(self, filename, record):
        """Add new record to CSV file"""
        try:
            df = self.load_csv(filename)

            # Generate ID if not provided
            if 'id' not in record:
                record['id'] = self.generate_id(filename)

            # Add timestamp if not provided
            if 'created_date' not in record:
                record['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
            
            # Log data access
            if hasattr(st.session_state, 'logging_system') and hasattr(st.session_state, 'user'):
                st.session_state.logging_system.log_data_access(
                    st.session_state.user.get('username', 'System'),
                    filename,
                    'INSERT',
                    1
                )
            
            return self.save_csv(filename, df)
        except Exception as e:
            # Log error
            if hasattr(st.session_state, 'logging_system') and hasattr(st.session_state, 'user'):
                st.session_state.logging_system.log_error(
                    st.session_state.user.get('username', 'System'),
                    'Database Error',
                    str(e),
                    f"add_record to {filename}"
                )
            return False

    def update_record(self, filename, record_id, updates):
        """Update existing record in CSV file"""
        try:
            df = self.load_csv(filename)
            if df.empty:
                return False

            # Find and update the record
            mask = df['id'] == record_id
            if mask.any():
                for key, value in updates.items():
                    # Handle type conversion carefully
                    if key in df.columns:
                        try:
                            # If column has a specific dtype and value is compatible, convert
                            if df[key].dtype != 'object' and pd.notna(value):
                                if df[key].dtype in ['int64', 'float64'] and str(value).replace('.', '').replace('-', '').isdigit():
                                    value = pd.to_numeric(value, errors='coerce')
                            df.loc[mask, key] = value
                        except (ValueError, TypeError):
                            # If conversion fails, convert column to object type
                            df[key] = df[key].astype('object')
                            df.loc[mask, key] = value
                    else:
                        df.loc[mask, key] = value

                # Log data access
                if hasattr(st.session_state, 'logging_system') and hasattr(st.session_state, 'user'):
                    st.session_state.logging_system.log_data_access(
                        st.session_state.user.get('username', 'System'),
                        filename,
                        'UPDATE',
                        1
                    )
                
                # Save updated data
                return self.save_csv(filename, df)
            return False
        except Exception as e:
            # Log error
            if hasattr(st.session_state, 'logging_system') and hasattr(st.session_state, 'user'):
                st.session_state.logging_system.log_error(
                    st.session_state.user.get('username', 'System'),
                    'Database Error',
                    str(e),
                    f"update_record in {filename}"
                )
            return False

    def delete_record(self, filename, record_id):
        """Delete record from CSV file"""
        try:
            df = self.load_csv(filename)
            original_count = len(df)
            df = df[df['id'] != record_id]
            
            # Log data access
            deleted_count = original_count - len(df)
            if hasattr(st.session_state, 'logging_system') and hasattr(st.session_state, 'user'):
                st.session_state.logging_system.log_data_access(
                    st.session_state.user.get('username', 'System'),
                    filename,
                    'DELETE',
                    deleted_count
                )
            
            return self.save_csv(filename, df)
        except Exception as e:
            # Log error
            if hasattr(st.session_state, 'logging_system') and hasattr(st.session_state, 'user'):
                st.session_state.logging_system.log_error(
                    st.session_state.user.get('username', 'System'),
                    'Database Error',
                    str(e),
                    f"delete_record from {filename}"
                )
            return False

    def backup_data(self):
        """Create backup of all CSV files"""
        import zipfile
        from datetime import datetime

        try:
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

            with zipfile.ZipFile(backup_filename, 'w') as zipf:
                for filename in os.listdir(self.data_dir):
                    if filename.endswith('.csv'):
                        zipf.write(os.path.join(self.data_dir, filename), filename)

            return backup_filename
        except Exception as e:
            st.error(f"Backup error: {e}")
            return None
# Performance optimizations added to data_manager.py
def optimized_load_csv(self, filename, use_cache=True):
    """Optimized CSV loading with caching"""
    cache_key = f"csv_cache_{filename}"
    
    if use_cache and hasattr(st.session_state, cache_key):
        return getattr(st.session_state, cache_key)
    
    df = self._load_csv_internal(filename)
    
    if use_cache:
        setattr(st.session_state, cache_key, df)
    
    return df

def clear_csv_cache(self):
    """Clear CSV cache"""
    cache_keys = [key for key in st.session_state.keys() if key.startswith('csv_cache_')]
    for key in cache_keys:
        del st.session_state[key]
