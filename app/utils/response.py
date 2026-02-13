from flask import jsonify


def success_response(data='', message=''):
    """成功响应
    Args:
        data: 响应数据，默认为空字符串
        message: 响应消息，默认为空字符串
    Returns:
        tuple: (json_response, 200)
    """
    return jsonify({
        'message': message,
        'code': 0,
        'data': data
    }), 200


def fail_response(message=''):
    """失败响应
    Args:
        message: 响应消息，默认为空字符串
    Returns:
        tuple: (json_response, 200)
    """
    return jsonify({
        'message': message,
        'code': -1,
        'data': ''
    }), 200


def error_response(code, message):
    """错误响应
    Args:
        code: 错误码
        message: 错误消息
    Returns:
        tuple: (json_response, code)
    """
    return jsonify({
        'message': message,
        'code': code,
        'data': ''
    }), code


def page_response(page=1, per_page=10, total=0, pages=0, items=[]):
    """分页响应
    Args:
        page: 当前页码，默认为1
        per_page: 每页数量，默认为10
        total: 总记录数，默认为0
        pages: 总页数，默认为0
    Returns:
        tuple: (json_response, 200)
    """

    data = {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages
    }
    return jsonify({
        'code': 0,
        'msg': 'success',
        'data': data
    }), 200
