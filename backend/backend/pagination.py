from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    自定义分页类，支持通过URL参数设置每页数据量
    
    默认每页50条数据，最大每页100条（强制限制，防止一次性拉取全量导致超时）
    """
    # 默认每页数据量
    page_size = 50
    # 最大每页数据量
    max_page_size = 100
    # 分页参数名
    page_query_param = 'page'
    # 每页数据量参数名
    page_size_query_param = 'page_size'
