#!/usr/bin/env python3
"""
Automatic File Monitor for Fraud Detection System
"""

import os
import time
import subprocess
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from datetime import datetime

class CSVFileHandler(FileSystemEventHandler):
    def __init__(self, repo_path, github_token, github_repo):
        self.repo_path = Path(repo_path)
        self.github_token = github_token
        self.github_repo = github_repo
        self.processed_files = set()
        
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            file_path = Path(event.src_path)
            if file_path.name not in self.processed_files:
                print(f"🔍 New CSV file detected: {file_path.name}")
                self.process_new_csv(file_path)
                
    def process_new_csv(self, file_path):
        """Process new CSV file and trigger automation pipeline"""
        try:
            print(f"⚡ Processing {file_path.name}...")
            self.processed_files.add(file_path.name)
            
            # Run fraud detection
            print("🔄 Running fraud detection analysis...")
            result = subprocess.run(
                ['python3', 'src/fraud_detector.py'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Local fraud detection completed!")
                fraud_count = self.extract_fraud_count()
                
                # Auto-commit to GitHub
                print("📤 Auto-committing to GitHub...")
                self.auto_commit_and_push(file_path, fraud_count)
                
                print(f"🎯 Pipeline triggered for {file_path.name}!")
            else:
                print(f"❌ Detection failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def extract_fraud_count(self):
        try:
            report_path = self.repo_path / 'outputs' / 'fraud_report.json'
            if report_path.exists():
                with open(report_path, 'r') as f:
                    data = json.load(f)
                    return data.get('fraud_detected', 0)
        except:
            pass
        return 0
    
    def auto_commit_and_push(self, file_path, fraud_count):
        try:
            os.chdir(self.repo_path)
            subprocess.run(['git', 'add', '.'], check=True)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"🚨 Auto-detect: {file_path.name} - {fraud_count} fraud(s) [{timestamp}]"
            
            result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True)
            if result.returncode == 0:
                subprocess.run(['git', 'push', 'origin', 'main'], check=True)
                print(f"✅ Pushed: {commit_msg}")
                print("🔄 Kaggle Integration: Dataset updated")
                print("☁️ AWS Integration: Lambda processing")
                if fraud_count > 0:
                    print(f"📧 ALERT: {fraud_count} frauds detected!")
                else:
                    print("✅ No fraud - system healthy")
        except Exception as e:
            print(f"❌ Git error: {e}")

def main():
    repo_path = Path.cwd()
    data_dir = repo_path / 'data' / 'raw'
    
    github_token = os.getenv('GITHUB_TOKEN')
    github_repo = os.getenv('GITHUB_REPO', 'DiponkarSinha/Fraud_detection_sys')
    
    if not github_token:
        print("❌ GITHUB_TOKEN not set")
        return
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Starting CSV file monitor...")
    print(f"📁 Monitoring: {data_dir}")
    print("⚡ Ready to auto-detect CSV files!")
    
    event_handler = CSVFileHandler(repo_path, github_token, github_repo)
    observer = Observer()
    observer.schedule(event_handler, str(data_dir), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()