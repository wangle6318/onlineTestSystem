from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class MyPaginator:

    def __init__(self, queryset, request, count):
        self.queryset = queryset
        self.request = request
        self.count = count

    def paginator(self):
        paginator = Paginator(self.queryset, self.count)
        page = self.request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        if page:
            current = int(page)
        else:
            current = 1
        max_page = paginator.num_pages
        if max_page < 7:
            pages = range(1, max_page + 1)
        else:
            if current < 4:
                pages = range(1, 8)
            elif max_page - current < 4:
                pages = range(max_page - 6, max_page + 1)
            else:
                pages = range(current - 3, current + 4)

        context = {"query": contacts, "pages": pages}
        return context