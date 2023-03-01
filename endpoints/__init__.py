# Standard library imports
import os
from datetime import datetime
from requests import post
from requests import get

# Third party imports
from flask import Flask
from flask import request
from flask import g
from flask_restx import Namespace
from flask_restx import Resource as _Resource
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw

# Local application imports
import models


class Resource(_Resource):
    dispatch_requests = []

    def __init__(self, api=None, *args, **kwargs):
        super(Resource, self).__init__(api, args, kwargs)

    def dispatch_request(self, *args, **kwargs):
        tmp = request.args.to_dict()

        if request.method == "GET":
            request.args = tmp

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.endswith("__in")
            ]

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.startswith("$sort")
            ]

        if (
            request.method == "POST"
            and request.headers.get("Content-Type", "") == "application/json"
        ):
            json = request.get_json()

            for key, value in json.items():
                if isinstance(value, dict) and key in routes:
                    if "id" in value:
                        json[key] = value["id"]

                    else:
                        item = post(
                            "http://localhost:5000/api/{}".format(key), json=value
                        )
                        json[key] = item.json()["id"]

        for method in self.dispatch_requests:
            method(self, args, kwargs)

        return super(Resource, self).dispatch_request(*args, **kwargs)


api = Namespace("api", description="")
product_base = api.model("product_base", models.Product.base())
product_reference = api.model("product_reference", models.Product.reference())
product_full = api.model("product", models.Product.model(api))
basket_base = api.model("basket_base", models.Basket.base())
basket_reference = api.model("basket_reference", models.Basket.reference())
basket_full = api.model("basket", models.Basket.model(api))


@api.route("/product")
class ProductController(Resource):
    @api.marshal_list_with(api.models.get("product"), skip_none=True)
    def get(self):
        return models.Product.qry(request.args)

    @api.marshal_with(api.models.get("product"), skip_none=True)
    def post(self):
        return models.Product.post(request.get_json())

    @api.marshal_with(api.models.get("product"), skip_none=True)
    def put(self):
        return models.Product.put(request.get_json())

    @api.marshal_with(api.models.get("product"), skip_none=True)
    def patch(self):
        return models.Product.patch(request.get_json())


@api.route("/product/<product_id>")
class BaseProductController(Resource):
    @api.marshal_with(api.models.get("product"), skip_none=True)
    def get(self, product_id):
        return models.Product.objects.get(id=product_id).to_json()

    @api.marshal_with(api.models.get("product"), skip_none=True)
    def put(self, product_id):
        return models.Product.put({"id": product_id, **request.get_json()})

    @api.marshal_with(api.models.get("product"), skip_none=True)
    def patch(self, product_id):
        return models.Product.patch({"id": product_id, **request.get_json()})

    def delete(self, product_id):
        return models.Product.get(id=product_id).delete()


@api.route("/basket")
class BasketController(Resource):
    @api.marshal_list_with(api.models.get("basket"), skip_none=True)
    def get(self):
        return models.Basket.qry(request.args)

    @api.marshal_with(api.models.get("basket"), skip_none=True)
    def post(self):
        return models.Basket.post(request.get_json())

    @api.marshal_with(api.models.get("basket"), skip_none=True)
    def put(self):
        return models.Basket.put(request.get_json())

    @api.marshal_with(api.models.get("basket"), skip_none=True)
    def patch(self):
        return models.Basket.patch(request.get_json())


@api.route("/basket/<basket_id>")
class BaseBasketController(Resource):
    @api.marshal_with(api.models.get("basket"), skip_none=True)
    def get(self, basket_id):
        return models.Basket.objects.get(id=basket_id).to_json()

    @api.marshal_with(api.models.get("basket"), skip_none=True)
    def put(self, basket_id):
        return models.Basket.put({"id": basket_id, **request.get_json()})

    @api.marshal_with(api.models.get("basket"), skip_none=True)
    def patch(self, basket_id):
        return models.Basket.patch({"id": basket_id, **request.get_json()})

    def delete(self, basket_id):
        return models.Basket.get(id=basket_id).delete()


routes = list(set([x.urls[0].split("/")[1] for x in api.resources]))
