Home-Assistant custom component for image classification (`tag` detection) using Machinebox.io [Tagbox](https://machinebox.io/docs/tagbox/recognizing-images). The component adds an `image_processing` entity, where the state of the entity is the most likely tag in the image.

Place the `custom_components` folder in your configuration directory (or add its contents to an existing custom_components folder).

Add to your HA config:
```yaml
image_processing:
  - platform: tagbox
    ip_address: localhost
    port: 8080
    source:
      - entity_id: camera.local_file
```

Configuration variables:
- **ip_address**: the ip of your Tagbox instance
- **port**: the port of your Tagbox instance
- **source**: must be a camera.

<p align="center">
<img src="https://github.com/robmarkcole/HASS-Machinebox-Tagbox/blob/master/tagbox_usage.png" width="650">
</p>

### Tagbox
Get/update Tagbox [from Dockerhub](https://hub.docker.com/r/machinebox/tagbox/) by running:
```
sudo docker pull machinebox/tagbox
```

[Run Tagbox with](https://machinebox.io/docs/tagbox/recognizing-images):
```
MB_KEY="INSERT-YOUR-KEY-HERE"
sudo docker run -p 8080:8080 -e "MB_KEY=$MB_KEY" machinebox/tagbox
```
To limit tagbox to only custom tags, add to the command `-e MB_TAGBOX_ONLY_CUSTOM_TAGS=true`. Tagbox will be then only return and calculate custom tags, saving some compute resources.
```
sudo docker run -p 8080:8080 -e "MB_KEY=$MB_KEY" -e MB_TAGBOX_ONLY_CUSTOM_TAGS=true machinebox/tagbox
```
You should see a message on startup `pretrained tags are disabled, only custom tags will be returned`.

### Teaching tagbox
I've written a script to allow teaching tagbox from folders of images, the script is at https://github.com/robmarkcole/tagbox_python

#### Limiting computation
[Image-classifier components](https://www.home-assistant.io/components/image_processing/) process the image from a camera at a fixed period given by the `scan_interval`. This leads to excessive computation if the image on the camera hasn't changed (for example if you are using a [local file camera](https://www.home-assistant.io/components/camera.local_file/) to display an image captured by a motion triggered system and this doesn't change often). The default `scan_interval` [is 10 seconds](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L27). You can override this by adding to your config `scan_interval: 10000` (setting the interval to 10,000 seconds), and then call the `scan` [service](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L62) when you actually want to process a camera image. So in my setup, I use an automation to call `scan` when a new motion triggered image has been saved and displayed on my local file camera.


## Local file camera
Note that for development I am using a [file camera](https://www.home-assistant.io/components/camera.local_file/).
```yaml
camera:
  - platform: local_file
    file_path: /images/dog.jpg
```
