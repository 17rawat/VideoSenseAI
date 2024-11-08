from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


# Create your views here.
@csrf_exempt
@login_required(login_url="/account/login")
def analyze_video(request):
    return render(request, "video_analyzer/analysis.html")
