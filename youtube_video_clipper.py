import subprocess
import json
import os
import sys
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import tempfile
import shutil


class YouTubeClipper:
    def __init__(self):
        self.temp_dir = None
        self.downloads_dir = Path("downloads")
        self.downloads_dir.mkdir(exist_ok=True)
    
    def time_to_seconds(self, time_str: str) -> float:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:  # hh:mm:ss
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:  # mm:ss
                return int(parts[0]) * 60 + float(parts[1])
        else:
            return float(time_str)
    
    def seconds_to_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def get_video_info(self, url: str) -> Dict:
        print("🔍 Fetching video information...")
        
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-warnings',
            '--no-check-certificates',
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error fetching video info: {e.stderr}")
            sys.exit(1)
        except json.JSONDecodeError:
            print("❌ Error parsing video information")
            sys.exit(1)
    
    def get_available_formats(self, video_info: Dict) -> List[Dict]:
        MAX_PIXELS = 3840 * 2160
        
        formats = video_info.get('formats', [])
        
        video_formats = []
        for f in formats:
            if (f.get('vcodec') != 'none' and 
                f.get('height') and f.get('width') and
                (f.get('width', 0) * f.get('height', 0) <= MAX_PIXELS) and
                f.get('ext') in ['mp4', 'webm', 'mkv']):
                
                fps_text = f"@{f.get('fps', '')}fps" if f.get('fps', 0) > 30 else ""
                label = f"{f.get('height')}p{fps_text}"
                
                estimated_size = None
                if f.get('filesize'):
                    estimated_size = f.get('filesize')
                elif f.get('tbr') and video_info.get('duration'):
                    estimated_size = (f.get('tbr') * video_info.get('duration') * 1024) // 8
                
                video_formats.append({
                    'format_id': f.get('format_id'),
                    'label': label,
                    'height': f.get('height'),
                    'width': f.get('width'),
                    'fps': f.get('fps', 0),
                    'has_audio': f.get('acodec') != 'none',
                    'ext': f.get('ext'),
                    'filesize': estimated_size,
                    'tbr': f.get('tbr', 0),  
                    'vcodec': f.get('vcodec', ''),
                    'acodec': f.get('acodec', ''),
                    'quality': f.get('quality', 0)
                })
        
        video_formats.sort(key=lambda x: (x['height'], x['fps']), reverse=True)
        
        unique_formats = []
        seen_resolutions = set()
        
        for fmt in video_formats:
            res_key = (fmt['height'], fmt['fps'])
            if res_key not in seen_resolutions:
                seen_resolutions.add(res_key)
                if not fmt['has_audio']:
                    fmt['format_id'] = f"{fmt['format_id']}+bestaudio"
                unique_formats.append(fmt)
        
        return unique_formats
    
    def display_formats(self, formats: List[Dict], video_info: Dict) -> None:
        """Display available formats with detailed information"""
        duration = video_info.get('duration', 0)
        
        print("\n📺 Available video qualities:")
        print("-" * 90)
        print(f"{'#':<3} {'Quality':<12} {'Codec':<15} {'Audio':<8} {'Bitrate':<10} {'Full Video Size':<15}")
        print("-" * 90)
        
        for i, fmt in enumerate(formats, 1):
            if fmt['filesize']:
                size_mb = fmt['filesize'] / (1024 * 1024)
                if size_mb > 1024:
                    size_str = f"{size_mb / 1024:.1f} GB"
                else:
                    size_str = f"{size_mb:.0f} MB"
            elif fmt['tbr'] and duration:
                estimated_mb = (fmt['tbr'] * duration) / 8 / 1024
                if estimated_mb > 1024:
                    size_str = f"~{estimated_mb / 1024:.1f} GB"
                else:
                    size_str = f"~{estimated_mb:.0f} MB"
            else:
                size_str = "Unknown"
            
            audio_status = "✓" if fmt['has_audio'] or '+bestaudio' in fmt['format_id'] else "✗"
            codec = fmt['vcodec'][:12] + "..." if len(fmt['vcodec']) > 12 else fmt['vcodec']
            bitrate = f"{fmt['tbr']:.0f}k" if fmt['tbr'] else "Unknown"
            
            print(f"{i:<3} {fmt['label']:<12} {codec:<15} {audio_status:<8} {bitrate:<10} {size_str:<15}")
        
        print("-" * 90)
        print("💡 Sizes shown are for the complete video. Your clip will be proportionally smaller.")
    
    def get_thumbnail_url(self, video_info: Dict) -> Optional[str]:
        thumbnails = video_info.get('thumbnails', [])
        if thumbnails:
            # Get the highest quality thumbnail
            best_thumbnail = max(thumbnails, key=lambda x: x.get('width', 0) * x.get('height', 0))
            return best_thumbnail.get('url')
        return None
    
    def download_video_section(self, url: str, format_id: str, start_time: str, 
                             end_time: str, output_path: str) -> bool:
        print(f"⬇️  Downloading video section ({start_time} - {end_time})...")
        
        section = f"*{start_time}-{end_time}"
        
        cmd = [
            'yt-dlp',
            url,
            '-f', format_id,
            '--download-sections', section,
            '-o', output_path,
            '--merge-output-format', 'mp4',
            '--no-check-certificates',
            '--no-warnings',
            '--add-header', 'referer:youtube.com',
            '--add-header', 'user-agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error downloading video: {e.stderr}")
            return False
    
    def optimize_video(self, input_path: str, output_path: str, selected_format: Dict) -> bool:
        print("🔄 Optimizing video for high quality...")
        
        crf_value = "18" if selected_format['height'] >= 1080 else "20" 
        preset = "slow"  
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:a', '192k',  
            '-movflags', '+faststart',
            '-preset', preset,
            '-crf', crf_value,
            '-pix_fmt', 'yuv420p',  
            output_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error optimizing video: {e.stderr}")
            return False
    
    def validate_time_format(self, time_str: str) -> bool:
        time_pattern = r'^\d{1,2}:\d{2}(:\d{2}(\.\d+)?)?$'
        if re.match(time_pattern, time_str):
            return True
        
        try:
            float(time_str)
            return True
        except ValueError:
            return False
    
    def get_user_input(self) -> Tuple[str, str, str, int]:
        print("🎬 YouTube Video Clipper")
        print("=" * 50)
        
        while True:
            url = input("\n📺 Enter YouTube URL: ").strip()
            if url and ('youtube.com' in url or 'youtu.be' in url):
                break
            print("❌ Please enter a valid YouTube URL")
        
        video_info = self.get_video_info(url)
        formats = self.get_available_formats(video_info)
        
        if not formats:
            print("❌ No suitable video formats found")
            sys.exit(1)
        
        title = video_info.get('title', 'Unknown Title')
        duration = video_info.get('duration', 0)
        thumbnail_url = self.get_thumbnail_url(video_info)
        uploader = video_info.get('uploader', 'Unknown')
        view_count = video_info.get('view_count', 0)
        
        print(f"\n🎥 Video: {title}")
        print(f"👤 Channel: {uploader}")
        print(f"⏱️  Duration: {self.seconds_to_time(duration)}")
        print(f"👁️  Views: {view_count:,}" if view_count else "👁️  Views: Unknown")
        if thumbnail_url:
            print(f"🖼️  Thumbnail: {thumbnail_url}")
        
        total_size_mb = 0
        if video_info.get('filesize'):
            total_size_mb = video_info.get('filesize') / (1024 * 1024)
        
        self.display_formats(formats, video_info)
        
        while True:
            try:
                choice = int(input(f"\n📝 Select quality (1-{len(formats)}): "))
                if 1 <= choice <= len(formats):
                    selected_format = formats[choice - 1]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(formats)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        while True:
            start_time = input("\n⏰ Enter start time (hh:mm:ss or seconds): ").strip()
            if self.validate_time_format(start_time):
                if self.time_to_seconds(start_time) < duration:
                    break
                else:
                    print(f"❌ Start time cannot exceed video duration ({self.seconds_to_time(duration)})")
            else:
                print("❌ Invalid time format. Use hh:mm:ss, mm:ss, or seconds")
        
        while True:
            end_time = input("⏰ Enter end time (hh:mm:ss or seconds): ").strip()
            if self.validate_time_format(end_time):
                end_seconds = self.time_to_seconds(end_time)
                start_seconds = self.time_to_seconds(start_time)
                if end_seconds > start_seconds and end_seconds <= duration:
                    break
                elif end_seconds <= start_seconds:
                    print("❌ End time must be after start time")
                else:
                    print(f"❌ End time cannot exceed video duration ({self.seconds_to_time(duration)})")
            else:
                print("❌ Invalid time format. Use hh:mm:ss, mm:ss, or seconds")
        
        return url, start_time, end_time, choice - 1, video_info, formats
    
    def create_clip(self, url: str, start_time: str, end_time: str, format_index: int,
                   video_info: Dict, formats: List[Dict], output_filename: str = None) -> bool:
        
        selected_format = formats[format_index]
        title = video_info.get('title', 'video').replace('/', '_').replace('\\', '_')
        
        if not output_filename:
            safe_title = re.sub(r'[^\w\-_\. ]', '', title)[:50]
            output_filename = f"{safe_title}_{start_time.replace(':', '-')}_to_{end_time.replace(':', '-')}.mp4"
        
        output_path = self.downloads_dir / output_filename
        
        self.temp_dir = tempfile.mkdtemp()
        temp_video_path = os.path.join(self.temp_dir, "temp_video.mp4")
        
        try:
            print(f"\n🎯 Selected quality: {selected_format['label']}")
            print(f"📁 Output file: {output_path}")
            
            success = self.download_video_section(
                url, selected_format['format_id'], 
                start_time, end_time, temp_video_path
            )
            
            if not success:
                return False
            
            if not os.path.exists(temp_video_path):
                print("❌ Downloaded file not found")
                return False
            
            success = self.optimize_video(temp_video_path, str(output_path), selected_format)
            
            if success:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Clip created successfully!")
                print(f"📁 File: {output_path}")
                print(f"📊 Size: {file_size:.1f} MB")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
        finally:
            # Cleanup temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def run(self):
        try:
            url, start_time, end_time, format_index, video_info, formats = self.get_user_input()
            
            success = self.create_clip(url, start_time, end_time, format_index, 
                                     video_info, formats)
            
            if success:
                print("\n🎉 All done! Enjoy your clip!")
                print("💝 Thank you for using YouTube Clipper by Mohit Khairnar!")
            else:
                print("\n❌ Failed to create clip")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)


def main():
    clipper = YouTubeClipper()
    clipper.run()

if __name__ == "__main__":
    main()