# HASS-Machinebox-Tagbox
Home-Assistant component for image classification using Machinebox.io

https://machinebox.io/docs/tagbox/recognizing-images

Add to your config:
```yaml
image_processing:
  - platform: tagbox
#    scan_interval: 1000
    endpoint: localhost:8080
    source:
      - entity_id: camera.local_file
    tags:
      - kettle
      - keys
```

An attribute is created for each entry in `tags`. The value of a tag is `0` if the tag is not detected, otherwise it is the confidence of detection. This allows the creation of template binary sensors to indicate the presence of a tag in an image. 
