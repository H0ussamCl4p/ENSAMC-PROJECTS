"""Script to add @login_required decorator to all dashboard routes."""
from pathlib import Path
import re

# Routes that should NOT be protected (login/logout/2FA)
EXCLUDED_ROUTES = ['/login', '/verify-2fa', '/resend-2fa', '/logout']


def add_login_required():
    root = Path(__file__).resolve().parents[1]
    dashboard_path = root / 'dashboard.py'
    content = dashboard_path.read_text(encoding='utf-8')
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if it's a route decorator
        if line.strip().startswith('@app.route('):
            # Extract route path
            match = re.search(r"@app\.route\('([^']+)'", line)
            if match:
                route_path = match.group(1)
                
                # Check if this route should be protected
                if route_path not in EXCLUDED_ROUTES:
                    # Check if @login_required is already there
                    if i + 1 < len(lines) and '@login_required' not in lines[i + 1]:
                        # Add @login_required after the @app.route line
                        new_lines.append(line)
                        new_lines.append('@login_required')
                        i += 1
                        continue
        
        new_lines.append(line)
        i += 1
    
    # Write back
    dashboard_path.write_text('\n'.join(new_lines), encoding='utf-8')
    
    print("✅ Added @login_required to all protected routes")


if __name__ == '__main__':
    add_login_required()
