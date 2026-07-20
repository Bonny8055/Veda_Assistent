import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .services import veda


def index(request):
    """Renders the main web interface."""
    return render(request, "index.html")

@require_GET
def health(request):
    return JsonResponse({"status": "Veda is running smoothly", "version": "3.0-django", "api": {"command": "/api/v1/command", "method": "POST"}})


@csrf_exempt
@require_POST
def command(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be valid JSON.", "status": "error"}, status=400)
    command_text = payload.get("command") or payload.get("text") or ""
    if not isinstance(command_text, str) or not command_text.strip():
        return JsonResponse({"error": "No command provided.", "status": "error"}, status=400)
    input_type = payload.get("input_type", "voice")
    return JsonResponse(veda.process_command(command_text, input_type if input_type in ("voice", "text") else "voice"))
