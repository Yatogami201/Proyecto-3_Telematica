import os
import json
import boto3
import requests
from datetime import datetime, timezone

S3 = boto3.client("s3")

BUCKET = os.environ["S3_BUCKET"]
S3_PREFIX = os.environ.get("S3_PREFIX", "raw/minsal/")
RESOURCE_ID = os.environ.get("RESOURCE_ID", "gt2j-8ykr")
SOCRATA_APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN")

BASE_URL = f"https://www.datos.gov.co/resource/{RESOURCE_ID}.json"

def fetch_with_pagination():
    headers = {}
    if SOCRATA_APP_TOKEN and SOCRATA_APP_TOKEN.strip():
        headers["X-App-Token"] = SOCRATA_APP_TOKEN

    all_data = []
    limit = 50000
    offset = 0
    
    print("🚀 Iniciando descarga paginada...")
    
    while True:
        url = f"{BASE_URL}?$limit={limit}&$offset={offset}"
        print(f"📥 Página {offset//limit + 1}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
                
            all_data.extend(data)
            print(f"✅ Recibidas {len(data)} filas (Total: {len(all_data):,})")
            
            if len(data) < limit:
                break
                
            offset += limit
            
        except Exception as e:
            print(f"❌ Error en página {offset//limit + 1}: {e}")
            break

    return all_data

def lambda_handler(event=None, context=None):
    print("=== DESCARGA PAGINADA Socrata ===")
    
    data = fetch_with_pagination()
    
    if not data:
        return {"status": "ERROR", "error": "No se pudieron descargar datos"}
    
    # Guardar en S3
    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y%m%dT%H%M%SZ')
    key = f"{S3_PREFIX}minsal_paginated_{timestamp}.json"
    
    print(f"💾 Guardando {len(data):,} filas en S3...")
    
    S3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(data, ensure_ascii=False).encode("utf-8")
    )
    
    print(f"✅ ÉXITO: s3://{BUCKET}/{key}")
    
    return {
        "status": "OK", 
        "rows": len(data),
        "s3_key": key
    }

if __name__ == "__main__":
    result = lambda_handler()
    print(json.dumps(result, indent=2))
