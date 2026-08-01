import re
import os
import sys
import shutil
from pathlib import Path

def remove_zhihu_zhida_links(file_path: str, backup: bool = True) -> None:
    """
    移文本文件中的除知乎直答链接

    :param file_path: 要处理的文件路径
    :param backup: 是否创建原始文件备份,默认为True
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    if backup:
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        print(f"已创建备份: {backup_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        for enc in ['gbk', 'gb-2312', 'gb-18030']:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                print(f"检测到非UTF-8编码，切换为 {enc} 解码")
                break
            except:
                continue
        else:
            raise ValueError("无法识别文件编码，请确保文件是文本格式")
    
    pattern = r'\[((?!\[).+?)\]\([^)]*zhida\.zhihu\.com[^)]*\)'
    clean_content, count = re.subn(pattern, r'\1', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print(f"处理完成！共移除 {count} 个知乎直答链接")
    print(f"修改已保存至: {os.path.abspath(file_path)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("错误：缺少文件路径参数")
        print("用法: python remove_zhida.py <文件路径> [--no-backup]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    create_backup = "--no-backup" not in sys.argv
    
    try:
        remove_zhihu_zhida_links(file_path, backup=create_backup)
    except Exception as e:
        print(f"\n处理失败: {str(e)}")
        sys.exit(1)
