import requests
import sys
from datetime import datetime, timedelta
import os

old_refresh_token = os.getenv('MY_API_KEY')
old_refresh_token = "" #TODO

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
    update_script_variable(response.json().get("refresh_token"))
    return response.json().get("access_token")


def update_script_variable(new_value):
    path = sys.argv[0]
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith('old_refresh_token ='):
                f.write(f'old_refresh_token = "{new_value}"\n')
            else:
                f.write(line)



def est_deja_reserve(date, token):
    # L'URL reste la même, mais on change la méthode
    floor_id = "" # TODO: changer
    url = f"https://api.my.roomz.io/floors/{floor_id}/workspaces/calendars?length=100&offset=0"
    # Le payload exact que tu m'as montré
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
            mon_bureau_id = "" # TODO
            for ws in data:
                if ws.get("workspaceId") == mon_bureau_id:
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
        "workspaceId": "", #TODO
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