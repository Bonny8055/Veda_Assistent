# Veda VR integration

## Run the backend

Create a virtual environment, install dependencies, then run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:5000
```

It listens on port `5000`. First verify it in a browser:

```text
http://YOUR_PC_IP:5000/health
```

When the VR headset is a separate device, use the PC's LAN address (for example, `192.168.1.20`) rather than `localhost`. Keep both devices on the same network and allow TCP port 5000 through Windows Firewall.

## API contract

Send a `POST` request to:

```text
http://YOUR_PC_IP:5000/api/v1/command
```

Request:

```json
{ "command": "tell me a joke", "input_type": "voice" }
```

`input_type` is optional: use `voice` or `text`. A successful response has `text`, `action`, `data`, `status`, and `timestamp` fields. For `play <song>`, `action` is `play_video`; for searches it is `web_search`. Use `data` in your VR app to open an in-world panel or media player.

## Unity setup

1. Create an empty GameObject named `VedaBackend` and add this script.
2. Set `serverUrl` to the PC's LAN address. `http://127.0.0.1:5000` works only for a PC-local VR build.
3. Send recognized speech text to `SendVoiceCommand`, display `response.text` in world-space UI, then pass it to your TTS system.
4. For standalone Quest/Android, enable Internet permission. Use HTTPS for production; Android may block local HTTP unless cleartext traffic is explicitly enabled.

```csharp
using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class VedaBackend : MonoBehaviour
{
    [SerializeField] private string serverUrl = "http://192.168.1.20:5000";

    [Serializable] private class CommandRequest
    {
        public string command;
        public string input_type;
    }

    [Serializable] public class VedaResponse
    {
        public string text;
        public string action;
        public string data;
        public string status;
    }

    public void SendVoiceCommand(string speechText)
    {
        StartCoroutine(SendCommand(speechText, "voice"));
    }

    public IEnumerator SendCommand(string command, string inputType)
    {
        var json = JsonUtility.ToJson(new CommandRequest {
            command = command, input_type = inputType
        });
        using var request = new UnityWebRequest(serverUrl + "/api/v1/command", "POST");
        request.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json));
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Veda request failed: " + request.error);
            yield break;
        }

        var response = JsonUtility.FromJson<VedaResponse>(request.downloadHandler.text);
        Debug.Log("Veda: " + response.text);
        // Update world-space UI and invoke your TTS here.
        // Handle response.action == "play_video" or "web_search" using response.data.
    }
}
```

## Troubleshooting

- Works on the PC but not the headset: use the LAN IP, confirm both are on the same network, and open port 5000 in Windows Firewall.
- Connection error: confirm `python manage.py runserver 0.0.0.0:5000` is running and the URL has no trailing slash before `/api`.
- Speech recognition is supplied by Unity or the headset SDK. This backend receives the recognized text and returns the keyword-based response.
