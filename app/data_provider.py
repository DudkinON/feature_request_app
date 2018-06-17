#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import User, ProductArea, Client, Request, session

query = session.query


def get_user_by_id(uid):
    """
    Returns user by user id

    :param uid: integer
    :return return: object
    """
    return query(User).filter_by(id=uid).first() or None


def get_user_by_email(email):
    """
    Returns user object

    :param email: string
    :return: object
    """
    return query(User).filter_by(email=email).first() or None


def create_user(email, password, first_name, last_name):
    """
    Creates a new user

    :param email: string
    :param password: string
    :param first_name: string
    :param last_name: string
    :return object:
    """
    user = User(email=email, first_name=first_name, last_name=last_name)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return user


def update_user(usr):
    """
    Update user and return new data

    :param usr: dictionary
    :return object:
    """

    user = session.query(User).filter_by(id=usr['uid']).first()
    if usr['password']:
        user.hash_password(usr['password'])
    if usr['email']:
        user.email = usr['email']
    if usr['first_name']:
        user.first_name = usr['first_name']
    if usr['last_name']:
        user.last_name = usr['last_name']

    session.commit()
    return user


def remove_user(uid):
    """
    Remove user by user id

    :param uid:
    :return void:
    """
    user = session.query(User).filter_by(id=uid).first()
    session.delete(user)
    session.commit()


def create_client(name):
    """
    Creates a new client in database

    :param name: string
    :return object:
    """
    client = Client(name=name)
    session.add(client)
    session.commit()
    return client


def get_clients():
    """
    Get all clients and serialize it

    :return object:
    """
    return [request.serialize for request in query(Client).all()]


def update_client(client_info):
    """
    Update client and return list of clients

    :param client_info: dict
    :return object:
    """
    client = session.query(Client).filter_by(id=client_info['id']).first()
    client.name = client_info['name']
    session.commit()
    return get_clients()


def remove_client(client_id):
    """
    Remove client by client id and return list of clients

    :param client_id: integer
    :return void:
    """
    client = query(Client).filter_by(id=client_id).first()
    session.delete(client)
    session.commit()
    return get_clients()


def client_exist(client_id):
    """
    Check client by id

    :param client_id: integer
    :return: bool
    """
    return True if query(Client).filter_by(id=client_id).first() else False


def create_product_area(name):
    """
    Creates a new product area

    :param name: string
    :return object:
    """
    product_area = ProductArea(name=name)
    session.add(product_area)
    session.commit()
    return product_area


def get_product_areas():
    """
    Get all product areas and serialize it

    :return object:
    """
    return [area.serialize for area in query(ProductArea).all()]


def product_area_exist(area_id):
    """
    Check product area by id

    :param area_id: integer
    :return: bool
    """
    return True if query(ProductArea).filter_by(id=area_id).first() else False


def update_product_area(area):
    """
    Update product area and return list of product areas

    :param area: dict
    :return object:
    """
    product_area = session.query(ProductArea).filter_by(id=area['id']).first()
    product_area.name = area['name']
    session.commit()
    return get_product_areas()


def remove_product_area(area_id):
    """
    Remove product area by id

    :param area_id: integer
    :return void:
    """
    product_area = session.query(ProductArea).filter_by(id=area_id).first()
    session.delete(product_area)
    session.commit()
    return get_product_areas()


def get_requests():
    """
    Get all requests and serialize them

    :return object:
    """
    requests = query(Request).filter_by(
        is_active=True).order_by(Request.client_priority.asc()).all()
    return [request.serialize for request in requests]


def get_completed_requests():
    """
    Get all completed requests and serialize them

    :return object:
    """
    requests = query(Request).filter_by(
        is_active=False).order_by(Request.client_priority.asc()).all()
    return [request.serialize for request in requests]


def completed_request(request_id):
    """
    Mark the request as completed

    :param request_id:
    :return:
    """
    current_request = query(Request).filter_by(id=request_id).first()
    current_request.is_active = False
    session.commit()
    return get_requests()


def create_request(data):
    """
    Creates a new request and return list of requests

    :param data: dictionary
    :return object:
    """
    new_request = Request(
        title=data['title'],
        description=data['description'],
        client=data['client'],
        client_priority=data['client_priority'],
        target_date=data['target_date'],
        product_area=data['product_area']
    )
    session.add(new_request)
    session.commit()
    return get_requests()


def update_request(request):

    current_request = query(Request).filter_by(id=request['id']).first()
    current_request.title = request['title']
    current_request.description = request['description']
    current_request.client = request['client']
    current_request.client_priority = request['client_priority']
    current_request.target_date = request['target_date']
    current_request.product_area = request['product_area']
    session.commit()

    return get_requests()
