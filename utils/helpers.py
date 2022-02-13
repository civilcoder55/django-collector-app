from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate(objects, page, objects_per_page):
    """function take Model Objects, page_number,
    elements per page and return paginator object"""
    paginator = Paginator(objects, objects_per_page)
    try:
        paginated_objects = paginator.page(page)
    except PageNotAnInteger:
        paginated_objects = paginator.page(1)
    except EmptyPage:
        paginated_objects = paginator.page(paginator.num_pages)

    return paginated_objects
