def post(client,files):
    return client.post('/api/dockets',json={'bundle':files}).json()


def evidence(client,key):
    return client.get('/api/dockets/'+key).json()['evidence']


def test_first_archive_bills_every_stop_as_new(client,relay):
    result=post(client,relay)
    assert result['adjustment_cents']==460
    adjustments=evidence(client,result['key'])['adjustments']
    assert adjustments['predecessor'] is None
    assert [row['code'] for row in adjustments['lines']]==['NEW_STOP','NEW_STOP']
    assert [row['billed_cents'] for row in adjustments['lines']]==[0,0]


def test_late_record_merges_stops_and_posts_delta(client,relay,relay_late_record):
    first=post(client,relay)
    merged=relay | {'sensors':relay['sensors']+relay_late_record}
    second=post(client,merged)
    assert second['key']!=first['key'] and second['adjustment_cents']==640
    doc=evidence(client,second['key'])
    stay,=doc['pricing']['stays']
    assert (stay['free_minutes'],stay['due_cents'])==(10,1100)
    adjustments=doc['adjustments']
    assert adjustments['predecessor']==first['key']
    line,=adjustments['lines']
    assert (line['code'],line['billed_cents'],line['due_cents'],line['adjustment_cents'])==('MERGED',460,1100,640)
    assert len(line['sources'])==2 and line['free_minutes']==10


def test_rerun_never_double_spends_allowance(client,relay):
    a,b=post(client,relay),post(client,relay)
    assert (b['reused'],a['key']==b['key'],a['adjustment_cents']==b['adjustment_cents'])==(True,True,True)
    doc=evidence(client,a['key'])
    assert doc['settlement']['totals']['free']==10
    assert doc['pricing']['due_cents']==460
    assert doc['adjustments']['total_cents']==460


def test_repriced_batch_with_unchanged_stays_posts_zero(client,relay):
    post(client,relay)
    again=post(client,relay | {'payments':relay['payments']+'\r\n'})
    assert again['adjustment_cents']==0
    adjustments=evidence(client,again['key'])['adjustments']
    assert [row['code'] for row in adjustments['lines']]==['UNCHANGED','UNCHANGED']


def test_removed_record_voids_original_bill(client,relay,relay_late_record):
    post(client,relay | {'sensors':relay['sensors']+relay_late_record})
    moved=relay | {'sensors':('event,berth,plate,sensor,start,end\n'
                              'E09,B-02,粤B44444,cam-1,2026-12-01T01:00+08:00,2026-12-01T01:05+08:00\n')}
    result=post(client,moved)
    adjustments=evidence(client,result['key'])['adjustments']
    lines={row['code']:row for row in adjustments['lines']}
    assert lines['VOIDED']['adjustment_cents']==-1100
    assert lines['NEW_STOP']['due_cents']==100
    assert adjustments['total_cents']==-1000
