using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

[System.Serializable]
public class CommandData
{
    public string command;
}

public class backend_link : MonoBehaviour
{
    public float moveSpeed = 5f;
    private bool isMoving = false;
    private string backendUrl = "http://localhost:8000/command/";

    void Start()
    {
        // Start polling the backend for commands
        StartCoroutine(PollForCommand());
    }

    IEnumerator PollForCommand()
    {
        while (true)
        {
            using (UnityWebRequest webRequest = UnityWebRequest.Get(backendUrl))
            {
                yield return webRequest.SendWebRequest();

                if (webRequest.result == UnityWebRequest.Result.Success)
                {
                    // --- DEBUG: Log the raw response from the server to confirm connection ---
                    Debug.Log("DEBUG: Successfully connected to Django. Raw response: " + webRequest.downloadHandler.text);

                    CommandData commandData = JsonUtility.FromJson<CommandData>(webRequest.downloadHandler.text);
                    // Sanitize the command as soon as it's received.
                    string newCommand = commandData.command?.ToLower().Trim();
                    
                    // Process the command only if it's not null or empty
                    if (!string.IsNullOrEmpty(newCommand))
                    {
                        Debug.Log("Received command: " + newCommand);
                        ProcessCommand(newCommand);
                        StartCoroutine(ClearCommandOnServer());
                    }
                }
            }
            // Wait for 1 second before polling again
            yield return new WaitForSeconds(1f);
        }
    }
    
    IEnumerator ClearCommandOnServer()
    {
        // Use a form to send the data, which is a common way for POST requests.
        WWWForm form = new WWWForm();
        form.AddField("command", ""); // Send an empty command to clear it

        using (UnityWebRequest webRequest = UnityWebRequest.Post(backendUrl, form))
        {
            // We need to set the content type for JSON, but since we are clearing, we can just post an empty command.
            // A more RESTful way would be a DELETE request, but POST works fine here.
            yield return webRequest.SendWebRequest();
            // We don't need to check the result, just fire and forget.
        }
    }

    void ProcessCommand(string command)
    {
        if (command == "go" || command == "move")
        {
            isMoving = true;
            Debug.Log("Moving");
        }
        else if (command == "stop")
        {
            isMoving = false;
            Debug.Log("Stopped");
        }
    }

    void Update()
    {
        if (isMoving)
        {
            // --- DEBUG: Confirm that the script is trying to move the object ---
            Debug.Log("Update: isMoving is true. Attempting to move cube.");

            // This will now execute when isMoving is true
            transform.Translate(Vector3.forward * moveSpeed * Time.deltaTime);
        }
    }
}