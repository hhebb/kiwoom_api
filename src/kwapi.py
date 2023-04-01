
'''
로그인 api
'''

def comm_connect(ocx):
    '''
    kiwoom api 로그인
    '''
    
    ocx.dynamicCall("CommConnect()")


'''
tr api
'''

def set_input_value(ocx, fid, val):
    '''
    tr 요청 값 지정
    comm rt data 전에 호출해야함 
    '''

    ocx.dynamicCall('SetInputValue(QString, int)', fid, val)


def comm_rq_data(ocx, rqname, trcode, next, screen):
    '''
    tr 요청 수행
    set input value 를 먼저 호출해야함
    '''

    ocx.dynamicCall('CommRqData(QString, QString, int, QString)', rqname, trcode, next, screen)


def get_comm_data(ocx, trcode, rqname, index, item):
    '''
    tr 응답 받아오는 함수
    콜백 핸들러 안에서 호출
    '''

    data = ocx.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, index, item)
    return data.strip()


def get_comm_data_ex(ocx, trcode, rqname):
    '''
    tr 응답 받아오는 함수
    콜백 핸들러 안에서 호출
    전체 데이터
    '''

    data = ocx.dynamicCall("GetCommDataEx(QString, QString)", trcode, rqname)
    return data.strip()


'''
실시간 api
'''

def set_real_reg(ocx, screen_no, code_list, fid_list, real_type):
    '''
    실시간 구독
    '''
    ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                         screen_no, code_list, fid_list, real_type)


def disconnect_real_data(ocx, screen_no):
    '''
    실시간 구독 해지
    '''
    ocx.dynamicCall("DisConnectRealData(QString)", screen_no)


def get_comm_real_data(ocx, code, fid):
    '''
    실시간 응답 받는 함수
    '''
    data = ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
    return data


'''
검색식 api
'''

def get_condition_load(ocx):
    '''
    검색식 로드
    '''
    ocx.dynamicCall("GetConditionLoad()")


def get_condition_name_list(ocx):
    '''
    검색식 이름
    '''
    data = ocx.dynamicCall("GetConditionNameList()")
    conditions = data.split(";")[:-1]
    cond_dict = dict()
    for condition in conditions:
        index, name = condition.split('^')
        cond_dict[index] = name
    
    return cond_dict


def send_condition(ocx, screen, cond_name, cond_index, search):
    '''
    검색식 실시간 감시 요청
    '''
    ret = ocx.dynamicCall("SendCondition(QString, QString, int, int)", screen, cond_name, cond_index, search)


def send_condition_stop(ocx, screen, cond_name, cond_index):
    '''
    검색식 감시 해제
    '''
    ret = ocx.dynamicCall("SendConditionStop(QString, QString, int)", screen, cond_name, cond_index)