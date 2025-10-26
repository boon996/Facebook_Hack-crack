#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import random
import string
import os
from tqdm import tqdm

class MegaWordlistGenerator:
    def __init__(self):
        self.target_count = 100_000_000  # 100M密码
        self.output_file = "mega_100m_wordlist.txt"
        
        # 常用密码组件
        self.common_words = [
            "password", "123456", "admin", "user", "login", "welcome", "qwerty",
            "facebook", "google", "apple", "microsoft", "amazon", "netflix", "spotify",
            "instagram", "twitter", "youtube", "tiktok", "snapchat", "whatsapp",
            "love", "family", "friend", "home", "work", "school", "college",
            "john", "mike", "david", "chris", "alex", "sarah", "emma", "lisa",
            "password", "secret", "private", "secure", "access", "account"
        ]
        
        self.common_numbers = [
            "123", "456", "789", "000", "111", "222", "333", "444", "555",
            "666", "777", "888", "999", "1234", "2345", "3456", "4567",
            "5678", "6789", "0123", "1111", "2222", "3333", "4444", "5555",
            "6666", "7777", "8888", "9999", "12345", "23456", "34567",
            "45678", "56789", "123456", "654321", "987654", "112233"
        ]
        
        self.years = [str(year) for year in range(1950, 2025)]
        
        self.symbols = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", 
                       "-", "_", "+", "=", "[", "]", "{", "}", "|", "\\",
                       ":", ";", "\"", "'", "<", ">", ",", ".", "?", "/"]
        
        self.common_suffixes = [
            "123", "456", "789", "1", "2", "3", "!", "@", "#", "$",
            "2023", "2024", "2025", "01", "02", "03", "99", "00"
        ]
        
        self.common_prefixes = [
            "my", "the", "new", "old", "big", "small", "good", "bad",
            "super", "mega", "ultra", "best", "top", "first", "last"
        ]
        
    def generate_common_passwords(self, count=1_000_000):
        """生成常见密码组合"""
        passwords = set()
        
        print("🔤 生成常见密码组合...")
        
        # 基础常用密码
        base_passwords = [
            "123456", "password", "123456789", "12345678", "12345", "1234567",
            "1234567890", "qwerty", "abc123", "111111", "123123", "admin",
            "letmein", "welcome", "monkey", "1234", "dragon", "master",
            "hello", "login", "princess", "solo", "qwertyuiop", "starwars"
        ]
        
        for pwd in base_passwords:
            passwords.add(pwd)
            passwords.add(pwd.upper())
            passwords.add(pwd.capitalize())
            
        # 单词 + 数字组合
        for word in self.common_words[:50]:
            for num in self.common_numbers[:20]:
                passwords.add(word + num)
                passwords.add(word.capitalize() + num)
                passwords.add(word.upper() + num)
                passwords.add(num + word)
                
        # 单词 + 年份
        for word in self.common_words[:30]:
            for year in self.years[-10:]:  # 最近10年
                passwords.add(word + year)
                passwords.add(word.capitalize() + year)
                
        # 单词 + 符号
        for word in self.common_words[:30]:
            for symbol in self.symbols[:10]:
                passwords.add(word + symbol)
                passwords.add(word.capitalize() + symbol)
                
        return list(passwords)[:count]
    
    def generate_pattern_passwords(self, count=5_000_000):
        """生成模式化密码"""
        passwords = set()
        
        print("🎯 生成模式化密码...")
        
        # 字母 + 数字模式
        for length in range(6, 13):
            for _ in range(count // 100):
                # 随机字母 + 随机数字
                letters = ''.join(random.choices(string.ascii_lowercase, k=length-3))
                numbers = ''.join(random.choices(string.digits, k=3))
                passwords.add(letters + numbers)
                passwords.add(letters.capitalize() + numbers)
                
                # 数字 + 字母
                passwords.add(numbers + letters)
                passwords.add(numbers + letters.capitalize())
                
        # 前缀 + 单词 + 后缀模式
        for prefix in self.common_prefixes[:10]:
            for word in self.common_words[:20]:
                for suffix in self.common_suffixes[:10]:
                    passwords.add(prefix + word + suffix)
                    passwords.add(prefix.capitalize() + word.capitalize() + suffix)
                    
        return list(passwords)[:count]
    
    def generate_keyboard_patterns(self, count=2_000_000):
        """生成键盘模式密码"""
        passwords = set()
        
        print("⌨️  生成键盘模式密码...")
        
        # 键盘行模式
        keyboard_rows = [
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm",
            "1234567890"
        ]
        
        for row in keyboard_rows:
            for start in range(len(row) - 3):
                for length in range(4, min(len(row) - start + 1, 12)):
                    pattern = row[start:start + length]
                    passwords.add(pattern)
                    passwords.add(pattern[::-1])  # 反向
                    passwords.add(pattern.upper())
                    passwords.add(pattern.capitalize())
                    
                    # 添加数字后缀
                    for suffix in ["123", "456", "789", "1", "2", "3"]:
                        passwords.add(pattern + suffix)
                        passwords.add(pattern.capitalize() + suffix)
        
        # 重复字符模式
        for char in string.ascii_lowercase + string.digits:
            for length in range(4, 10):
                passwords.add(char * length)
                
        return list(passwords)[:count]
    
    def generate_name_based_passwords(self, count=3_000_000):
        """生成基于姓名的密码"""
        passwords = set()
        
        print("👤 生成姓名基础密码...")
        
        # 常见英文名字
        first_names = [
            "james", "john", "robert", "michael", "william", "david", "richard",
            "charles", "joseph", "thomas", "christopher", "daniel", "paul",
            "mark", "donald", "george", "kenneth", "steven", "edward", "brian",
            "ronald", "anthony", "kevin", "jason", "matthew", "gary", "timothy",
            "jose", "larry", "jeffrey", "frank", "scott", "eric", "stephen",
            "andrew", "raymond", "gregory", "joshua", "jerry", "dennis", "walter",
            "patrick", "peter", "harold", "douglas", "henry", "carl", "arthur",
            "ryan", "roger", "joe", "juan", "jack", "albert", "jonathan", "wayne",
            "mary", "patricia", "jennifer", "linda", "elizabeth", "barbara",
            "susan", "jessica", "sarah", "karen", "nancy", "lisa", "betty",
            "helen", "sandra", "donna", "carol", "ruth", "sharon", "michelle",
            "laura", "sarah", "kimberly", "deborah", "dorothy", "lisa", "nancy",
            "karen", "betty", "helen", "sandra", "donna", "carol", "ruth"
        ]
        
        # 姓名 + 数字/年份组合
        for name in first_names:
            # 基础姓名
            passwords.add(name)
            passwords.add(name.capitalize())
            passwords.add(name.upper())
            
            # 姓名 + 数字
            for num in self.common_numbers[:15]:
                passwords.add(name + num)
                passwords.add(name.capitalize() + num)
                passwords.add(num + name)
                
            # 姓名 + 年份
            for year in self.years[-15:]:
                passwords.add(name + year)
                passwords.add(name.capitalize() + year)
                
            # 姓名 + 符号
            for symbol in ["!", "@", "#", "$", "123"]:
                passwords.add(name + symbol)
                passwords.add(name.capitalize() + symbol)
                
        return list(passwords)[:count]
    
    def generate_dictionary_mutations(self, count=10_000_000):
        """生成字典变异密码"""
        passwords = set()
        
        print("🔄 生成字典变异密码...")
        
        # 读取现有的facebook词典
        facebook_words = []
        try:
            with open("facebook_wordlist.txt", "r", encoding="utf-8") as f:
                facebook_words = [line.strip() for line in f if line.strip()]
        except:
            facebook_words = ["facebook", "meta", "instagram", "whatsapp"]
            
        # 对每个词进行变异
        for word in facebook_words + self.common_words:
            if len(word) < 3:
                continue
                
            # 基础变异
            passwords.add(word)
            passwords.add(word.upper())
            passwords.add(word.capitalize())
            passwords.add(word[::-1])  # 反向
            
            # 字符替换变异
            mutations = {
                'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'],
                's': ['$', '5'], 't': ['7'], 'l': ['1'], 'g': ['9']
            }
            
            for char, replacements in mutations.items():
                for replacement in replacements:
                    mutated = word.replace(char, replacement)
                    passwords.add(mutated)
                    passwords.add(mutated.capitalize())
                    
            # 添加前缀后缀
            for prefix in ["my", "the", "new"]:
                passwords.add(prefix + word)
                passwords.add(prefix.capitalize() + word.capitalize())
                
            for suffix in ["123", "456", "!", "@", "2024"]:
                passwords.add(word + suffix)
                passwords.add(word.capitalize() + suffix)
                
        return list(passwords)[:count]
    
    def generate_random_combinations(self, count=79_000_000):
        """生成随机组合密码"""
        passwords = set()
        
        print("🎲 生成随机组合密码...")
        
        # 纯数字密码
        for length in range(4, 12):
            for _ in range(count // 200):
                pwd = ''.join(random.choices(string.digits, k=length))
                passwords.add(pwd)
                
        # 纯字母密码
        for length in range(4, 12):
            for _ in range(count // 200):
                pwd = ''.join(random.choices(string.ascii_lowercase, k=length))
                passwords.add(pwd)
                passwords.add(pwd.capitalize())
                passwords.add(pwd.upper())
                
        # 字母数字混合
        for length in range(6, 14):
            for _ in range(count // 100):
                chars = string.ascii_lowercase + string.digits
                pwd = ''.join(random.choices(chars, k=length))
                passwords.add(pwd)
                passwords.add(pwd.capitalize())
                
        # 包含符号的密码
        for length in range(8, 16):
            for _ in range(count // 300):
                chars = string.ascii_lowercase + string.digits + "!@#$%"
                pwd = ''.join(random.choices(chars, k=length))
                passwords.add(pwd)
                
        return list(passwords)[:count]
    
    def generate_mega_wordlist(self):
        """生成100M密码库"""
        print("🚀 开始生成100M密码库...")
        print(f"📁 输出文件: {self.output_file}")
        
        all_passwords = set()
        
        # 分阶段生成不同类型的密码
        generators = [
            (self.generate_common_passwords, 1_000_000),
            (self.generate_pattern_passwords, 5_000_000),
            (self.generate_keyboard_patterns, 2_000_000),
            (self.generate_name_based_passwords, 3_000_000),
            (self.generate_dictionary_mutations, 10_000_000),
            (self.generate_random_combinations, 79_000_000)
        ]
        
        for generator_func, target_count in generators:
            print(f"\n📊 目标生成: {target_count:,} 个密码")
            passwords = generator_func(target_count)
            print(f"✅ 实际生成: {len(passwords):,} 个密码")
            all_passwords.update(passwords)
            print(f"📈 累计唯一密码: {len(all_passwords):,}")
            
        print(f"\n🎯 最终唯一密码数量: {len(all_passwords):,}")
        
        # 写入文件
        print("💾 写入密码库文件...")
        passwords_list = list(all_passwords)
        
        # 如果密码数量不足100M，用随机密码补充
        if len(passwords_list) < self.target_count:
            print(f"🔄 补充随机密码到100M...")
            needed = self.target_count - len(passwords_list)
            
            for _ in tqdm(range(needed), desc="生成补充密码"):
                length = random.randint(6, 12)
                chars = string.ascii_lowercase + string.digits
                pwd = ''.join(random.choices(chars, k=length))
                passwords_list.append(pwd)
        
        # 随机打乱顺序
        print("🔀 随机打乱密码顺序...")
        random.shuffle(passwords_list)
        
        # 写入文件
        print("💾 写入文件...")
        with open(self.output_file, "w", encoding="utf-8") as f:
            for i, password in enumerate(tqdm(passwords_list[:self.target_count], desc="写入密码")):
                f.write(password + "\n")
                
        file_size = os.path.getsize(self.output_file) / (1024 * 1024)  # MB
        print(f"\n🎉 100M密码库生成完成！")
        print(f"📁 文件: {self.output_file}")
        print(f"📊 密码数量: {self.target_count:,}")
        print(f"💾 文件大小: {file_size:.1f} MB")

def main():
    generator = MegaWordlistGenerator()
    generator.generate_mega_wordlist()

if __name__ == "__main__":
    main()