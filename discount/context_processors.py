from kulik.settings import DEBUG
def debug(request):
    return {'debug': DEBUG}
