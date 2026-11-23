from app.web import STEPS


def test_each_page_returns_rendered_evidence(client):
    home=client.get('/')
    assert home.status_code==200 and '泊位占位阶段流' in home.text
    for slug,label in STEPS.items():
        response=client.get('/clearing/'+slug)
        assert response.status_code==200 and f'<h1>{label}</h1>' in response.text


def test_sealed_flow_links_to_evidence(client):
    key=client.post('/api/dockets',json={'sample':'dirty'}).json()['key']
    result=client.get('/clearing/appeal',params={'key':key})
    assert f'href="/api/export/{key}"' in result.text
    assert '泊位分钟勾稽差额 <b>0</b>' in result.text


def test_sample_error_has_recovery_code(client):
    r=client.get('/api/cases/not-found/intake')
    assert (r.status_code,r.json()['code'])==(404,'SAMPLE_BAD')


def test_billing_pages_explain_allowance_and_adjustments(client,relay,relay_late_record):
    first=client.post('/api/dockets',json={'bundle':relay}).json()
    merged=relay | {'sensors':relay['sensors']+relay_late_record}
    second=client.post('/api/dockets',json={'bundle':merged}).json()
    pricing=client.get('/clearing/pricing',params={'key':second['key']})
    assert '首免' in pricing.text and '共享 10 分钟额度' in pricing.text
    assert '已出账' in pricing.text and '迟到杆侧记录并入' in pricing.text
    settlement=client.get('/clearing/settlement',params={'key':second['key']})
    assert '批次调整' in settlement.text and '调整净额' in settlement.text
    earlier=client.get('/clearing/pricing',params={'key':first['key']})
    assert '新停靠出账' in earlier.text
