import streamlit as st
import pandas as pd
from datetime import datetime
import traceback
import logging

class ErrorHandler:
    def __init__(self):
        self.error_log_file = 'data/error_log.csv'
        self.initialize_error_log()
    
    def initialize_error_log(self):
        """Initialize error log CSV file"""
        try:
            import os
            if not os.path.exists('data'):
                os.makedirs('data')
            
            if not os.path.exists(self.error_log_file):
                error_df = pd.DataFrame(columns=[
                    'timestamp', 'error_type', 'error_message', 'traceback',
                    'user', 'context', 'severity'
                ])
                error_df.to_csv(self.error_log_file, index=False, encoding='utf-8-sig')
        except Exception:
            pass  # Fail silently to avoid cascading errors
    
    def safe_execute(self, func, *args, default_return=None, context="", **kwargs):
        """Safely execute a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.log_error(e, context)
            return default_return
    
    def log_error(self, error, context="", severity="Medium"):
        """Log error to CSV file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user = getattr(st.session_state, 'user', {}).get('username', 'Unknown') if hasattr(st.session_state, 'user') else 'Unknown'
            
            error_entry = {
                'timestamp': timestamp,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc(),
                'user': user,
                'context': context,
                'severity': severity
            }
            
            # Read existing errors
            try:
                error_df = pd.read_csv(self.error_log_file, encoding='utf-8-sig')
            except:
                error_df = pd.DataFrame()
            
            # Add new error
            new_error_df = pd.DataFrame([error_entry])
            if not error_df.empty:
                error_df = pd.concat([error_df, new_error_df], ignore_index=True)
            else:
                error_df = new_error_df
            
            # Keep only last 1000 errors
            if len(error_df) > 1000:
                error_df = error_df.tail(1000)
            
            # Save to CSV
            error_df.to_csv(self.error_log_file, index=False, encoding='utf-8-sig')
            
        except Exception:
            # Fail silently to avoid cascading errors
            pass
    
    def safe_datetime_parse(self, date_value):
        """Safely parse datetime values"""
        if pd.isna(date_value) or date_value is None:
            return datetime.now()
        
        try:
            if isinstance(date_value, datetime):
                return date_value
            
            # Convert to string and try parsing
            date_str = str(date_value).strip()
            if not date_str or date_str.lower() in ['nan', 'none', '']:
                return datetime.now()
            
            # Try multiple formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Use pandas as fallback
            return pd.to_datetime(date_value, errors='coerce')
            
        except Exception:
            return datetime.now()
    
    def safe_dataframe_operation(self, operation_func, df, *args, **kwargs):
        """Safely perform DataFrame operations"""
        try:
            if df is None or df.empty:
                return pd.DataFrame()
            
            return operation_func(df, *args, **kwargs)
        except Exception as e:
            self.log_error(e, "DataFrame Operation")
            return df  # Return original dataframe if operation fails
    
    def safe_csv_read(self, filepath, default_columns=None):
        """Safely read CSV files"""
        try:
            if not os.path.exists(filepath):
                if default_columns:
                    return pd.DataFrame(columns=default_columns)
                return pd.DataFrame()
            
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            return df if not df.empty else pd.DataFrame(columns=default_columns or [])
            
        except Exception as e:
            self.log_error(e, f"CSV Read: {filepath}")
            return pd.DataFrame(columns=default_columns or [])
    
    def safe_csv_write(self, df, filepath):
        """Safely write CSV files"""
        try:
            if df is None:
                df = pd.DataFrame()
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return True
            
        except Exception as e:
            self.log_error(e, f"CSV Write: {filepath}")
            return False
    
    def validate_user_input(self, input_value, input_type="string", required=False):
        """Validate user input safely"""
        try:
            if required and (input_value is None or str(input_value).strip() == ""):
                return False, "이 필드는 필수입니다."
            
            if input_value is None:
                return True, None
            
            if input_type == "string":
                return True, str(input_value).strip()
            elif input_type == "int":
                return True, int(input_value)
            elif input_type == "float":
                return True, float(input_value)
            elif input_type == "date":
                parsed_date = self.safe_datetime_parse(input_value)
                return True, parsed_date
            else:
                return True, input_value
                
        except Exception as e:
            return False, f"입력값 검증 실패: {str(e)}"
    
    def wrap_streamlit_component(self, component_func, *args, **kwargs):
        """Wrap Streamlit components with error handling"""
        try:
            return component_func(*args, **kwargs)
        except Exception as e:
            self.log_error(e, f"Streamlit Component: {component_func.__name__}")
            st.error(f"컴포넌트 오류가 발생했습니다: {str(e)}")
            return None

# Global error handler instance
error_handler = ErrorHandler()
# Safe wrapper functions for common operations
def safe_dataframe_filter(df, condition_func):
    """Safely filter DataFrame"""
    try:
        if df.empty:
            return df
        return df[condition_func(df)]
    except Exception:
        return df

def safe_dataframe_sort(df, column, ascending=True):
    """Safely sort DataFrame"""
    try:
        if df.empty or column not in df.columns:
            return df
        return df.sort_values(column, ascending=ascending)
    except Exception:
        return df

def safe_metric_calculation(numerator, denominator, default=0):
    """Safely calculate metrics"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception:
        return default
