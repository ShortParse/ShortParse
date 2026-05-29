# shortparse/server/bnet_client.py
import os
import time
import json
import requests
from pathlib import Path

TOKEN_URL = "https://oauth.battle.net/token"
API_BASE_URL = "https://us.api.blizzard.com"
NAMESPACE = "static-us"
LOCALE = "en_US"

class BlizzardClient:
    def __init__(self):
        # Load credentials from settings or environment
        from shortparse.settings import GEMINI_API_KEY
        # Check standard env vars loaded by shortparse settings
        self.client_id = os.getenv("BLIZZARD_CLIENT_ID")
        self.client_secret = os.getenv("BLIZZARD_CLIENT_SECRET")
        
        self.token = None
        self.token_expires_at = 0
        
        # Determine offline mode
        self.is_offline = not self.client_id or not self.client_secret
        
        # Initialize Cache Directory and File under shortparse data folder
        local_dir = Path(__file__).resolve().parent.parent
        self.cache_dir = local_dir / "data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "bnet_spells.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def get_token(self) -> str | None:
        if self.is_offline:
            return None
            
        if self.token and time.time() < self.token_expires_at:
            return self.token
            
        try:
            response = requests.post(
                TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            
            self.token = payload["access_token"]
            self.token_expires_at = time.time() + int(payload.get("expires_in", 86400)) - 60
            return self.token
        except Exception:
            self.is_offline = True
            return None

    def get_spell_info(self, spell_id: int) -> dict | None:
        spell_key = str(spell_id)
        
        # 1. Check persistent cache
        if spell_key in self.cache:
            cached_data = self.cache[spell_key]
            if cached_data.get("tombstone"):
                return None
            return cached_data
            
        # 2. Return None if in offline mode
        if self.is_offline:
            return None
            
        token = self.get_token()
        if not token:
            return None
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Battlenet-Namespace": NAMESPACE
        }
        
        try:
            # Query spell metadata
            spell_url = f"{API_BASE_URL}/data/wow/spell/{spell_id}"
            params = {"locale": LOCALE}
            
            response = requests.get(spell_url, headers=headers, params=params, timeout=8)
            
            if response.status_code == 404:
                self.cache[spell_key] = {"tombstone": True}
                self._save_cache()
                return None
                
            response.raise_for_status()
            payload = response.json()
            
            name_val = payload.get("name", "")
            if isinstance(name_val, dict):
                name = name_val.get(LOCALE, name_val.get("en_US", ""))
            else:
                name = str(name_val)
                
            desc_val = payload.get("description", "")
            if isinstance(desc_val, dict):
                description = desc_val.get(LOCALE, desc_val.get("en_US", ""))
            else:
                description = str(desc_val)
            
            # Resolve Icon/Media URL
            icon_url = None
            media_info = payload.get("media", {})
            media_href = media_info.get("key", {}).get("href")
            
            if media_href:
                try:
                    media_response = requests.get(media_href, headers=headers, timeout=8)
                    if media_response.status_code == 200:
                        media_payload = media_response.json()
                        assets = media_payload.get("assets", [])
                        for asset in assets:
                            if asset.get("key") == "icon":
                                icon_url = asset.get("value")
                                break
                        if not icon_url and assets:
                            icon_url = assets[0].get("value")
                except Exception:
                    pass
            
            result = {
                "name": name,
                "description": description,
                "icon_url": icon_url
            }
            
            self.cache[spell_key] = result
            self._save_cache()
            
            return result
            
        except Exception:
            return None
