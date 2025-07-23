#!/usr/bin/env python3
"""
Singapore News Scraper Test Runner (Python Version)
Cross-platform test execution script
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
import shutil

class Colors:
    """ANSI color codes for console output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class TestRunner:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.reports_dir = self.test_dir / "reports"
        self.coverage_dir = self.test_dir / "coverage"
        
        # Create directories
        self.reports_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)
        
        self.start_time = time.time()
        self.test_results = {}

    def print_status(self, message):
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

    def print_success(self, message):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

    def print_warning(self, message):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

    def print_error(self, message):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

    def command_exists(self, command):
        """Check if a command exists in PATH"""
        return shutil.which(command) is not None

    def run_command(self, command, cwd=None, check=True):
        """Run a shell command and return the result"""
        if isinstance(command, str):
            command = command.split()
        
        self.print_status(f"Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            self.print_error(f"Command failed: {e}")
            self.print_error(f"STDOUT: {e.stdout}")
            self.print_error(f"STDERR: {e.stderr}")
            raise

    def install_python_deps(self):
        """Install Python test dependencies"""
        self.print_status("Installing Python test dependencies...")
        
        if not self.command_exists('pip'):
            raise RuntimeError("pip not found. Please install Python and pip first.")
        
        # Install test requirements
        requirements_file = self.test_dir / "requirements.txt"
        if requirements_file.exists():
            self.run_command(f"pip install -r {requirements_file}")
        
        # Install main requirements if available
        main_requirements = self.project_root / "requirements.txt"
        if main_requirements.exists():
            try:
                self.run_command(f"pip install -r {main_requirements}")
            except subprocess.CalledProcessError:
                self.print_warning("Could not install main requirements.txt")

    def install_node_deps(self):
        """Install Node.js test dependencies"""
        self.print_status("Installing Node.js test dependencies...")
        
        if not self.command_exists('npm'):
            raise RuntimeError("npm not found. Please install Node.js and npm first.")
        
        package_json = self.test_dir / "package.json"
        if package_json.exists():
            self.run_command("npm install", cwd=self.test_dir)

    def run_python_tests(self):
        """Run Python unit tests with pytest"""
        self.print_status("Running Python unit tests...")
        
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}:{self.project_root}/scripts:{env.get('PYTHONPATH', '')}"
        
        command = [
            'python', '-m', 'pytest', 'tests/',
            '--verbose',
            '--cov=scripts',
            f'--cov-report=html:{self.coverage_dir}/python',
            f'--cov-report=xml:{self.coverage_dir}/python/coverage.xml',
            '--cov-report=term-missing',
            f'--junit-xml={self.reports_dir}/python-results.xml',
            '--tb=short'
        ]
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                env=env,
                check=True
            )
            self.test_results['python'] = {'status': 'success', 'exit_code': result.returncode}
            self.print_success("Python tests completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.test_results['python'] = {'status': 'failed', 'exit_code': e.returncode}
            self.print_error(f"Python tests failed with exit code {e.returncode}")
            return False

    def run_javascript_tests(self):
        """Run JavaScript unit tests with Jest"""
        self.print_status("Running JavaScript unit tests...")
        
        try:
            self.run_command(
                "npm test -- --coverage --coverageDirectory=coverage/javascript --ci --watchAll=false",
                cwd=self.test_dir
            )
            self.test_results['javascript'] = {'status': 'success'}
            self.print_success("JavaScript tests completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.test_results['javascript'] = {'status': 'failed', 'exit_code': e.returncode}
            self.print_error("JavaScript tests failed")
            return False

    def run_api_tests(self):
        """Run API integration tests"""
        self.print_status("Running API integration tests...")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}:{self.project_root}/scripts:{env.get('PYTHONPATH', '')}"
        
        command = [
            'python', '-m', 'pytest', 'tests/test_api_integration.py',
            '--verbose',
            f'--junit-xml={self.reports_dir}/api-results.xml',
            '--tb=short'
        ]
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                env=env,
                check=True
            )
            self.test_results['api'] = {'status': 'success'}
            self.print_success("API integration tests completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.test_results['api'] = {'status': 'failed', 'exit_code': e.returncode}
            self.print_error("API integration tests failed")
            return False

    def run_e2e_tests(self):
        """Run E2E tests with Playwright"""
        self.print_status("Running E2E tests with Playwright...")
        
        if not self.command_exists('npx'):
            self.print_warning("npx not found, skipping E2E tests")
            return False
        
        # Install Playwright browsers if needed
        try:
            self.run_command("npx playwright --version", cwd=self.test_dir, check=False)
        except:
            self.print_status("Installing Playwright browsers...")
            self.run_command("npx playwright install", cwd=self.test_dir)
        
        try:
            self.run_command(
                "npx playwright test --reporter=html --reporter=junit",
                cwd=self.test_dir
            )
            self.test_results['e2e'] = {'status': 'success'}
            self.print_success("E2E tests completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.test_results['e2e'] = {'status': 'failed', 'exit_code': e.returncode}
            self.print_error("E2E tests failed")
            return False

    def run_security_tests(self):
        """Run security analysis"""
        self.print_status("Running security tests...")
        
        security_issues = 0
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password.*=.*["\'].*["\']',
            r'api.*key.*=.*["\'].*["\']',
            r'token.*=.*["\'].*["\']',
            r'secret.*=.*["\'].*["\']'
        ]
        
        import re
        
        for pattern in secret_patterns:
            for file_pattern in ['**/*.py', '**/*.js', '**/*.json']:
                for file_path in self.project_root.glob(file_pattern):
                    if file_path.is_file() and not str(file_path).startswith(str(self.test_dir)):
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            if re.search(pattern, content, re.IGNORECASE):
                                self.print_warning(f"Potential hardcoded secret in {file_path}")
                                security_issues += 1
                        except:
                            continue
        
        if security_issues == 0:
            self.print_success("No obvious security issues found")
        else:
            self.print_warning(f"Found {security_issues} potential security issues")
        
        self.test_results['security'] = {
            'status': 'completed',
            'issues_found': security_issues
        }
        return True

    def run_performance_tests(self):
        """Run basic performance checks"""
        self.print_status("Running performance tests...")
        
        issues = 0
        
        # Check file sizes
        for file_pattern in ['**/*.py', '**/*.js']:
            for file_path in self.project_root.glob(file_pattern):
                if file_path.is_file() and not str(file_path).startswith(str(self.test_dir)):
                    try:
                        line_count = len(file_path.read_text(encoding='utf-8').splitlines())
                        if line_count > 1000:
                            self.print_warning(f"Large file: {file_path} ({line_count} lines)")
                            issues += 1
                    except:
                        continue
        
        self.test_results['performance'] = {
            'status': 'completed',
            'issues_found': issues
        }
        self.print_success("Performance tests completed")
        return True

    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_status("Generating test report...")
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'test_results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed': sum(1 for r in self.test_results.values() if r.get('status') == 'success'),
                'failed': sum(1 for r in self.test_results.values() if r.get('status') == 'failed'),
            }
        }
        
        # Save JSON report
        report_file = self.reports_dir / f"test-summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.print_success(f"Test report generated: {report_file}")
        
        # Print summary
        print(f"\n{Colors.WHITE}=== TEST SUMMARY ==={Colors.NC}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Total test suites: {report_data['summary']['total_tests']}")
        print(f"Passed: {Colors.GREEN}{report_data['summary']['passed']}{Colors.NC}")
        print(f"Failed: {Colors.RED}{report_data['summary']['failed']}{Colors.NC}")
        
        return report_data['summary']['failed'] == 0

    def cleanup(self):
        """Clean up temporary files"""
        self.print_status("Cleaning up temporary files...")
        
        # Remove Python cache files
        for cache_dir in self.project_root.rglob('__pycache__'):
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir, ignore_errors=True)
        
        for pyc_file in self.project_root.rglob('*.pyc'):
            if pyc_file.is_file():
                pyc_file.unlink(missing_ok=True)
        
        self.print_success("Cleanup completed")

    def run_all_tests(self, args):
        """Run all specified tests"""
        success = True
        
        # Install dependencies unless skipped
        if not args.skip_install:
            try:
                self.install_python_deps()
                self.install_node_deps()
            except Exception as e:
                self.print_error(f"Failed to install dependencies: {e}")
                return False
        
        # Run tests based on arguments
        if args.all or args.python:
            if not self.run_python_tests():
                success = False
        
        if args.all or args.javascript:
            if not self.run_javascript_tests():
                success = False
        
        if args.all or args.api:
            if not self.run_api_tests():
                success = False
        
        if args.all or args.e2e:
            if not self.run_e2e_tests():
                success = False
        
        if args.all or args.security:
            if not self.run_security_tests():
                success = False
        
        if args.all or args.performance:
            if not self.run_performance_tests():
                success = False
        
        # Generate report
        report_success = self.generate_report()
        
        # Cleanup
        self.cleanup()
        
        return success and report_success

def main():
    parser = argparse.ArgumentParser(description='Singapore News Scraper Test Runner')
    parser.add_argument('--skip-install', action='store_true', help='Skip dependency installation')
    parser.add_argument('--python', action='store_true', help='Run Python tests only')
    parser.add_argument('--javascript', action='store_true', help='Run JavaScript tests only')
    parser.add_argument('--api', action='store_true', help='Run API tests only')
    parser.add_argument('--e2e', action='store_true', help='Run E2E tests only')
    parser.add_argument('--security', action='store_true', help='Run security tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    
    args = parser.parse_args()
    
    # If no specific test type is specified, run all
    args.all = not any([args.python, args.javascript, args.api, args.e2e, args.security, args.performance])
    
    runner = TestRunner()
    
    try:
        success = runner.run_all_tests(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        runner.print_warning("Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        runner.print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()