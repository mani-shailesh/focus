"""
This module contains the custom Router(s) needed for this app.
"""

from rest_framework.routers import (Route, DynamicRoute, SimpleRouter)


class CustomDefaultRouter(SimpleRouter):
    """
    Default router for APIs that generates routes for GET, POST, PUT and DELETE
    methods.
    """
    routes = [
        # List route.
        Route(
            url=r'^{prefix}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]
