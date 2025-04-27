from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from pytube import YouTube
import os
from django.conf import settings
from urllib.error import HTTPError
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def home(request):
    if request.method == "POST":
        url = request.POST.get('url', '').strip()
        
        if not url:
            return render(request, 'core/home.html', {
                'error': 'Please enter a YouTube URL'
            }, status=400)
        
        if 'youtube.com' not in url and 'youtu.be' not in url:
            return render(request, 'core/home.html', {
                'error': 'Please enter a valid YouTube URL'
            }, status=400)
        
        try:
            # Ensure downloads directory exists
            output_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
            os.makedirs(output_path, exist_ok=True)
            logger.info(f"Download directory: {output_path}")
            
            # Initialize YouTube with OAuth
            yt = YouTube(
                url,
                use_oauth=True,
                allow_oauth_cache=True
            )
            logger.info(f"Video title: {yt.title}")
            
            # Get the highest resolution progressive stream
            stream = yt.streams.filter(
                progressive=True,
                file_extension='mp4'
            ).order_by('resolution').desc().first()
            
            if not stream:
                return render(request, 'core/home.html', {
                    'error': 'No downloadable stream found for this video'
                }, status=400)
            
            filename = f"{yt.title}.mp4"
            safe_filename = "".join(
                c for c in filename if c.isalnum() or c in (' ', '.', '_')
            ).rstrip()
            
            # Download the video
            logger.info(f"Starting download: {safe_filename}")
            video_path = stream.download(
                output_path=output_path,
                filename=safe_filename
            )
            logger.info(f"Download complete: {video_path}")
            
            # Create file response
            response = FileResponse(
                open(video_path, 'rb'),
                as_attachment=True,
                filename=safe_filename
            )
            response['Content-Type'] = 'video/mp4'
            response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
            
            return response
            
        except HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            return render(request, 'core/home.html', {
                'error': f"YouTube error: {e.reason}"
            }, status=400)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return render(request, 'core/home.html', {
                'error': f"An error occurred: {str(e)}"
            }, status=500)
    
    return render(request, 'core/home.html', {})