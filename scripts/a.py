# a.py
from datetime import datetime

def print_time():
    """打印当前时间"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(current_time)

if __name__ == "__main__":
    print_time()
