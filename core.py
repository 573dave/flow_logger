import os
import sys
import inspect
import time
import platform
import psutil
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List
from pathlib import Path
from string import Template


# Global enable/disable flag - Set this to False to disable all logging globally
FLOW_LOGGER_ENABLED = True

for module_name, module in sys.modules.items():
    if hasattr(module, 'FLOW_LOGGER_ENABLED'):
        FLOW_LOGGER_ENABLED = getattr(module, 'FLOW_LOGGER_ENABLED')
        break

class _FlowLoggerCore:
    def __init__(self):
        self.logs: List[Dict] = []
        self._start_time = datetime.now()
        self.report_path = None
    
    def _serialize_value(self, value: Any) -> Any:
        """Safely serialize any value with truncation for large objects."""
        try:
            if isinstance(value, (int, float, str, bool, type(None))):
                return value
            
            if isinstance(value, (list, tuple, set)):
                return [self._serialize_value(v) for v in value[:100]]  # Limit large collections
            
            if isinstance(value, dict):
                return {str(k): self._serialize_value(v) for k, v in list(value.items())[:100]}
            
            # Handle custom objects
            if hasattr(value, '__dict__'):
                return f"<{value.__class__.__name__}: {str(value)[:100]}>"
            
            return str(value)[:200]  # Truncate long string representations
        except Exception:
            return f"<Non-serializable {type(value).__name__}>"

    def _get_caller_info(self) -> Dict[str, str]:
        """Get information about who called the function."""
        stack = inspect.stack()
        # Look for the first frame that's not in this module
        for frame in stack[2:]:  # Skip this function and the wrapper
            if 'core.py' not in frame.filename:
                return {
                    'file': os.path.basename(frame.filename),
                    'filename': frame.filename,
                    'line': frame.lineno,
                    'caller': frame.function if frame.function != '<module>' else 'main'
                }
        return {'file': 'unknown', 'filename' : 'unknown', 'line': 0, 'caller': 'unknown'}

    def __call__(self, func):
        """Decorator implementation."""
        if not FLOW_LOGGER_ENABLED:
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            start_timestamp = datetime.now().strftime('%b-%d-%Y_%H:%M:%S.%f')[:-3]
            caller_info = self._get_caller_info()
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = e
                success = False
                raise
            finally:
                duration = (time.perf_counter() - start_time) * 1000  # ms
                end_timestamp = datetime.now().strftime('%b-%d-%Y_%H:%M:%S.%f')[:-3]
                
                # Create log entry
                log_entry = {
                    'timestamp': start_timestamp,
                    'end_timestamp': end_timestamp,
                    'function': func.__name__,
                    'args': self._serialize_value(args),
                    'kwargs': self._serialize_value(kwargs),
                    'result': self._serialize_value(result) if success else str(result),
                    'success': success,
                    'duration_ms': round(duration, 2),
                    'caller': caller_info
                }
                
                self.logs.append(log_entry)
                
                # Generate report on program exit if we have logs
                if not hasattr(self, '_atexit_registered'):
                    import atexit
                    atexit.register(self._generate_report)
                    self._atexit_registered = True
                
            return result
        
        return wrapper

    def _generate_report(self):
        """Generate HTML report on program exit."""
        if not self.logs:
            return
                
        try:
            main_script_path = Path(sys.modules['__main__'].__file__).parent
        except (KeyError, AttributeError):
            try:
                main_script_path = Path(self.logs[0]['caller']['file']).parent
            except (IndexError, KeyError):
                try:
                    import inspect
                    frame = inspect.stack()[-1]
                    main_script_path = Path(frame.filename).parent
                except Exception:
                    main_script_path = Path.cwd()
        
        timestamp = self._start_time.strftime('%b-%d-%Y_%H-%M-%S')
        self.report_path = main_script_path / f'FlowLogger_{timestamp}.html'
        
        generate_html_report(self.logs, self.report_path)
        print(f"\nFlow Logger Report generated: {self.report_path}")


def get_system_info() -> Dict[str, Dict[str, str]]:
    """Gather system information organized by category."""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'System': {
                'OS': f"{platform.system()} {platform.release()}",
                'Python': sys.version.split()[0],
                'Process ID': str(os.getpid())
            },
            'CPU': {
                'Cores': f"{psutil.cpu_count()} ({psutil.cpu_count(logical=False)} physical)",
                'Usage': f"{psutil.cpu_percent()}%"
            },
            'Memory': {
                'Total': f"{memory.total / (1024**3):.1f} GB",
                'Available': f"{memory.available / (1024**3):.1f} GB",
                'Usage': f"{memory.percent}%"
            },
            'Storage': {
                'Total': f"{disk.total / (1024**3):.1f} GB",
                'Free': f"{disk.free / (1024**3):.1f} GB",
                'Usage': f"{(disk.used / disk.total * 100):.1f}%"
            }
        }
    except Exception as e:
        return {'Error': {'Message': f"Failed to gather system information: {str(e)}"}}

def generate_log_entry_html(log: Dict) -> str:
    """Generate HTML for a single log entry."""
    status_class = 'success' if log['success'] else 'error'
    status_text = 'SUCCESS' if log['success'] else 'ERROR'
    
    template_path = Path(__file__).parent / 'templates' / 'log_entry.html'
    try:
        template = Template(template_path.read_text(encoding='utf-8'))
        return template.safe_substitute(
            function=log['function'],
            duration=log['duration_ms'],
            status_class=status_class,
            status_text=status_text,
            caller_file=log['caller']['file'],
            caller_line=log['caller']['line'],
            caller_func=log['caller']['caller'],
            timestamp=log['timestamp'],
            end_timestamp=log['end_timestamp'],
            args=log['args'],
            kwargs=log['kwargs'],
            result=log['result']
        )
    except FileNotFoundError:
        raise RuntimeError("Log entry template not found")

def _generate_system_info_html(info: Dict[str, Dict[str, str]]) -> str:
    """Generate HTML for system information section."""
    sections = []
    
    for section, metrics in info.items():
        metrics_html = []
        for label, value in metrics.items():
            metrics_html.append(
                f'<div class="system-info-item">'
                f'<span class="system-info-label">{label}</span>'
                f'<span class="system-info-value">{value}</span>'
                f'</div>'
            )
        
        sections.append(
            f'<div class="system-info-section">'
            f'<h3 class="system-info-title">{section}</h3>'
            f'<div class="system-info-metrics">'
            f'{"".join(metrics_html)}'
            f'</div>'
            f'</div>'
        )
    
    return (
        '<div class="system-info">'
        f'{"".join(sections)}'
        '</div>'
    )

def generate_html_report(logs: List[Dict], output_path: Path) -> None:
    """Generate an HTML report from the logs."""
    template_path = Path(__file__).parent / 'templates' / 'report_template.html'
    
    try:
        template = Template(template_path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise RuntimeError(
            "HTML template not found. Ensure the templates directory is included in the package."
        )

    # Calculate statistics
    total_calls = len(logs)
    avg_duration = sum(log['duration_ms'] for log in logs) / total_calls if total_calls else 0
    error_rate = (sum(1 for log in logs if not log['success']) / total_calls * 100) if total_calls else 0

    # Get system information
    system_info = get_system_info()
    system_info_html = _generate_system_info_html(system_info)

    # Generate log entries HTML
    log_entries_html = [generate_log_entry_html(log) for log in logs]  # First call to last

    # Fill template
    html_content = template.safe_substitute(
        timestamp=logs[0]['timestamp'] if logs else datetime.now().strftime('%b-%d-%Y_%H:%M:%S.%f')[:-3],
        filename=logs[0]['caller']['filename'] if logs else "unknown",  # Add this line
        total_calls=total_calls,
        avg_duration=f"{avg_duration:.2f}",
        error_rate=f"{error_rate:.1f}",
        system_info=system_info_html,
        log_entries='\n'.join(log_entries_html)
    )

    # Write report
    output_path.write_text(html_content, encoding='utf-8')

# Single instance for the entire application
flow_logger = _FlowLoggerCore()