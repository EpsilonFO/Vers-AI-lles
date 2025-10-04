import subprocess
import json

# Lance le MCP server
proc = subprocess.Popen(
    ["python", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Exemple : appeler le tool get_next_passages
request = {
    "tool": "get_next_passages",
    "args": {"stop": "Châtelet", "line": "72", "transport_type": "bus"}
}

# Envoyer la requête
proc.stdin.write(json.dumps(request) + "\n")
proc.stdin.flush()

# Lire la réponse
response = proc.stdout.readline()
try:
    data = json.loads(response)
    print("Response:", data)
except json.JSONDecodeError:
    print("Raw response:", response)

# Terminer le server
proc.terminate()