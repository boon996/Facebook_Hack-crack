#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook简化版一亿密码库破解器
移除emoji字符，兼容Windows GBK编码
"""

import hashlib
import threading
import time
import argparse
import sys
import os
from queue import Queue
from password_database_manager import PasswordDatabaseManager, PasswordGenerator

class FacebookSimpleCracker:
    def __init__(self, target_hash, hash_method='md5', threads=8, chunk_size=10000):
        """
        初始化Facebook一亿密码库破解器
        """
        self.target_hash = target_hash.lower()
        self.hash_method = hash_method.lower()
        self.threads = threads
        self.chunk_size = chunk_size
        
        # 状态变量
        self.found_password = None
        self.stop_flag = threading.Event()
        self.attempts = 0
        self.start_time = None
        self.lock = threading.Lock()
        
        # 密码库管理器
        self.password_manager = PasswordDatabaseManager(chunk_size=chunk_size)
        self.password_generator = PasswordGenerator()
        
        # 工作队列
        self.password_queue = Queue(maxsize=threads * 2)
        
        # 统计信息
        self.total_passwords = 0
        self.processed_passwords = 0
        self.current_batch = 0
        
        print(f"Facebook一亿密码库破解器初始化")
        print(f"线程数: {threads}")
        print(f"目标哈希: {target_hash}")
        print(f"哈希方法: {hash_method.upper()}")
        print(f"批处理大小: {chunk_size}")
        print("=" * 60)
    
    def hash_password(self, password):
        """计算密码哈希值"""
        try:
            if self.hash_method == 'md5':
                return hashlib.md5(password.encode()).hexdigest()
            elif self.hash_method == 'sha1':
                return hashlib.sha1(password.encode()).hexdigest()
            elif self.hash_method == 'sha256':
                return hashlib.sha256(password.encode()).hexdigest()
            else:
                return hashlib.md5(password.encode()).hexdigest()
        except Exception:
            return ""
    
    def worker_thread(self, thread_id):
        """工作线程函数"""
        while not self.stop_flag.is_set():
            try:
                # 从队列获取密码批次
                password_batch = self.password_queue.get(timeout=1)
                if password_batch is None:
                    break
                
                # 处理密码批次
                for password in password_batch:
                    if self.stop_flag.is_set():
                        break
                    
                    # 计算哈希
                    computed_hash = self.hash_password(password)
                    
                    with self.lock:
                        self.attempts += 1
                        self.processed_passwords += 1
                    
                    # 检查匹配
                    if computed_hash == self.target_hash:
                        with self.lock:
                            if not self.found_password:
                                self.found_password = password
                                self.stop_flag.set()
                                print(f"\n线程 {thread_id} 找到密码!")
                                print(f"密码: {password}")
                                break
                
                self.password_queue.task_done()
                
            except Exception as e:
                continue
    
    def progress_monitor(self):
        """进度监控线程"""
        last_attempts = 0
        
        while not self.stop_flag.is_set():
            time.sleep(5)  # 每5秒更新一次
            
            with self.lock:
                current_attempts = self.attempts
                elapsed_time = time.time() - self.start_time if self.start_time else 0
                
                if elapsed_time > 0:
                    rate = current_attempts / elapsed_time
                    recent_rate = (current_attempts - last_attempts) / 5
                    
                    progress = (self.processed_passwords / self.total_passwords * 100) if self.total_passwords > 0 else 0
                    
                    print(f"\r进度: {progress:.2f}% | 尝试: {current_attempts:,} | "
                          f"速率: {rate:.0f}/s | 最近: {recent_rate:.0f}/s | "
                          f"批次: {self.current_batch}", end="", flush=True)
                
                last_attempts = current_attempts
    
    def load_password_database(self):
        """加载密码库"""
        print("加载一亿密码库...")
        
        # 添加主密码库文件
        password_file = "billion_passwords.txt"
        if os.path.exists(password_file):
            self.password_manager.add_password_file(password_file)
            print(f"加载密码库: {password_file}")
        else:
            print(f"密码库文件不存在: {password_file}")
            return False
        
        # 统计总密码数
        print("统计密码数量...")
        self.total_passwords = self.password_manager.count_total_passwords()
        print(f"总密码数: {self.total_passwords:,}")
        
        return True
    
    def dictionary_attack(self):
        """字典攻击 - 使用一亿密码库"""
        print("启动一亿密码库字典攻击")
        print(f"目标哈希: {self.target_hash}")
        print(f"哈希方法: {self.hash_method.upper()}")
        print("=" * 60)
        
        # 加载密码库
        if not self.load_password_database():
            print("无法加载密码库，攻击终止")
            return False
        
        self.start_time = time.time()
        self.attempts = 0
        
        # 启动工作线程
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker_thread, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 启动进度监控
        progress_thread = threading.Thread(target=self.progress_monitor)
        progress_thread.daemon = True
        progress_thread.start()
        
        # 分批处理密码
        try:
            for batch_num, password_batch in enumerate(self.password_manager.get_password_batch(self.chunk_size)):
                if self.stop_flag.is_set():
                    break
                
                self.current_batch = batch_num + 1
                self.password_queue.put(password_batch)
                
                # 控制队列大小，避免内存溢出
                while self.password_queue.qsize() > self.threads * 2:
                    if self.stop_flag.is_set():
                        break
                    time.sleep(0.1)
            
            # 等待所有任务完成
            self.password_queue.join()
            
        except KeyboardInterrupt:
            print("\n用户中断攻击")
            self.stop_flag.set()
        
        # 停止所有线程
        for _ in range(self.threads):
            self.password_queue.put(None)
        
        for t in threads:
            t.join(timeout=1)
        
        # 计算结果
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        
        if self.found_password:
            print(f"\n字典攻击破解成功！")
            print(f"密码: {self.found_password}")
            print(f"用时: {elapsed_time:.2f} 秒")
            print(f"尝试次数: {self.attempts:,}")
            if elapsed_time > 0:
                print(f"平均速率: {self.attempts / elapsed_time:,.0f} 次/秒")
            return True
        else:
            print(f"\n字典攻击未找到密码")
            print(f"用时: {elapsed_time:.2f} 秒")
            print(f"尝试次数: {self.attempts:,}")
            if elapsed_time > 0:
                print(f"平均速率: {self.attempts / elapsed_time:,.0f} 次/秒")
            return False
    
    def smart_attack(self, target_info=None):
        """智能攻击 - 优先级密码 + 社会工程学"""
        print("启动智能攻击")
        print(f"目标哈希: {self.target_hash}")
        print("=" * 60)
        
        self.start_time = time.time()
        self.attempts = 0
        
        # 生成智能密码列表
        smart_passwords = []
        
        # 1. Facebook特定密码
        smart_passwords.extend(self.password_generator.generate_facebook_specific_passwords())
        
        # 2. 常见密码
        smart_passwords.extend(self.password_generator.common_passwords)
        
        # 3. 基于目标信息的密码
        if target_info:
            smart_passwords.extend(self.password_generator.generate_social_passwords(target_info))
        
        # 去重
        smart_passwords = list(dict.fromkeys(smart_passwords))
        
        print(f"智能密码总数: {len(smart_passwords)}")
        
        # 测试智能密码
        for i, password in enumerate(smart_passwords):
            computed_hash = self.hash_password(password)
            self.attempts += 1
            
            if computed_hash == self.target_hash:
                end_time = time.time()
                elapsed_time = end_time - self.start_time
                
                print(f"智能攻击破解成功！")
                print(f"密码: {password}")
                print(f"用时: {elapsed_time:.2f} 秒")
                print(f"尝试次数: {self.attempts}")
                return password
        
        print(f"智能攻击未找到密码")
        return None
    
    def hybrid_attack(self, target_info=None):
        """混合攻击 - 智能攻击 + 字典攻击"""
        print("启动混合攻击模式")
        print("=" * 60)
        
        # 1. 先进行智能攻击
        result = self.smart_attack(target_info)
        if result:
            return result
        
        print("\n智能攻击未成功，切换到字典攻击...")
        print("=" * 60)
        
        # 2. 进行字典攻击
        if self.dictionary_attack():
            return self.found_password
        
        return None

def main():
    parser = argparse.ArgumentParser(description='Facebook一亿密码库破解器')
    parser.add_argument('hash', help='目标哈希值')
    parser.add_argument('-m', '--method', choices=['md5', 'sha1', 'sha256'], 
                       default='md5', help='哈希方法 (默认: md5)')
    parser.add_argument('-t', '--threads', type=int, default=8, 
                       help='线程数 (默认: 8)')
    parser.add_argument('-a', '--attack', choices=['smart', 'dictionary', 'hybrid'], 
                       default='hybrid', help='攻击模式 (默认: hybrid)')
    parser.add_argument('-u', '--username', help='目标用户名')
    parser.add_argument('-e', '--email', help='目标邮箱')
    parser.add_argument('-n', '--name', help='目标姓名')
    parser.add_argument('-c', '--chunk', type=int, default=10000,
                       help='批处理大小 (默认: 10000)')
    
    args = parser.parse_args()
    
    # 创建破解器
    cracker = FacebookSimpleCracker(
        target_hash=args.hash,
        hash_method=args.method,
        threads=args.threads,
        chunk_size=args.chunk
    )
    
    # 准备目标信息
    target_info = {}
    if args.username:
        target_info['username'] = args.username
    if args.email:
        target_info['email'] = args.email
    if args.name:
        target_info['name'] = args.name
    
    # 执行攻击
    start_time = time.time()
    
    try:
        if args.attack == 'smart':
            result = cracker.smart_attack(target_info)
        elif args.attack == 'dictionary':
            result = cracker.dictionary_attack()
        else:  # hybrid
            result = cracker.hybrid_attack(target_info)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 60)
        if result or cracker.found_password:
            password = result or cracker.found_password
            print("破解成功！")
            print(f"密码: {password}")
        else:
            print("破解失败")
        
        print(f"\n攻击统计:")
        print(f"  总用时: {total_time:.2f} 秒")
        print(f"  总尝试: {cracker.attempts:,}")
        if total_time > 0:
            print(f"  平均速率: {cracker.attempts / total_time:,.0f} 次/秒")
        print(f"  使用线程: {args.threads}")
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        sys.exit(1)

if __name__ == "__main__":
    main()