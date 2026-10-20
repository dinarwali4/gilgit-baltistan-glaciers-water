"""Write state.kml (camera + optional historical-imagery date) for the GB NetworkLink control.
RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
def write(lat, lon, rng, when=None, tilt=0, heading=0):
    ts = f'<gx:TimeStamp><when>{when}</when></gx:TimeStamp>' if when else ''
    open(os.path.join(HERE, 'state.kml'), 'w').write(
        f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">'
        f'<Document><name>v {lat} {lon} {rng} {when}</name><LookAt>{ts}<longitude>{lon}</longitude><latitude>{lat}</latitude>'
        f'<altitude>0</altitude><heading>{heading}</heading><tilt>{tilt}</tilt><range>{rng}</range><altitudeMode>relativeToGround</altitudeMode></LookAt></Document></kml>')
if __name__ == '__main__':
    a = sys.argv; write(float(a[1]), float(a[2]), float(a[3]), a[4] if len(a) > 4 and a[4] != '-' else None)
