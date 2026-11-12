# [2025] Sensofusion — Radio City

## Metadata

- **Year**: 2025
- **Challenge Partner**: Sensofusion
- **Original Historical Track**: Entertainment
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Millimeter-Wave Radar & High-Speed Machine Vision Sensors
- **Core Theme**: Physical propagation and multipath reflection simulation of radio waves from mobile radios, vehicles, and drones in 3D urban environments
- **Classification Rationale**: Although originally in the Entertainment track, it is initiated by counter-drone RF detection hardware manufacturer Sensofusion, focusing on physical modeling of propagation loss, reflection, and occlusion of radio waves among real physical urban buildings.

---

## Full Original Challenge Name

Radio City

## Challenge Description

Radio waves: They surround us and penetrate us; they bind the galaxy together. Show them to us.

Radio quietly powers much of what we do every day. This challenge offers an approachable way to grasp the basics. Take a 3D city model and make the invisible radio world visible. Show when and where radio transmitters can be heard — and when they fade away.

Using the provided 3D model of Hong Kong, demonstrate how radio waves travel. Place imaginary moving radio sources on the map: for example, people walking on the streets with mobile phones, cars driving on the streets or drones flying in the air – or come up with other sources. Then visualize how the radio transmission sent from these sources travel. You'll demonstrate how radio waves bounce from walls and how geographic obstacles will block radio. We’ll be looking for a physics-based simulation with creative visuals. You need a grasp of how radio behaves. Ideally, your visualization helps others learn too. Feel free to add interactivity and bring in other data, if they add to the story. There are several different ways to visualize radio waves. There is no single correct solution for this challenge; there are multiple creative ways of showing your results.

## Challenge Insights

Background and sources:
https://en.wikipedia.org/wiki/Radio https://en.wikipedia.org/wiki/Radio_wave 
https://en.wikipedia.org/wiki/Radio_propagation 
https://en.wikipedia.org/wiki/Line-of-sight_propagation
https://en.wikipedia.org/wiki/Ray_tracing_(graphics)
https://en.wikipedia.org/wiki/Free-space_path_loss
https://en.wikipedia.org/wiki/Computational_electromagnetics
https://en.wikipedia.org/wiki/ITU_terrain_model

Some visualization ideas:
https://wifi-solver.com/
https://wigle.net/
https://www.youtube.com/watch?v=qHLaFV86XmM

## Judging Criteria

We want to SEE what radio waves look like in a 3D city. Show us an interactive demo or make a video. Make it flashy. Wow us. Heck, turn it into a 3D game if you feel like it. Bring your idea to life with clarity, credibility, and polish, showing attention to detail.

## Prizes

The winning team, as chosen by the Sensofusion mentors, will be rewarded with DJI Mini 3 drones. Every member of the winning team will get a drone.

## Resources

City 3D Model: Hong Kong (tall buildings, interesting geography)
Unit: meters
Licenses:
JAXA https://earth.jaxa.jp/en/data/policy/
OpenStreetMap contributors https://www.openstreetmap.org/copyright

Extra details:
A python3 function to map a GPS coordinate to the model space:

def lat_lon_to_model_space(lat_lon):
    import math
    hong_kong_center_lat_lon = (22.268385798683745, 114.2578125)
    EARTH_RADIUS_METERS = 6371000
    delta_lat_deg = float(lat_lon[0]) - float(hong_kong_center_lat_lon[0])
    delta_lon_deg = float(lat_lon[1]) - float(hong_kong_center_lat_lon[1])

    meters_north = math.radians(delta_lat_deg) * EARTH_RADIUS_METERS

    cos_latitude = math.cos(math.radians(hong_kong_center_lat_lon[0]))
    radius_at_latitude = EARTH_RADIUS_METERS * cos_latitude
    meters_east = math.radians(delta_lon_deg) * radius_at_latitude

    # Flip signs to match your coordinate system
    return [meters_north, -meters_east]

Area bounds WGS84: {'north_lat': 22.59372606392931, 'south_lat': 21.943045533438177, 'west_lon': 113.90625, 'east_lon': 114.609375}

## About the Partner

The mission for Sensofusion is to secure personnel and infrastructure against drones with our Airfence product. Our systems are ready, tested and shipping. Sensofusion has governmental customers in Europe, North America, Middle East and Asia.
