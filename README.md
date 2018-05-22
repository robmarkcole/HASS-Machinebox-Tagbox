# HASS-Machinebox-Tagbox
Home-Assistant component for image classification (`tag` detection) using Machinebox.io [Tagbox](https://machinebox.io/docs/tagbox/recognizing-images)

Place the `custom_components` folder in your configuration directory (or add its contents to an existing custom_components folder).
Add to your HA config:
```yaml
image_processing:
  - platform: tagbox
    scan_interval: 5
    endpoint: localhost:8080
    source:
      - entity_id: camera.local_file
    tags:
      - food
```
Configuration variables:
- **endpoint**: the ip and port of your facebox instance
- **scan_interval**: [see the docs](https://www.home-assistant.io/docs/configuration/platform_options/#scan-interval), units seconds.
- **source**: Must be a camera.
- **tags**: An attribute is created for each entry in `tags`. The value of a tag is `0` if the tag is not detected, otherwise it is the confidence of detection. Use lowercase.

The component adds an `image_processing` entity. The state of the entity is the most likely tag in the image. The entity has an attribute `confident_tags` which is the total number of tags with a confidence greater than zero. The attribute `response_time` is the time in seconds for tagbox to perform processing on an image. Your `scan_interval` therefore should not be shorter than `response_time`.

The use of `tags` allows the creation of [template binary sensors](https://www.home-assistant.io/components/binary_sensor.template/) to indicate the presence of a tag in an image. For example:
```yaml
binary_sensor:
  - platform: template
    sensors:
      food:
        value_template: >-
          {{states.image_processing.tagbox_local_file.attributes.food > 0.5}}
```

<p align="center">
<img src="https://github.com/robmarkcole/HASS-Machinebox-Tagbox/blob/master/usage.png" width="800">
</p>

### Get Tagbox
Get/update Tagbox [from Dockerhub](https://hub.docker.com/r/machinebox/tagbox/) by running:
```
sudo docker pull machinebox/tagbox
```

#### Run Tagbox
[Run tagbox with](https://machinebox.io/docs/tagbox/recognizing-images):
```
MB_KEY="INSERT-YOUR-KEY-HERE"
sudo docker run -p 8080:8080 -e "MB_KEY=$MB_KEY" machinebox/tagbox
```
To limit tagbox to only custom tags add to the command `-e MB_TAGBOX_ONLY_CUSTOM_TAGS=true`

#### Limiting computation
[Image-classifier components](https://www.home-assistant.io/components/image_processing/) process the image from a camera at a fixed period given by the `scan_interval`. This leads to excessive computation if the image on the camera hasn't changed (for example if you are using a [local file camera](https://www.home-assistant.io/components/camera.local_file/) to display an image captured by a motion triggered system and this doesn't change often). The default `scan_interval` [is 10 seconds](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L27). You can override this by adding to your config `scan_interval: 10000` (setting the interval to 10,000 seconds), and then call the `scan` [service](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L62) when you actually want to process a camera image. So in my setup, I use an automation to call `scan` when a new motion triggered image has been saved and displayed on my local file camera.


## Local file camera
Note that for development I am using a [file camera](https://www.home-assistant.io/components/camera.local_file/).
```yaml
camera:
  - platform: local_file
    file_path: /images/food_photo.jpg
```
