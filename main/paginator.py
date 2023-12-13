from django.core.paginator import Paginator
from django.utils.functional import cached_property


class BigQueryPaginator(Paginator):

    @cached_property
    def count(self):
        return 9_999_999_999
