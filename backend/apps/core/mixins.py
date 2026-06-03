class PageSizeMixin:
    """Adds support for a `page_size` GET parameter to control pagination."""

    page_size_param = "page_size"
    max_page_size = 100
    default_page_size = None

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get(self.page_size_param)
        if page_size and page_size.isdigit():
            return min(int(page_size), self.max_page_size)
        return self.default_page_size or self.paginate_by
