import os

def create_project_structure():
    """Create the complete project directory structure"""
    
    # Define all directories
    directories = [
        'ml_models',
        'database/schema',
        'database/migrations',
        'database/procedures',
        'database/seeds',
        'backend/models',
        'backend/services',
        'backend/api/auth',
        'backend/api/student',
        'backend/api/faculty',
        'backend/api/admin',
        'backend/api/prediction',
        'backend/api/common',
        'backend/middleware',
        'backend/utils',
        'backend/tasks',
        'backend/ml_integration',
        'frontend/public',
        'frontend/src/css',
        'frontend/src/js/api',
        'frontend/src/js/auth',
        'frontend/src/js/components',
        'frontend/src/js/pages',
        'frontend/src/js/utils',
        'frontend/src/assets/images',
        'frontend/src/assets/fonts',
        'frontend/src/assets/vendor',
        'frontend/templates/layouts',
        'frontend/templates/auth',
        'frontend/templates/student',
        'frontend/templates/faculty',
        'frontend/templates/admin',
        'frontend/templates/components',
        'frontend/templates/errors',
        'scripts/setup',
        'scripts/data',
        'scripts/maintenance',
        'scripts/deployment',
        'tests/unit',
        'tests/integration',
        'tests/e2e',
        'tests/fixtures',
        'logs/app',
        'logs/error',
        'logs/access',
        'logs/prediction',
        'docs/api',
        'docs/guides',
        'docs/technical',
        'docs/images',
        'deployment/nginx',
        'deployment/systemd',
        'deployment/kubernetes',
        'deployment/terraform',
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created: {directory}")
    
    # Define all files to create
    files = [
        'backend/__init__.py',
        'backend/models/__init__.py',
        'backend/services/__init__.py',
        'backend/api/__init__.py',
        'backend/middleware/__init__.py',
        'backend/utils/__init__.py',
        'backend/ml_integration/__init__.py',
        'backend/api/auth/__init__.py',
        'backend/api/student/__init__.py',
        'backend/api/faculty/__init__.py',
        'backend/api/admin/__init__.py',
        'backend/api/prediction/__init__.py',
        'backend/api/common/__init__.py',
        'README.md',
        'requirements.txt',
        'package.json',
        '.env.example',
        '.gitignore',
        'config.py',
        'wsgi.py',
    ]
    
    # Create files
    for file_path in files:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Create empty file
        with open(file_path, 'w') as f:
            if file_path.endswith('.py') and '__init__' in file_path:
                f.write('# Python package initialization\n')
            else:
                f.write('')
        print(f"Created: {file_path}")
    
    print("\nProject structure created successfully!")

if __name__ == "__main__":
    create_project_structure()