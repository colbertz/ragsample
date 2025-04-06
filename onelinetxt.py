import os
import sys

def filter_file(input_file, output_file, condition_func):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if not condition_func(line):
                # trim start sub string 
                if "共865页" in line:
                    line = line.split("共865页")[1]
                outfile.write(line.replace(" ", "").strip())

def condition(line):
    line = line.strip()
    # 跳过空行
    if not line:
        return True
    # 跳过特定内容
    if line == "《达摩祖师血脉论》体佛法师讲义":
        return True
    # 跳过包含特定字符串的行
    if " 《金刚经》讲记" in line:
        return True
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python onelinetxt.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    filename, ext = os.path.splitext(input_file)
    output_file = f"{filename}.oneline{ext}"
    filter_file(input_file, output_file, condition)

if __name__ == "__main__":
    main()