# -*- coding: utf-8 -*-

class Trend:
    """
    This model represents and holds information for a trending topic

    :ivar name: Name used for the trend
    :ivar is_promoted: *True* if trend is payed, *False* otherwise
    :ivar query: Query string for the trend
    :ivar url: URL to fetch this trend
    :ivar location: A :class:`libturpial.api.models.trend.TrendLocation` object with location information
    """

    def __init__(self, name, location=None, url=None, query=None, is_promoted=False):
        self.name = name
        self.location = location
        self.url = url
        self.query = query
        self.is_promoted = is_promoted


class TrendLocation:
    """
    This model represents the location of a trending topic

    :ivar name: Name for this location
    :ivar woeid: Yahoo! Where On Earth ID
    :ivar country: Country
    :ivar country_code: Country code
    :ivar parent_id: Parent WOEID
    :ivar placetype_code: Number that represents the PlaceType
    :ivar placetype_name: String for the PlaceType name
    """

    def __init__(self, name, woeid, country=None, country_code=None, parent_id=None,
            placetype_code=None, placetype_name=None):
        self.name = name
        self.woeid = woeid
        self.country = country
        self.country_code = country_code
        self.parent_id = parent_id
        self.placetype_code = placetype_code
        self.placetype_name = placetype_name
