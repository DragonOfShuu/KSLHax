class PaginationHelper:
    def __init__(self, collection, items_per_page):
        self.collection = list(self._break_list(collection, items_per_page))
        if len(self.collection) == 0:
            self.collection.append([])
        self.ipp = items_per_page

    def _break_list(self, items, ipp):
        for i in range(0, len(items), ipp): yield items[i:i + ipp]
        
    # returns the number of items within the entire collection
    def item_count(self):
        if len(self.collection) == 0: return 0
        return (len(self.collection[:-1])*self.ipp)+len(self.collection[-1])

    # returns the number of pages
    def page_count(self): return len(self.collection)

    # returns the number of items on the current page. page_index is zero based
    # this method should return -1 for page_index values that are out of range
    def page_item_count(self, page_index):
        try:
            return len(self.collection[page_index])
        except IndexError:
            return -1

    # determines what page an item is on. Zero based indexes.
    # this method should return -1 for item_index values that are out of range
    def page_index(self, item_index):
        if (item_index < 0) or (item_index > (self.item_count()-1)): return -1
        return item_index // self.ipp