#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube视频下载器 - 支持下载视频并嵌入中文字幕
"""

import os
import sys
import subprocess
from pathlib import Path
import translators as ts
import pysrt
import chardet
import time

def is_subtitle_empty(file_path):
    """检查SRT字幕文件是否只包含时间码而没有文本"""
    try:
        # 使用 chardet 检测文件编码
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'

        subs = pysrt.open(file_path, encoding=encoding)
        if not subs:
            return True # 文件为空或无法解析
        
        for sub in subs:
            if sub.text and sub.text.strip():
                return False # 找到任何非空文本行
        return True # 所有行都没有文本
    except Exception as e:
        print(f"⚠️ 检查字幕文件 '{file_path}' 时出错: {e}")
        return False # 出错时，假定它不是空的以避免错误翻译

def translate_subtitle(source_path, target_path, to_lang='zh-CN'):
    """翻译SRT字幕文件"""
    print(f"\n🔄 开始翻译字幕: 从 {source_path.name} 到 {target_path.name}")
    
    try:
        # 检测源文件编码
        with open(source_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            source_encoding = result['encoding'] or 'utf-8'

        source_subs = pysrt.open(source_path, encoding=source_encoding)
        
        # 限制QPS为1，避免请求过于频繁
        for i, sub in enumerate(source_subs):
            original_text = sub.text
            
            if not original_text or not original_text.strip():
                sub.text = ""
                continue

            translated_text = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 使用 atexit 钩子来处理可能的连接错误
                    translated_text = ts.translate_text(original_text, translator='google', to_language=to_lang)
                    if translated_text:
                        sub.text = translated_text
                        break  # 成功，跳出重试循环
                except Exception as e:
                    print(f"\n⚠️  翻译 '{original_text}' 时第 {attempt + 1} 次失败: {e}")
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** (attempt + 1)  # 指数退避
                        print(f"    将在 {sleep_time} 秒后重试...")
                        time.sleep(sleep_time)
                    else:
                        print(f"❌ 翻译失败，已达最大重试次数。将保留原文。")
                        sub.text = original_text  # 保留原文
            
            progress = (i + 1) / len(source_subs) * 100
            print(f"\r翻译进度: {progress:.1f}% ({i+1}/{len(source_subs)})", end="")
            time.sleep(1) # 简单的延迟

        # 保存为UTF-8编码
        source_subs.save(target_path, encoding='utf-8')
        print("\n✅ 字幕翻译完成！")

    except Exception as e:
        print(f"\n❌ 翻译字幕时发生错误: {e}")
        import traceback
        traceback.print_exc()

def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    # 确保所有 yt-dlp impersonate 功能的依赖都已安装
    required_packages = [
        'yt-dlp', 
        'brotli', 
        'certifi', 
        'pycryptodome', 
        'websockets',
        'requests',
        'urllib3'
    ]
    
    print("正在检查和更新依赖包，这可能需要一些时间...")
    
    try:
        # 使用 --no-cache-dir 确保获取最新信息
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", *required_packages],
        )
        print("✅ 所有依赖均已更新至最新版本。")
    except subprocess.CalledProcessError as e:
        print("❌ 依赖安装或更新失败，请检查pip是否配置正确以及网络连接。")
        print(f"错误详情: {e}")
        raise

def get_impersonate_target():
    """检查可用的impersonate target"""
    try:
        # 使用 yt-dlp 检查可用的 target
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--list-impersonate-targets"],
            capture_output=True, text=True, check=True
        )
        if 'chrome' in result.stdout.lower():
            # 优先使用 chrome110 或其他 chrome 版本
            for line in result.stdout.splitlines():
                if 'chrome110' in line:
                    return 'chrome110'
                if 'chrome' in line:
                    return line.split()[0] # 返回第一个找到的chrome版本
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果命令失败或yt-dlp未安装，则无法使用impersonate
        return None
    return None

def download_video_with_subtitle(url, output_path=None, merge_subtitles=True, translate_enabled=False):
    """
    下载YouTube视频并嵌入中文字幕
    
    参数:
        url: YouTube视频URL
        output_path: 输出路径（可选）
        merge_subtitles: 是否合并字幕（可选）
        translate_enabled: 是否启用翻译（可选）
    """
    import yt_dlp
    
    # 设置输出目录
    if output_path is None:
        output_path = Path.cwd() / "downloads"
    else:
        output_path = Path(output_path)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    cookie_file = Path.cwd() / "youtube_cookies.txt"
    
    # 根据是否合并字幕来配置后期处理器
    postprocessors = [
        {'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'},
        {'key': 'FFmpegMetadata', 'add_metadata': True},
    ]

    if merge_subtitles:
        print("\nℹ️ 将下载并嵌入字幕。")
        # 将FFmpegEmbedSubtitle插入到正确的位置
        postprocessors.insert(1, {'key': 'FFmpegEmbedSubtitle', 'already_have_subtitle': False})
    else:
        print("\nℹ️ 将只下载字幕文件，不进行嵌入。")

    # 配置下载选项
    ydl_opts = {
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-Hans', 'zh-Hant', 'zh', 'en'],
        'subtitlesformat': 'srt',
        'subtitles_retry': 3,
        'postprocessors': postprocessors,
        'cookiefile': str(cookie_file) if cookie_file.exists() else None,
        'retries': 10,
        'fragment_retries': 10,
        'retry_sleep': 'linear',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False, # Show all errors, especially from post-processing
        'progress_hooks': [progress_hook],
    }

    # 动态设置 impersonate
    impersonate_target = get_impersonate_target()
    if impersonate_target:
        print(f"✅ 检测到可用的浏览器模拟目标: {impersonate_target}")
        ydl_opts['impersonate'] = impersonate_target
    else:
        print("⚠️ 未能配置浏览器模拟功能。如果下载失败，请检查依赖安装过程中的错误信息。")

    print(f"\n开始下载视频: {url}")
    print(f"输出目录: {output_path.absolute()}\n")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            
            print(f"视频标题: {video_title}")
            print(f"视频时长: {info.get('duration', 0) // 60}分{info.get('duration', 0) % 60}秒")
            
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            available_langs = set(subtitles.keys()) | set(automatic_captions.keys())
            chinese_subs = [lang for lang in ['zh-Hans', 'zh-Hant', 'zh'] if lang in available_langs]
            
            if chinese_subs:
                print(f"找到中文字幕: {', '.join(chinese_subs)}")
            elif 'en' in available_langs:
                print("警告: 未找到中文字幕，将尝试下载英文字幕")
            else:
                print("警告: 未找到任何中/英文字幕")

            # 准备文件名以供后续使用
            base_filepath_str = ydl.prepare_filename(info).rsplit('.', 1)[0]

            print("\n开始下载...")
            ydl.download([url])
            
            print(f"\n✅ 下载完成！")

            # 检查并翻译字幕
            if translate_enabled:
                zh_hans_path = Path(f"{base_filepath_str}.zh-Hans.srt")
                en_path = Path(f"{base_filepath_str}.en.srt")

                if zh_hans_path.exists() and is_subtitle_empty(zh_hans_path):
                    print(f"ℹ️ 检测到空的简体中文字幕: {zh_hans_path.name}")
                    if en_path.exists() and not is_subtitle_empty(en_path):
                        print(f"✅ 找到可用的英文字幕: {en_path.name}")
                        translate_subtitle(en_path, zh_hans_path, to_lang='zh-CN')
                    else:
                        print("⚠️ 未找到可用于翻译的非空英文字幕。")
                elif not zh_hans_path.exists() and en_path.exists() and not is_subtitle_empty(en_path):
                    print(f"ℹ️ 未找到中文字幕，但找到可用的英文字幕: {en_path.name}")
                    translate_subtitle(en_path, zh_hans_path, to_lang='zh-CN')

            print(f"📁 文件保存在: {output_path.absolute()}")
            
            try:
                # Corrected subprocess call
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, text=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("\n⚠️ 注意：FFmpeg未安装或未在PATH中。字幕可能无法嵌入视频。")
                print("   请访问 https://ffmpeg.org/download.html 进行安装。")
            
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ 下载失败: {str(e)}")
        if "HTTP Error 429" in str(e):
            print("\n提示：遇到 'Too Many Requests' 错误。这可能是因为YouTube限制了下载频率。")
            print("   你可以尝试等待一段时间，或使用cookies文件。")
        return False
    except Exception as e:
        print(f"\n❌ 发生未知错误: {str(e)}")
        return False
    
    return True

def progress_hook(d):
    """下载进度回调"""
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        
        if total > 0:
            percent = (downloaded / total) * 100
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            
            speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "N/A"
            eta_str = f"{int(eta // 60)}m {int(eta % 60)}s" if eta else "N/A"

            print(f"\r下载进度: {percent:.1f}% | 速度: {speed_str} | 预计剩余时间: {eta_str}   ", end='')
    elif d['status'] == 'finished':
        if d.get('postprocessor') == 'Merger':
             print(f"\n下载完成，正在合并文件...")
        elif d.get('postprocessor') == 'EmbedSubtitle':
             print(f"\n正在嵌入字幕...")
        else:
             print(f"\n下载完成，正在处理: {d.get('postprocessor') or '...'} ")
    elif d['status'] == 'error':
        print(f"\n下载时发生错误: {d.get('error')}")

def main():
    """主函数"""
    print("=" * 60)
    print("YouTube视频下载器 - 支持中文字幕")
    print("=" * 60)
    
    try:
        check_and_install_dependencies()
    except Exception:
        input("\n依赖安装失败，请检查网络和Python环境后重试。按Enter键退出...")
        return
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"\n检测到命令行传入的URL: {url}")
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        # 命令行暂不支持选择，默认为是合并，否翻译
        download_video_with_subtitle(url, output_path, merge_subtitles=True, translate_enabled=False)
        return

    while True:
        url = input("\n请输入YouTube视频URL (或输入 't' 仅翻译, 'q' 退出): ").strip()
        
        if url.lower() == 'q':
            print("感谢使用，再见！")
            break

        if url.lower() == 't':
            print("\n--- 仅翻译字幕文件 ---")
            
            # 提示用户输入基础文件名
            base_filename_prompt = "请输入字幕文件的基础名称 (例如 'Kubernetes Tutorial for Beginners [FULL COURSE in 4 Hours]')\n"
            base_filename = input(base_filename_prompt).strip()

            if not base_filename:
                print("❌ 文件名不能为空。")
                continue

            # 构建默认路径
            downloads_dir = Path.cwd() / "downloads"
            en_path = downloads_dir / f"{base_filename}.en.srt"
            zh_hans_path = downloads_dir / f"{base_filename}.zh-Hans.srt"

            print(f"ℹ️ 将尝试使用以下文件路径:")
            print(f"    源文件 (英文): {en_path}")
            print(f"    目标文件 (简体中文): {zh_hans_path}")

            if not en_path.exists():
                print(f"\n❌ 错误: 源英文字幕文件不存在。")
                print(f"   请确认文件 '{en_path}' 是否存在于 'downloads' 文件夹中。")
                continue

            # 检查目标文件是否为空，如果为空则从头翻译
            if zh_hans_path.exists() and is_subtitle_empty(zh_hans_path):
                print(f"ℹ️ 检测到空的简体中文字幕文件，将从头开始翻译。")
            
            translate_subtitle(en_path, zh_hans_path, to_lang='zh-CN')
            print(f"\n📁 文件保存在: {zh_hans_path.absolute()}")
            continue
        
        if not url:
            print("URL不能为空，请重新输入")
            continue
        
        if 'youtube.com' not in url and 'youtu.be' not in url:
            print("请输入有效的YouTube URL")
            continue
        
        custom_path = input("输入下载路径 (直接回车使用默认'downloads'文件夹): ").strip()
        
        merge_choice = input("是否需要合并字幕到视频中？ (y/n, 默认是): ").strip().lower()
        merge_subtitles = merge_choice != 'n'

        translate_choice = input("当缺少中文或中文字幕为空时，是否尝试翻译英文字幕？ (y/n, 默认否): ").strip().lower()
        translate_enabled = translate_choice == 'y'

        output_path = custom_path if custom_path else None
        success = download_video_with_subtitle(url, output_path, merge_subtitles, translate_enabled)
        
        if success:
            choice = input("\n是否继续下载其他视频？(y/n): ").strip().lower()
            if choice != 'y':
                print("感谢使用，再见！")
                break
        else:
            print("\n请检查URL是否正确，或稍后重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序意外终止: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
