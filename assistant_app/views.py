from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from .assistant import process_command

# A simple in-memory store for the last command
last_command = {"command": None}


def home_view(request):
    """Render the dashboard and process commands submitted from it."""
    if request.method == 'GET':
        return render(request, 'assistant_app/index.html')

    if request.method == 'POST':
        command = request.POST.get('command', '')
        response = process_command(command)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'response': response})
        return render(request, 'assistant_app/index.html', {
            'command': command,
            'response': response,
        })

    return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def command_view(request):
    if request.method == 'POST':
        try:
            # Handle JSON from main.py
            data = json.loads(request.body)
            last_command['command'] = data.get('command')
            return JsonResponse({'status': 'ok', 'command': last_command['command']})
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
            # Handle form data from Unity to clear the command
            command = request.POST.get('command', None)
            last_command['command'] = command
            return JsonResponse({'status': 'ok', 'command': last_command['command']})
    if request.method == 'GET':
        # --- DEBUG: Log when Unity connects to get a command ---
        print(f"DEBUG: Unity client connected. Sending command: {last_command}")
        return JsonResponse(last_command)

    return HttpResponseNotAllowed(['GET', 'POST'])
