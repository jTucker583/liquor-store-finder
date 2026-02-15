# Liquor Store Finder

Uses OSM Data to find the optimal route from your current location to a set of coordinates with Valhalla. To run the Valhalla container, use
```bash
docker compose up
```

In order to get lat/long information for locations with the property *off license*, run the following api query (feel free to change the parameters):
```bash
curl "https://nominatim.openstreetmap.org/search?addressdetails=1&q=off+license+in+london&format=jsonv2&limit=5"
```

Adafruit code will go in the `microcontroller-code` directory. 