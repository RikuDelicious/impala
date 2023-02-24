def add_x_real_ip(get_response):
    """
    開発環境用のミドルウェア。
    リバースプロキシから付与されるX-Real-Ipヘッダを疑似的に再現する。
    元のリクエストにrequest.META["HTTP_X_REAL_IP"]が存在していなければ、
    request.META["REMOTE_ADDR"]の値をセットする。
    """

    def middleware(request):
        if "HTTP_X_REAL_IP" not in request.META:
            request.META["HTTP_X_REAL_IP"] = request.META["REMOTE_ADDR"]
        response = get_response(request)
        return response

    return middleware
