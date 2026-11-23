import pytest
from fastapi.testclient import TestClient

from app.clearing import Clearing
from app.main import create_app
from app.source.packet import bundle


@pytest.fixture(scope='session')
def dirty():
    return Clearing(bundle('dirty'),b'fixture-2026')


@pytest.fixture(scope='session')
def clean():
    return Clearing(bundle('clean'),b'fixture-2026')


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path/'clearing.sqlite')) as client:
        yield client


@pytest.fixture
def relay():
    # 同一预约先短停再回来卸货：E01 短停 4 分钟，E02 跨午夜回来卸货 25 分钟
    return {'survey':'{"name":"测试配送区","start":"2026-11-30T23:00+08:00","end":"2026-12-01T02:00+08:00","berths":["B-01","B-02"]}',
            'sensors':('event,berth,plate,sensor,start,end\n'
                       'E01,B-01,粤B33333,cam-1,2026-11-30T23:50+08:00,2026-11-30T23:54+08:00\n'
                       'E02,B-01,粤B33333,cam-1,2026-12-01T00:10+08:00,2026-12-01T00:35+08:00\n'),
            'bookings':('reservation,berth,plate,effective,start,end,state\n'
                        'BK-31,B-01,粤B33333,2026-11-30T23:00+08:00,2026-11-30T23:45+08:00,2026-12-01T00:45+08:00,ACTIVE\n'),
            'payments':('receipt,berth,plate,arrival,cents\n'
                        'R01,B-01,粤B33333,2026-11-30T23:50+08:00,0\n')}


@pytest.fixture
def relay_late_record():
    # 迟到的杆侧记录，恰好把短停和回来卸货连成一段
    return 'E03,B-01,粤B33333,cam-2,2026-11-30T23:54+08:00,2026-12-01T00:10+08:00\n'
