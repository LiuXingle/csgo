"""
MP3 转 WAV 转换工具
使用方法：python convert_mp3_to_wav.py
"""

import os

def convert_with_pydub():
    """使用 pydub 库转换（推荐）"""
    try:
        from pydub import AudioSegment
        
        # 转换 reload.mp3 到 reload.wav
        if os.path.exists('assets/reload.mp3'):
            print("正在转换 reload.mp3...")
            audio = AudioSegment.from_mp3('assets/reload.mp3')
            audio.export('assets/reload.wav', format='wav')
            print("✓ 转换成功: assets/reload.wav")
            
            # 显示音频信息
            duration = len(audio) / 1000.0  # 毫秒转秒
            print(f"  时长: {duration:.2f} 秒")
            print(f"  采样率: {audio.frame_rate} Hz")
            print(f"  声道: {audio.channels}")
        else:
            print("✗ 找不到 assets/reload.mp3")
            
    except ImportError:
        print("✗ 未安装 pydub 库")
        print("请运行: pip install pydub")
        print("如果转换 MP3，还需要安装 ffmpeg")
        return False
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return False
    
    return True

def convert_with_ffmpeg():
    """使用 ffmpeg 命令行工具转换"""
    import subprocess
    
    if os.path.exists('assets/reload.mp3'):
        print("正在使用 ffmpeg 转换 reload.mp3...")
        try:
            subprocess.run([
                'ffmpeg', '-i', 'assets/reload.mp3',
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ar', '44100',  # 44.1kHz 采样率
                'assets/reload.wav'
            ], check=True)
            print("✓ 转换成功: assets/reload.wav")
            return True
        except FileNotFoundError:
            print("✗ 未安装 ffmpeg")
            print("请从 https://ffmpeg.org/download.html 下载安装")
            return False
        except Exception as e:
            print(f"✗ 转换失败: {e}")
            return False
    else:
        print("✗ 找不到 assets/reload.mp3")
        return False

def main():
    print("=" * 50)
    print("MP3 转 WAV 转换工具")
    print("=" * 50)
    print()
    
    # 检查 assets 文件夹
    if not os.path.exists('assets'):
        print("✗ 找不到 assets 文件夹")
        print("请确保在项目根目录运行此脚本")
        return
    
    # 方法1: 尝试使用 pydub
    print("方法1: 使用 pydub 库")
    if convert_with_pydub():
        print("\n转换完成！现在可以运行游戏了。")
        return
    
    print()
    
    # 方法2: 尝试使用 ffmpeg
    print("方法2: 使用 ffmpeg 命令行")
    if convert_with_ffmpeg():
        print("\n转换完成！现在可以运行游戏了。")
        return
    
    print()
    print("=" * 50)
    print("所有转换方法都失败了")
    print("=" * 50)
    print()
    print("手动转换方法：")
    print("1. 使用在线工具: https://cloudconvert.com/mp3-to-wav")
    print("2. 使用 Audacity 软件:")
    print("   - 打开 reload.mp3")
    print("   - 文件 -> 导出 -> 导出为 WAV")
    print("   - 保存为 assets/reload.wav")
    print()

if __name__ == '__main__':
    main()
