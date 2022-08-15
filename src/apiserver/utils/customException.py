from rest_framework.views import exception_handler
from rest_framework.exceptions import  ValidationError, ErrorDetail
from rest_framework.exceptions import AuthenticationFailed
from django.http import Http404
from rest_framework.response import Response
from rest_framework import  status

"""
    에러 Response 형태 관리
    {
        "status": "error",
        "error_code": "validation_error"
        "detail": "토큰이 유효하지 않습니다."
    }
"""
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if type(response.data) == list:
            response.data = response.data[0]
        if isinstance(response.data, ErrorDetail):
            response.data = {'status': 'error', 'detail': response.data}
        
        if type(exc) == ValidationError:
            if not response.data.get('error_code', None):
                response.data['error_code'] = 'validation_error'
            if not response.data.get('detail', None) and exc.detail:
                try:
                    new_res_data = response.data.copy()
                    data = {}
                    for k in exc.detail.keys():
                        if k in [ 'status', 'error_code']:
                            continue
                        data[k] = exc.detail[k][0] if isinstance(exc.detail[k], dict) else exc.detail[k].__str__()
                        del(new_res_data[k])
                    new_res_data['detail'] = data
                    response.data = new_res_data
                except Exception as err:
                    print(err)
                    pass

        else:
            try:
                response.data['error_code'] = exc.get_codes()
            except AttributeError:
                response.data['error_code'] = 'not_found'
                response.data['status'] = 'error'
                if response.status_code == 403:
                    response.data['error_code'] = 'forbidden'
            except AuthenticationFailed:
                response.data['status'] = 'error'
        
    elif 'does not exist' in exc.__str__():
        raise Http404()

    if isinstance(exc, TypeError):
        return Response({'detail': exc.__str__(), 'error_code': 'validation_error', 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if response.data.get('status', 'success') == 'success':
            response.data['status'] = 'error'
    except Exception as err:
        print(f'err {err}')
    
    return response
    

