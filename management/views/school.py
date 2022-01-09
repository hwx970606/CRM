from stark.service.stark import StarkHandler

class SchoolHandler(StarkHandler):
    list_display = [
        'id',
        'title',
    ]
    has_add_btn = True