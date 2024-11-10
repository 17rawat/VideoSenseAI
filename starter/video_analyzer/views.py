from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import yt_dlp
from django.conf import settings
import assemblyai as aai
import os


aai.settings.api_key = settings.ASSEMBLY_API_KEY


# Create your views here.
@login_required(login_url="/account/login")
def dashboard(request):
    return render(request, "video_analyzer/dashboard.html")


def process_youtube_url(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": str(settings.MEDIA_ROOT / "%(id)s.%(ext)s"),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get("title", None)
        audio_file_path = str(settings.MEDIA_ROOT / f"{info.get('id')}.mp3")

    return audio_file_path, video_title


@csrf_exempt
@login_required(login_url="/account/login")
def analysis(request):
    if request.method == "POST":
        try:
            audio_file_path, video_title = process_youtube_url(
                request.POST.get("video_url")
            )

            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(
                audio_file_path,
                config=aai.TranscriptionConfig(
                    language_detection=True, sentiment_analysis=True
                ),
            )

            # Clean up audio file after transcription
            os.remove(audio_file_path)

            sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            for sentiment in transcript.sentiment_analysis:
                sentiment_counts[sentiment.sentiment] += 1

            return render(
                request,
                "video_analyzer/analysis.html",
                {
                    "video_title": video_title,
                    "transcript": transcript.text,
                    "sentiment_counts": sentiment_counts,
                    "success": True,
                },
            )

        except yt_dlp.utils.DownloadError:
            context = {
                "error": "We couldn't access this video. Please make sure the URL is correct and the video is publicly available.",
                "success": False,
            }
        except aai.error.APIError:
            context = {
                "error": "We're having trouble analyzing this video right now. Please try again in a few minutes.",
                "success": False,
            }
        except Exception as error:
            print(f"Internal error occurred: {str(error)}")
            context = {
                "error": "Something went wrong while processing your video. Please try again or use a different video.",
                "success": False,
            }
        finally:
            if "audio_file_path" in locals() and os.path.exists(audio_file_path):
                os.remove(audio_file_path)

    return render(request, "video_analyzer/analysis.html", context)
