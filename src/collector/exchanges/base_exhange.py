class Exchange:
    '''
    base 거래소 모듈
    거래소 API 에 직접적으로 접근하고 데이터 조회 요청을 담당
    주로 collector 에 의해 제어됨
    하지만 거래소 API 테스트를 위해서 자체적으로 구동될 수 있음
    '''
    def __init__(self):
        self.name = ''

    def connect(self):
        '''
        해당 API 에 연결을 수립하는 메서드
        '''
        pass

    def set_preference(self, preference):
        '''
        조회 요청에 대한 특정 조건을 받아 설정
        주로 collector 의 의도를 그대로 받아들임
        '''

    def get_data(self):
        '''
        실제로 데이터를 요청하고 반환하는 부분
        '''

        data = None
        return data