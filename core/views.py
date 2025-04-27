from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from pytube import YouTube
import os
from django.conf import settings
from urllib.error import HTTPError

def home(request):
    if request.method == "POST":
        url = request.POST.get('url')
        
        if not url:
            return HttpResponse("No URL provided", status=400)
        
        try:
            # Create downloads directory if it doesn't exist
            output_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
            os.makedirs(output_path, exist_ok=True)
            
            # Initialize YouTube with OAuth (helps with age-restricted videos)
            yt = YouTube(
                url,
                use_oauth=True,       # Enable OAuth
                allow_oauth_cache=True  # Cache OAuth tokens
            )
            
            # Get the highest resolution stream
            stream = yt.streams.get_highest_resolution()
            filename = stream.default_filename
            
            # Download the video
            video_file = stream.download(output_path=output_path)
            
            # Send the file as a response
            response = FileResponse(
                open(video_file, 'rb'),
                as_attachment=True,
                filename=filename
            )
            
            return response
            
        except HTTPError as e:
            return HttpResponse(f"HTTP Error: {e.code} - {e.reason}", status=400)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return render(request, 'core/home.html', {})