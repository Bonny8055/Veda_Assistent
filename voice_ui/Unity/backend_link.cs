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
    private string lastProcessedCommand = null;
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
                    CommandData commandData = JsonUtility.FromJson<CommandData>(webRequest.downloadHandler.text);
                    string newCommand = commandData.command;

                    // Process the command only if it's new
                    if (newCommand != null && newCommand != lastProcessedCommand)
                    {
                        Debug.Log("Received command: " + newCommand);
                        ProcessCommand(newCommand);
                        lastProcessedCommand = newCommand;
                    }
                }
            }
            // Wait for 1 second before polling again
            yield return new WaitForSeconds(1f);
        }
    }

    void ProcessCommand(string command)
    {
        Debug.Log("ProcessCommand: " + command);

        command = command.ToLower().Trim();

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
            Debug.Log("Moving object");
            transform.Translate(Vector3.forward * moveSpeed * Time.deltaTime);
        }
    }
}