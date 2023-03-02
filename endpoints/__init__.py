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
cart_base = api.model("cart_base", models.Cart.base())
cart_reference = api.model("cart_reference", models.Cart.reference())
cart_full = api.model("cart", models.Cart.model(api))


@api.route("/product")
class ProductController(Resource):
    def get(self):
        return models.Product.qry(request.args)

    def post(self):
        return models.Product.post(request.get_json())

    def put(self):
        return models.Product.put(request.get_json())

    def patch(self):
        return models.Product.patch(request.get_json())


@api.route("/product/<product_id>")
class BaseProductController(Resource):
    def get(self, product_id):
        return models.Product.objects.get(id=product_id).to_json()

    def put(self, product_id):
        return models.Product.put({"id": product_id, **request.get_json()})

    def patch(self, product_id):
        return models.Product.patch({"id": product_id, **request.get_json()})

    def delete(self, product_id):
        return models.Product.get(id=product_id).delete()


@api.route("/cart")
class CartController(Resource):
    def get(self):
        return models.Cart.qry(request.args)

    def post(self):
        return models.Cart.post(request.get_json())

    def put(self):
        return models.Cart.put(request.get_json())

    def patch(self):
        return models.Cart.patch(request.get_json())


@api.route("/cart/<cart_id>")
class BaseCartController(Resource):
    def get(self, cart_id):
        return models.Cart.objects.get(id=cart_id).to_json()

    def put(self, cart_id):
        return models.Cart.put({"id": cart_id, **request.get_json()})

    def patch(self, cart_id):
        return models.Cart.patch({"id": cart_id, **request.get_json()})

    def delete(self, cart_id):
        return models.Cart.get(id=cart_id).delete()


routes = list(set([x.urls[0].split("/")[1] for x in api.resources]))
