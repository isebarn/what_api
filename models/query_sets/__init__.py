from mongoengine import QuerySet


class ProductQuerySet(QuerySet):
    def default(self, cls, filters):
        products = cls.fetch(filters)

        return products

    # mongodb full-text search into product.name and product.description
    def search(self, cls, filter):
        # if filter['filter'] is empty, return all products
        if not filter['filter']:
            return self.default(cls, {})
        
        # mongodb query that partially matches product.name and product.description
        return list(cls.objects().aggregate([
            { "$match": {
                "$or": [
                    { "name": { "$regex": filter['filter'], "$options": "i" } },
                    { "description": { "$regex": filter['filter'], "$options": "i" } }
                ]
            }}
        ]))


        


class CartQuerySet(QuerySet):
    pass
