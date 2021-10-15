import requests
import datetime as dt
import json

def get_pincode_slots(pincode):
    
    # give cowin url here for pincodes
    url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin'

    headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'cdn-api.co-vin.in' ,
            'Pragma': 'no-cache',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
            }
    dt_format = "%d-%m-%Y"
    dt_now = dt.datetime.now()
    dt_now_IST = (dt_now + dt.timedelta(hours=5, minutes=30)).strftime(dt_format)

    params = {
            'pincode': pincode,
            'date': dt_now_IST
            }

    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code != 200:
        return False, {}, {}

    data = json.loads(resp.text)
    slots18, dateobj18, cids18 = [], [], []
    slots45, dateobj45, cids45 = [], [], []

    for center in data['centers']:
        cid = center['center_id']
        for session in center['sessions']:
            if session['min_age_limit'] == 18:
                cids18.append(cid)
                slots18.append(session['available_capacity'])
                dtobj = dt.datetime.strptime(session['date'], dt_format).date()
                dateobj18.append(dtobj)

            else:
                cids45.append(cid)
                slots45.append(session['available_capacity'])
                dtobj = dt.datetime.strptime(session['date'], dt_format).date()
                dateobj45.append(dtobj)
    
    if slots18:
        total_slots18 = sum(slots18)
        daysobj = max(dateobj18) - min(dateobj18)
        days18 = daysobj.days
        center18 = len(set(cids18))
    else:
        total_slots18, days18, center18 = 0,0,0

    if slots45:
        total_slots45 = total_slots18 + sum(slots45)
        daysobj = max(dateobj45) - min(dateobj45)
        days45 = max(days18, daysobj.days)
        center45 = center18 +  len(set(cids45))
    else:
        total_slots45, days45, center45 = 0,0,0

    plus_18 = {
            'slots': total_slots18,
            'days': days18,
            'center': center18
            }
    plus_45 = {
            'slots': total_slots45,
            'days': days45,
            'center': center45
            }
    
    return True, plus_18, plus_45
