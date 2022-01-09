from stark.service.stark import StarkHandler
class DepartHandler(StarkHandler):
    list_display = [
        'id',
        'title',
    ]