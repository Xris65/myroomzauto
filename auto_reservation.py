import requests
from datetime import datetime, timedelta
import os

var_name = "MY_API_KEY"
old_refresh_token = os.getenv(var_name)
token = os.getenv('GH_PAT')
repo = os.getenv('Xris65/myroomzauto') # Format: "pseudo/nom-du-depot"

#specific myroomz
floor_id = os.getenv('FLOOR_ID')
workspace_id = os.getenv('WORKSPACE_ID')

print("floor id : " + str(floor_id))
print("workspace id : " + str(workspace_id))

def update_github_variable(name, value):
    url = f"https://api.github.com/repos/{repo}/actions/variables/{name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"name": name, "value": str(value)}
    
    response = requests.patch(url, json=data, headers=headers)
    
    if response.status_code == 204:
        print(f"✅ Variable {name} mise à jour avec succès !")
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")

def refresh_my_token():
    global old_refresh_token
    url = "https://login.roomz.io/connect/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": old_refresh_token,
        "client_id": "my-roomz",
        "scope": "openid profile email identityServer-api my-roomz-api offline_access"
    }
    response = requests.post(url, data=data)
    print(response.json())
    update_github_variable(var_name, response.json().get("refresh_token"))
    return response.json().get("access_token")

def est_deja_reserve(date, token):
    url = f"https://api.my.roomz.io/floors/{floor_id}/workspaces/calendars?length=100&offset=0"
    payload = {
        "availableWorkspaceOnly": False,
        "date": date,
        "timeSlot": "FullDay",
        "tagIds": []
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://my.roomz.io",
        "Referer": "https://my.roomz.io/"
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json().get("data", [])
            for ws in data:
                if ws.get("workspaceId") == workspace_id:
                    status = ws.get("status")
                    return status != "Available"
            return False
        else:
            print(f"❌ Erreur {response.status_code} : {response.text}")
            return False
    except Exception as e:
        print(f"🔥 Crash : {e}")
        return False
    
def verifier_et_reserver_prochains_jours():
    token = refresh_my_token()
    jours_sur_site = [0, 2, 3] # Lundi, Mercredi, Jeudi
    
    for i in range(1, 14):
        date_cible = datetime.now() + timedelta(days=i)
        if date_cible.weekday() in jours_sur_site:
            date_str = date_cible.strftime("%Y-%m-%d")
            
            print(f"--- 📅 Analyse du {date_str} ---")
            
            if est_deja_reserve(date_str, token):
                print(f"✅ Déjà réservé (ou occupé) pour le {date_str}. Skip.")
            else:
                print(f"🆓 Libre ! Tentative de réservation...")
                reserver_avec_token(date_str, token)

def reserver_avec_token(date, token):
    url = "https://api.my.roomz.io/bookings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "roomz-source-type": "1", 
        "x-roomz-source-type": "1",
        "Origin": "https://my.roomz.io",
        "Referer": "https://my.roomz.io/"
    }
    payload = {
        "workspaceId": workspace_id,
        "localDate": date,
        "timeSlot": "FullDay",
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"✅ Succès pour le {date} !")
        elif response.status_code == 409: # Exemple si déjà réservé
            print(f"⚠️ Déjà réservé ou conflit pour le {date}.")
        else:
            print(f"❌ Erreur {response.status_code} pour le {date} : {response.text}")
    except Exception as e:
        print(f"🔥 Erreur script : {e}")

verifier_et_reserver_prochains_jours()