import os

class Collector:
    '''
    데이터 수집하는 수집기 객체
    어떤 거래소에서든 돌아가는 게 목표임
    '''
    def __init__(self):
        self.tmp = None
        self.exchange = None
        self.save_path = ''

    def set_preference(self, preference):
        '''
        어떤 데이터를 어떻게 수집할 건지 정의, 설정하는 함수
        목표 데이터 정보에 대한 메타 정보 포함
        '''
        self.preference = preference
        self.save_path = ''

    def set_exchange(self, exchange):
        '''
        특정 거래소를 지정하고 준비시킴
        수집 직전의 상태로 변경됨
        '''
        self.exchange = exchange
        self.exchange.set_preference(self.preference)

    def execute(self):
        '''
        정의된 데이터를 지정된 거래소에서 수집하는 것을 실행
        거래소에서 조회한 데이터를 받아 로컬에 저장하는 단계
        '''

        data_generator = self.exchange.get_data() # generator

        for data in data_generator:
            self.__save(data)

    def execute_update(self):
        pass

    def execute_flush(self):
        pass

    def __save(self, data):
        '''
        거래소에서 받아온 데이터를 직접 저장하는 메서드
        일관된 형식으로 받아서 일관된 형태로 저장하기 때문에 거래소 모듈에서 forming 해야함
        '''
        self.data_queue
        path = os.path.join(self.prefernce.market_type,
                            self.prefernce.data_type,
                            self.prefernce.period,
                            self.prefernce.items,
                            self.prefernce.range
                            )

        with open(f'{path}.csv', 'w') as f:
            f.write(data)


class Runner:
    def __init__(self):
        pass


class Preference:
    '''
    사용자가 수집하려는 데이터 형식
    '''
    def __init__(self):
        self.market_type = 'stock'
        self.data_type = 'candle'
        self.period = '1m'
        self.items = list()
        self.range = ['20220103', '20220107']
        # self.~