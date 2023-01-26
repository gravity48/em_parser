class Paginator:

    def __init__(self, obj_list: list, limit: int):
        self._obj_list = obj_list
        self.limit = limit

    @property
    def pages_count(self):
        if len(self._obj_list) % self.limit:
            return int(len(self._obj_list) / self.limit) + 1
        else:
            return int(len(self._obj_list) / self.limit)

    def get_items(self, page_id: int):
        assert self.pages_count >= page_id, 'page_id lte then pages count'
        offset = page_id * self.limit
        return self._obj_list[offset: offset + self.limit]

    def page_exist(self, page_id):
        return 0 <= page_id < self.pages_count
