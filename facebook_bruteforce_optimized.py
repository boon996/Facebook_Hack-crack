import hashlib
import itertools
import string
import time
import os
import threading
import queue
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from argparse import ArgumentParser
import random
import sys
from collections import deque
from facebook_smart_generator import FacebookSmartPasswordGenerator

class FacebookBruteForceOptimized:
    def __init__(self, num_threads=None):
        self.attempts = 0
        self.start_time = None
        self.found_password = None
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.num_threads = num_threads or min(multiprocessing.cpu_count() * 2, 16)
        self.progress_queue = queue.Queue()
        self.smart_generator = FacebookSmartPasswordGenerator()
        self.failed_attempts = []
        
    def hash_password(self, password, method='md5'):
        """将密码转换为哈希值 - 优化版本"""
        password_bytes = password.encode('utf-8')
        if method == 'md5':
            return hashlib.md5(password_bytes).hexdigest()
        elif method == 'sha1':
            return hashlib.sha1(password_bytes).hexdigest()
        elif method == 'sha256':
            return hashlib.sha256(password_bytes).hexdigest()
        else:
            raise ValueError("不支持的哈希方法")
    

    
    def worker_thread(self, password_chunk, target_hash, method, thread_id):
        """工作线程函数"""
        local_attempts = 0
        
        for password in password_chunk:
            if self.stop_flag.is_set():
                break
                
            local_attempts += 1
            
            try:
                if self.hash_password(password, method) == target_hash:
                    with self.lock:
                        if not self.found_password:
                            self.found_password = password
                            self.stop_flag.set()
                            print(f"\n🎉 密码破解成功！")
                            print(f"密码: {password}")
                            return password
                else:
                    # 记录失败的尝试用于自适应学习
                    if len(self.failed_attempts) < 10000:  # 限制内存使用
                        with self.lock:
                            self.failed_attempts.append(password)
            except Exception as e:
                continue
            
            # 更新进度
            if local_attempts % 1000 == 0:
                with self.lock:
                    self.attempts += local_attempts
                    local_attempts = 0
                    self.show_progress(password, thread_id)
        
        # 更新剩余的尝试次数
        with self.lock:
            self.attempts += local_attempts
        
        return None
    
    def parallel_brute_force(self, target_hash, max_length=8, method='md5'):
        """并行暴力破解主函数"""
        self.start_time = time.time()
        self.attempts = 0
        self.found_password = None
        self.stop_flag.clear()
        
        print(f"🚀 启动Facebook优化暴力攻击")
        print(f"线程数: {self.num_threads}")
        print(f"最大密码长度: {max_length}")
        print(f"哈希算法: {method.upper()}")
        print("=" * 60)
        
        # 阶段1: 使用智能生成器的优先级队列
        print("🎯 阶段1: 智能优先级密码队列")
        priority_groups = self.smart_generator.get_priority_queue(max_length)
        
        # 超高优先级
        if priority_groups['ultra_high']:
            result = self._parallel_attack_phase(priority_groups['ultra_high'], target_hash, method, "超高优先级")
            if result:
                return result
        
        # 高优先级
        if priority_groups['high']:
            result = self._parallel_attack_phase(priority_groups['high'], target_hash, method, "高优先级")
            if result:
                return result
        
        # 中优先级
        if priority_groups['medium']:
            result = self._parallel_attack_phase(priority_groups['medium'], target_hash, method, "中优先级")
            if result:
                return result
        
        # 阶段3: 数字暴力破解
        print("🎯 阶段3: 数字密码暴力破解")
        for length in range(4, min(max_length + 1, 9)):
            print(f"尝试 {length} 位数字密码...")
            digit_passwords = [''.join(p) for p in itertools.product('0123456789', repeat=length)]
            
            result = self._parallel_attack_phase(digit_passwords, target_hash, method, f"{length}位数字")
            if result:
                return result
        
        # 阶段4: 字母数字组合 (智能采样)
        print("🎯 阶段4: 字母数字组合 (智能采样)")
        for length in range(3, min(max_length + 1, 7)):
            print(f"尝试长度为 {length} 的字母数字组合...")
            
            # 智能生成策略：优先常见模式
            charset = string.ascii_lowercase + string.digits
            total_combinations = len(charset) ** length
            
            if total_combinations > 500000:  # 如果组合太多，使用智能采样
                passwords = self._generate_smart_combinations(charset, length, 500000)
            else:
                passwords = [''.join(p) for p in itertools.product(charset, repeat=length)]
            
            result = self._parallel_attack_phase(passwords, target_hash, method, f"{length}位字母数字")
            if result:
                return result
        
        # 阶段5: 自适应密码生成
        print("🎯 阶段5: 自适应密码生成")
        if self.failed_attempts:
            adaptive_passwords = self.smart_generator.generate_adaptive_passwords(self.failed_attempts)
            result = self._parallel_attack_phase(adaptive_passwords, target_hash, method, "自适应模式")
            if result:
                return result
        
        # 阶段6: 低优先级模式
        print("🎯 阶段6: 低优先级模式")
        if priority_groups['low']:
            result = self._parallel_attack_phase(priority_groups['low'], target_hash, method, "低优先级")
            if result:
                return result
        
        return None
    
    def _parallel_attack_phase(self, password_list, target_hash, method, phase_name):
        """并行攻击阶段"""
        if not password_list:
            return None
        
        # 将密码列表分块给不同线程
        chunk_size = max(1, len(password_list) // self.num_threads)
        password_chunks = [password_list[i:i + chunk_size] 
                          for i in range(0, len(password_list), chunk_size)]
        
        print(f"📊 {phase_name}: {len(password_list)} 个密码，{len(password_chunks)} 个线程块")
        
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []
            
            for i, chunk in enumerate(password_chunks):
                if chunk:  # 确保块不为空
                    future = executor.submit(self.worker_thread, chunk, target_hash, method, i)
                    futures.append(future)
            
            # 等待结果
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=1)
                    if result:
                        # 取消其他任务
                        for f in futures:
                            f.cancel()
                        return result
                except Exception as e:
                    continue
        
        return None
    
    def _generate_smart_combinations(self, charset, length, max_count):
        """智能生成密码组合 - 优先常见模式"""
        passwords = []
        
        # 策略1: 字母开头 + 数字结尾 (最常见)
        letters = string.ascii_lowercase
        digits = string.digits
        
        for letter_len in range(1, length):
            digit_len = length - letter_len
            if digit_len > 0:
                # 生成一些字母+数字的组合
                for _ in range(min(10000, max_count // 4)):
                    letter_part = ''.join(random.choices(letters, k=letter_len))
                    digit_part = ''.join(random.choices(digits, k=digit_len))
                    passwords.append(letter_part + digit_part)
        
        # 策略2: 随机采样
        remaining = max_count - len(passwords)
        if remaining > 0:
            all_combinations = list(itertools.product(charset, repeat=length))
            if len(all_combinations) > remaining:
                sampled = random.sample(all_combinations, remaining)
                passwords.extend([''.join(p) for p in sampled])
            else:
                passwords.extend([''.join(p) for p in all_combinations])
        
        return passwords[:max_count]
    
    def show_progress(self, current_password, thread_id=0):
        """显示进度信息"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            rate = self.attempts / elapsed if elapsed > 0 else 0
            
            print(f"\r⚡ 线程{thread_id} | 尝试: {self.attempts:,} | "
                  f"速率: {rate:,.0f}/秒 | 当前: {current_password[:20]}...", end='', flush=True)
    
    def gpu_accelerated_attack(self, target_hash, password_list, method='md5'):
        """GPU加速攻击 (需要安装hashcat或类似工具)"""
        print("🔥 GPU加速功能需要额外配置，当前使用CPU多线程模式")
        return self.parallel_brute_force(target_hash, method=method)
    
    def crack_facebook_password(self, target_hash, method='md5', max_length=8, use_gpu=False):
        """主破解函数"""
        print(f"🎯 目标哈希: {target_hash}")
        print(f"🔧 哈希方法: {method.upper()}")
        
        if use_gpu:
            result = self.gpu_accelerated_attack(target_hash, [], method)
        else:
            result = self.parallel_brute_force(target_hash, max_length, method)
        
        if result:
            elapsed = time.time() - self.start_time
            print(f"\n✅ 破解成功！")
            print(f"🔑 密码: {result}")
            print(f"⏱️  用时: {elapsed:.2f} 秒")
            print(f"🔢 总尝试: {self.attempts:,}")
            print(f"⚡ 平均速率: {self.attempts/elapsed:,.2f} 次/秒")
            return result
        else:
            elapsed = time.time() - self.start_time
            print(f"\n❌ 破解失败")
            print(f"⏱️  用时: {elapsed:.2f} 秒")
            print(f"🔢 总尝试: {self.attempts:,}")
            return None

def main():
    parser = ArgumentParser(description='Facebook密码优化暴力破解工具')
    parser.add_argument('hash', help='要破解的哈希值')
    parser.add_argument('-m', '--method', choices=['md5', 'sha1', 'sha256'], 
                       default='md5', help='哈希算法 (默认: md5)')
    parser.add_argument('-l', '--max-length', type=int, default=8, 
                       help='最大密码长度 (默认: 8)')
    parser.add_argument('-t', '--threads', type=int, 
                       help='线程数 (默认: CPU核心数x2)')
    parser.add_argument('--gpu', action='store_true', 
                       help='启用GPU加速 (实验性)')
    
    args = parser.parse_args()
    
    # 验证哈希格式
    hash_lengths = {'md5': 32, 'sha1': 40, 'sha256': 64}
    if len(args.hash) != hash_lengths[args.method]:
        print(f"❌ 错误: {args.method.upper()} 哈希长度应为 {hash_lengths[args.method]} 字符")
        return
    
    # 创建破解器实例
    cracker = FacebookBruteForceOptimized(num_threads=args.threads)
    
    try:
        result = cracker.crack_facebook_password(
            args.hash, 
            method=args.method, 
            max_length=args.max_length,
            use_gpu=args.gpu
        )
        
        if result:
            print(f"\n🎉 破解完成！密码是: {result}")
        else:
            print(f"\n😞 未能破解密码，请尝试增加最大长度或使用字典攻击")
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  用户中断破解过程")
        print(f"📊 已尝试 {cracker.attempts:,} 个密码")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    main()