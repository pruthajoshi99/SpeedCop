import math


def get_latlng(lat, lng, dx, dy):
    r = 6378137
    # Coordinate offsets in radians
    lat, lng, dx, dy = float(lat), float(lng), float(dx), float(dy),
    dlat = dx / r
    dlng = dy / (r * math.cos(math.pi * lat / 180))

    # OffsetPosition, decimal degrees
    new_lat = lat + dlat * 180 / math.pi
    new_lng = lng + dlng * 180 / math.pi
    return new_lat, new_lng
