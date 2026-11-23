from app.curb.timeaxis import minute
from app.setup import POLICY


def predecessor(docket,hashes,key):
    for manifest in docket.manifests():
        if manifest['key']!=key and manifest['rule']==POLICY and manifest['inputs'].get('survey')==hashes['survey']:
            packet=docket.find(manifest['key'])
            if packet:
                return manifest['key'],packet['evidence']['pricing']['stays']
    return None,[]


def _at(value):
    return minute(value) if isinstance(value,str) else value


def reconcile(previous,current):
    lines=[]
    claimed=set()
    for stay in sorted(current,key=lambda r:(_at(r['start']),r['berth'],r['vehicle'])):
        start,end=_at(stay['start']),_at(stay['end'])
        overlap=[old for old in previous if old['berth']==stay['berth'] and old['vehicle']==stay['vehicle']
                 and _at(old['start'])<end and start<_at(old['end'])]
        fresh=[old for old in overlap if old['stay'] not in claimed]
        claimed.update(old['stay'] for old in fresh)
        billed=sum(old['due_cents'] for old in fresh)
        if not overlap:
            code='NEW_STOP'
        elif len(overlap)>len(fresh):
            code='SPLIT'
        elif len(fresh)>1:
            code='MERGED'
        else:
            old=fresh[0]
            same_span=_at(old['start'])==start and _at(old['end'])==end
            if same_span:
                code='UNCHANGED' if stay['due_cents']==billed else 'REPRICED'
            else:
                covers=_at(old['start'])>=start and _at(old['end'])<=end
                code='EXTENDED' if covers else 'SPAN_CHANGED'
        lines.append({'stay':stay['stay'],'berth':stay['berth'],'vehicle':stay['vehicle'],
                      'arrival':start.isoformat(),'free_minutes':stay.get('free_minutes',0),
                      'due_cents':stay['due_cents'],'billed_cents':billed,
                      'adjustment_cents':stay['due_cents']-billed,'code':code,
                      'sources':[old['stay'] for old in overlap]})
    for old in previous:
        if old['stay'] not in claimed:
            lines.append({'stay':old['stay'],'berth':old['berth'],'vehicle':old['vehicle'],
                          'arrival':_at(old['start']).isoformat(),'free_minutes':old.get('free_minutes',0),
                          'due_cents':0,'billed_cents':old['due_cents'],
                          'adjustment_cents':-old['due_cents'],'code':'VOIDED','sources':[old['stay']]})
    lines.sort(key=lambda r:(r['arrival'],r['berth'],r['stay']))
    return lines


def adjustments(docket,hashes,key,stays):
    origin,previous=predecessor(docket,hashes,key)
    lines=reconcile(previous,stays)
    return {'predecessor':origin,'lines':lines,'total_cents':sum(row['adjustment_cents'] for row in lines)}
