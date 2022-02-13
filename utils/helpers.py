from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice


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


def get_user_totp_device(user, confirmed=None):
    """function to get user confirmed secuirty decive"""
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device
