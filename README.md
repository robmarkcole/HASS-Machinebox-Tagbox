# HASS-Machinebox-Tagbox
Home-Assistant component for image classification using Machinebox.io [Tagbox](https://machinebox.io/docs/tagbox/recognizing-images)

Place the custom_components folder in your configuration directory (or add its contents to an existing custom_components folder).
Add to your HA config:
```yaml
image_processing:
  - platform: tagbox
    scan_interval: 10
    endpoint: localhost:8080
    source:
      - entity_id: camera.local_file
    tags:
      - kettle
      - keys
```
Configuration variables:
- **endpoint**: the ip and port of your facebox instance
- **scan_interval**: [see the docs](https://www.home-assistant.io/docs/configuration/platform_options/#scan-interval), units seconds.
- **source**: Must be a camera.
- **tags**: An attribute is created for each entry in `tags`. The value of a tag is `0` if the tag is not detected, otherwise it is the confidence of detection.

The use of `tags` allows the creation of [template binary sensors](https://www.home-assistant.io/components/binary_sensor.template/) to indicate the presence of a tag in an image. For example:
```yaml
binary_sensor:
  - platform: template
    sensors:
      kettle_image:
        value_template: >-
          {{states.image_processing.tagbox_local_file.attributes.kettle > 0.5}}
```

<p align="center">
<img src="https://github.com/robmarkcole/HASS-Machinebox-Tagbox/blob/master/usage.png" width="500">
</p>
