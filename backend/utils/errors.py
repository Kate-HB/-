from flask import request, jsonify


def success_response(data=None, message='操作成功', page=None, total=None):
    resp = {'success': True, 'data': data, 'message': message}
    if page is not None:
        resp['page'] = page
    if total is not None:
        resp['total'] = total
    return resp


def error_response(message, status_code=400, error_code=None):
    resp = {'success': False, 'message': message}
    if error_code:
        resp['error_code'] = error_code
    return resp, status_code


def get_json():
    """Get JSON body, returning error if Content-Type is wrong or body is empty."""
    if not request.is_json:
        return None, error_response('请求体必须为JSON格式', 400, 'INVALID_JSON')
    data = request.get_json(silent=True)
    if data is None:
        return None, error_response('请求体为空或格式错误', 400, 'INVALID_JSON')
    return data, None


def require_fields(data, *fields):
    """Check that all required fields exist and are non-empty. Returns first missing field name or None."""
    for field in fields:
        val = data.get(field)
        if val is None or val == '':
            return field
    return None
