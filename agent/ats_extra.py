"""Conectores a tableros públicos Ashby y SmartRecruiters de empresas aprobadas."""
from __future__ import annotations
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .geo import fold

def fetch_public(url, opener=urlopen):
    if not (url.startswith('https://api.ashbyhq.com/posting-api/job-board/') or
            url.startswith('https://api.smartrecruiters.com/v1/companies/')):
        raise ValueError('API de origen no permitida')
    request = Request(url, headers={'Accept':'application/json','User-Agent':'TotalChanbaIndexer/1.0'})
    with opener(request, timeout=18) as response:
        if response.status != 200 or 'json' not in response.headers.get('Content-Type','').lower():
            raise ValueError('Respuesta no JSON o fuente no disponible')
        return json.loads(response.read(3_000_000))

def nicaragua_location(value):
    if isinstance(value, dict):
        country = str(value.get('country') or value.get('countryCode') or '')
        if fold(country) in ('ni', 'nicaragua'):
            return ', '.join(x for x in [str(value.get('city') or '').strip(), 'Nicaragua'] if x)
        value = ' '.join(str(value.get(k) or '') for k in ('city','region','country'))
    txt = str(value or '').strip()
    return txt if 'nicaragua' in fold(txt) else ''

def parse_ashby(payload, source):
    if not isinstance(payload,dict):
        raise ValueError('Formato Ashby desconocido')
    rows=[]
    for item in payload.get('jobs', []) if isinstance(payload.get('jobs'),list) else []:
        if not isinstance(item,dict) or item.get('isListed') is False: continue
        locs=[item.get('location','')]
        for entry in item.get('secondaryLocations') or []:
            if isinstance(entry,dict):
                locs.extend([entry.get('location',''),entry.get('address',{})])
        local=next((v for v in (nicaragua_location(x) for x in locs) if v),'')
        if not local: continue
        compensation=item.get('compensation') or {}
        if not isinstance(compensation,dict): compensation={}
        pay=compensation.get('compensationTierSummary') or compensation.get('scrapeableCompensationSalarySummary') or ''
        workplace=str(item.get('workplaceType') or '').lower()
        mode={'remote':'Remoto','hybrid':'Híbrido','onsite':'Presencial'}.get(workplace,'Remoto' if item.get('isRemote') is True else '')
        rows.append({'url':item.get('jobUrl'),'title':item.get('title'),
                     'company':source['company'],'location':local,
                     'summary':item.get('descriptionPlain') or item.get('descriptionHtml') or '',
                     'salary':pay,'type':item.get('employmentType') or '',
                     'published_at':item.get('publishedAt'),'modality':mode})
    return rows

def smart_location(item):
    return nicaragua_location(item.get('location',{})) if isinstance(item,dict) else ''

def parse_smart(item,detail,source):
    if not isinstance(detail,dict): return None
    location=smart_location(detail) or smart_location(item)
    if not location: return None
    link=detail.get('postingUrl') or detail.get('applyUrl')
    if not link: return None
    sections=(detail.get('jobAd') or {}).get('sections') or {}
    if not isinstance(sections,dict): sections={}
    def section(key):
        value=sections.get(key) or {}
        return value.get('text','') if isinstance(value,dict) else ''
    commitment=detail.get('typeOfEmployment') or {}
    return {'url':link,'title':detail.get('name') or item.get('name'),
            'company':source['company'],'location':location,
            'summary':section('jobDescription') or section('companyDescription'),
            'requirements':section('qualifications'),
            'benefits':section('additionalInformation'),
            'published_at':detail.get('releasedDate') or item.get('releasedDate'),
            'type':commitment.get('label','') if isinstance(commitment,dict) else '',
            'modality':''}

def collect_extra(source,now,normalise,fetcher=fetch_public):
    from .quality import valid_and_recent
    token=source['board']
    if source['provider']=='ashby':
        url=f'https://api.ashbyhq.com/posting-api/job-board/{token}?' + urlencode({'includeCompensation':'true'})
        parsed=parse_ashby(fetcher(url),source)
    elif source['provider']=='smartrecruiters':
        parsed=[]
        for page in range(2):
            url=f'https://api.smartrecruiters.com/v1/companies/{token}/postings?' + urlencode({'country':'ni','limit':100,'offset':page*100})
            response=fetcher(url)
            if not isinstance(response,dict): raise ValueError('Formato SmartRecruiters desconocido')
            postings=response.get('content') or []
            if not isinstance(postings,list): raise ValueError('Formato SmartRecruiters desconocido')
            for entry in postings:
                if not smart_location(entry): continue
                ident=str(entry.get('id') or '')
                if not re.fullmatch(r'[a-zA-Z0-9-]{4,80}',ident): continue
                detail=fetcher(f'https://api.smartrecruiters.com/v1/companies/{token}/postings/{ident}')
                item=parse_smart(entry,detail,source)
                if item: parsed.append(item)
                if len(parsed)>=40: break
            if len(parsed)>=40 or len(postings)<100: break
    else:
        raise ValueError('Proveedor desconocido')
    jobs=[normalise(item,source,now) for item in parsed[:100]]
    return [item for item in jobs if item and valid_and_recent(item,now)]
