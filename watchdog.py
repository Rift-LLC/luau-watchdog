# Everything in here is self-explanatory.

import requests
import time
import os

# Config
webhookUrl = "" # Place your webhook here
apiUrl = "https://api.github.com/repos/luau-lang/luau/releases/latest" # Target endpoint for latest luau build
versionFile = "version.txt" # This exist to avoid sending the same version more than once

def getStoredVersion():
    if os.path.exists(versionFile):
        with open(versionFile, "r") as f:
            return f.read().strip()
    return None

def storeVersion(ver):
    with open(versionFile, "w") as f:
        f.write(ver)

def fetchLatestLuau():
    try:
        res = requests.get(apiUrl)
        if res.status_code == 200:
            data = res.json()
            return {
                "ver": data["tag_name"],
                "body": data["body"],
                "zipUrl": data["zipball_url"] 
            }
    except:
        pass
    return None

def sendNotify(release):
    # Cap under 4000 to stay under Discord's limit
    fullChangelog = release["body"]
    if len(fullChangelog) > 4000:
        fullChangelog = fullChangelog[:4000] + "\n\n(Truncated due to Discord length limits...)"

    payload = {
        "content": "A new luau version has released!",
        "embeds": [{
            "title": f"luau-ver: {release['ver']}",
            "description": f"**Changelogs:**\n```\n{fullChangelog}\n```",
            "color": 0x2f3136,
            "fields": [
                {
                    "name": "Download",
                    "value": f"[Download {release['ver']}.zip]({release['zipUrl']})",
                    "inline": False
                }
            ]
        }]
    }
    requests.post(webhookUrl, json=payload)

def startMonitor():
    lastVer = getStoredVersion()

    while True:
        release = fetchLatestLuau()
        
        if release and release["ver"] != lastVer:
            sendNotify(release)
            
            lastVer = release["ver"]
            storeVersion(lastVer)
        
        time.sleep(1800)

if __name__ == "__main__":
    startMonitor()