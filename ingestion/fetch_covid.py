#!/usr/bin/env python3
import os, json, time
from datetime import datetime, timezone
from urllib import request, parse, error
import boto3

# CONFIGURA AQUÍ (o usa variables de entorno)
BUCKET = os.environ.get('S3_BUCKET', 'my-covid-samuelv01-raw')
RESOURCE_ID = os.environ.get('RESOURCE_ID', 'gt2j-8ykr')
LAST_FETCH_KEY = os.environ.get('LAST_FETCH_KEY', 'state/last_fetch.txt')
S3_PREFIX = os.environ.get('S3_PREFIX', 'raw/minsal/')
SOCRATA_TOKEN = os.environ.get('SOCRATA_TOKEN', 'fxiFGGqaze2IxxzZJ58X6hszV')

BASE_URL = f"https://www.datos.gov.co/resource/{RESOURCE_ID}.json"
s3 = boto3.client('s3')

def read_last_fetch():
    try:
        resp = s3.get_object(Bucket=BUCKET, Key=LAST_FETCH_KEY)
        ts = resp['Body'].read().decode('utf-8').strip()
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime(2000,1,1, tzinfo=timezone.utc)

def write_last_fetch(dt):
    s3.put_object(Bucket=BUCKET, Key=LAST_FETCH_KEY, Body=dt.isoformat())

def http_get_json(url):
    req = request.Request(url)
    if SOCRATA_TOKEN:
        req.add_header("X-App-Token", SOCRATA_TOKEN)
    req.add_header("User-Agent", "Mozilla/5.0 (EC2-fetcher)")
    try:
        with request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except error.HTTPError as e:
        print("HTTPError:", e.code, e.reason, url)
        raise
    except error.URLError as e:
        print("URLError:", e.reason, url)
        raise

def main():
    last_fetch = read_last_fetch()
    date_col = 'fecha_reporte_web'
    last_fetch_str = last_fetch.strftime("%Y-%m-%dT%H:%M:%S")
    where = f"{date_col} > '{last_fetch_str}'"
    limit = 1000
    offset = 0
    all_rows = []

    while True:
        params = {
            '$limit': str(limit),
            '$offset': str(offset),
            '$where': where,
            '$order': f"{date_col} ASC"
        }
        query = parse.urlencode(params, safe="',:")
        url = BASE_URL + "?" + query
        print("Requesting:", url)
        rows = http_get_json(url)
        if not rows:
            break
        all_rows.extend(rows)
        offset += limit
        if offset > 5000000:
            print("Offset limit reached")
            break
        # small sleep to be nice to the API
        time.sleep(0.1)

    if not all_rows:
        print("No new data.")
        return

    now = datetime.now(timezone.utc)
    key = f"{S3_PREFIX}minsal_fetch_{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(all_rows).encode('utf-8'))
    print("Saved to S3:", key)

    # update last fetch using max fecha_reporte_web found
    vals = [r[date_col] for r in all_rows if date_col in r]
    if vals:
        max_ts = max([datetime.fromisoformat(v) for v in vals])
        write_last_fetch(max_ts)
        print("Updated last fetch to:", max_ts.isoformat())

if __name__ == "__main__":
    main()
