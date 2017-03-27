import django_filters
from . import models
from rest_framework import filters as rest_framework_filters


class MyClubsFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        only_my_clubs = bool(request.query_params.get('my_clubs', None))
        if only_my_clubs:
            queryset = queryset.filter(roles__members__id__contains=request.user.id)
        return queryset


class MyClubRolesFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows club members to see club roles of their clubs.
    """
    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(
            club__roles__members__id__contains=request.user.id,
        )
        return queryset
