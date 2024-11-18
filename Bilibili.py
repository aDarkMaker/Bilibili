import os
import subprocess
import tempfile
from datetime import datetime
import chardet

def read_config(config_file):
    config = {}
    with open(config_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):  # 忽略空行和注释行
                key, value = line.split('=', 1)
                config[key] = value
    return config

def convert_cookies_to_netscape(cookies):
    netscape_cookies = "# Netscape HTTP Cookie File\n"
    for cookie in cookies.split('; '):
        name, value = cookie.split('=', 1)
        netscape_cookies += f".bilibili.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n"
    return netscape_cookies

def list_formats(url, cookies):
    # 将 cookies 转换为 Netscape 格式并写入临时文件
    netscape_cookies = convert_cookies_to_netscape(cookies)
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_cookies_file:
        temp_cookies_file.write(netscape_cookies)
        temp_cookies_file_path = temp_cookies_file.name

    # 列出可用的格式
    command = f'yt-dlp --cookies {temp_cookies_file_path} -F "{url}"'
    os.system(command)

    # 删除临时文件
    os.remove(temp_cookies_file_path)

def detect_encoding(data):
    result = chardet.detect(data)
    return result['encoding']

def download_bilibili_video_as_mp4(url, output_path, cookies, format_code):
    # 将 cookies 转换为 Netscape 格式并写入临时文件
    netscape_cookies = convert_cookies_to_netscape(cookies)
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_cookies_file:
        temp_cookies_file.write(netscape_cookies)
        temp_cookies_file_path = temp_cookies_file.name

    # 创建文件夹，以当前日期和时间命名
    folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(output_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # 使用 yt-dlp 下载视频和音频，并保存为单独的文件
    video_command = f'yt-dlp -f {format_code} --cookies {temp_cookies_file_path} -o "{folder_path}/video.%(ext)s" "{url}"'
    audio_command = f'yt-dlp -f bestaudio --cookies {temp_cookies_file_path} -o "{folder_path}/audio.%(ext)s" "{url}"'
    subprocess.run(video_command, shell=True)
    subprocess.run(audio_command, shell=True)

    # 获取下载的视频和音频文件名
    original_video_file_bytes = subprocess.check_output(f'yt-dlp -f {format_code} --cookies {temp_cookies_file_path} --get-filename -o "{folder_path}/%(title)s.%(ext)s" "{url}"', shell=True)
    encoding = detect_encoding(original_video_file_bytes)
    original_video_file = original_video_file_bytes.decode(encoding).strip()
    video_file = os.path.join(folder_path, "video.mp4")
    audio_file = os.path.join(folder_path, "audio.m4a")

    # 删除临时文件
    os.remove(temp_cookies_file_path)

    # 合并视频和音频文件
    merged_file = os.path.join(folder_path, f"{folder_name}_merged.mp4")
    merge_command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c copy "{merged_file}"'
    subprocess.run(merge_command, shell=True)

    # 创建Readme.txt文件
    readme_path = os.path.join(folder_path, "Readme.txt")
    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        readme_file.write(f"视频名称: {os.path.basename(original_video_file)}\n下载仅供自用，转载请注明来处")

if __name__ == "__main__":
    config_file = 'config.txt'  # 配置文件路径
    config = read_config(config_file)
    
    video_url = input("请输入要下载的B站视频URL: ")  # 询问用户输入视频链接
    output_directory = config['output_directory']  # 从配置文件中读取保存路径
    cookies = config['cookies']  # 从配置文件中读取cookies
    
    # 列出可用的格式
    print("可用的格式列表：")
    list_formats(video_url, cookies)
    
    # 询问用户选择的格式代码
    format_code = input("请输入要下载的格式代码: ")
    
    # 下载视频
    download_bilibili_video_as_mp4(video_url, output_directory, cookies, format_code)