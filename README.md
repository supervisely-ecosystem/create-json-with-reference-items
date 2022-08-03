<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48245050/182571333-b1698b1a-c41a-472d-8349-ecbdcc1bab04.png"/>

# Create catalog with reference items

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Use</a> •
  <a href="#JSON-Format">JSON Format</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/create-json-with-reference-items)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/create-json-with-reference-items)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/create-json-with-reference-items)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/create-json-with-reference-items)](https://supervise.ly)

</div>

## Overview

Classification and tagging tasks become complex when you deal with large items catalogs (hundreds or thousands of classes). This app transforms labeled project to JSON file with reference items: user has to define `reference tag name` (objects with this tag will be considered as reference) and `key tag name` (value of this tag on object is used to group reference items). 

For example, in retail labeling there may be thousands of unique  UPC codes ([Universal Product Code](https://en.wikipedia.org/wiki/Universal_Product_Code)). Labelers can assign tag `ref` to objects that have to be references. Multiple reference items for the same key (`UPC code`) are allowed. These reference objects will be grouped by the value of `key tag name` (e.g. `UPC code`).

If you already have items catagol we recommend you to convert it into the format described here: it will allow you to use other tagging/classification apps from [Ecosystem](https://ecosystem.supervise.ly/). 

<img src="https://i.imgur.com/OrLDCxg.png" width="450px"/>

## How To Use

**Step 1:** Add app to your team from Ecosystem if it is not there.

**Step 2:** Run app from the context menu of project

<img src="https://i.imgur.com/78nH5U0.png" width="500px"/>

**Step 3:** Fill in the fields in modal window and press `Run` button

**Step 4:** Wait until the task is finished, JSON will be created and saved to team file, find link to it in task output

<img src="https://i.imgur.com/xG3gRbz.png"/>

You can go to (1) Team Files -> (2) `/reference_items` directory. All JSONs are saved there (3).

<img src="https://i.imgur.com/qgmsVGA.png"/>

**Step 5:** All warnings and errors can be found in task log


## JSON Format

Here is the example:

```json
{
  "project_id": 1219,
  "project_name": "grocery_products",
  "project_url": "http://supervise.ly/projects/1219/datasets",
  "reference_tag_name": "ref",
  "key_tag_name": "UPC",
  "all_keys": [
    "123",
    "777"
  ],
  "references": {
    "123": [
      {
        "image_id": 368147,
        "image_name": "IMG_1836.jpeg",
        "dataset_name": "ds1",
        "image_preview_url": "http://supervise.ly/app/images/65/99/1219/1476#image-368147",
        "image_url": "http://supervise.ly/abcd.jpg",
        "UPC": "123",
        "bbox": [
          122,
          569,
          273,
          706
        ]
      },
      {
        "image_id": 368151,
        "image_name": "IMG_4451.jpeg",
        "dataset_name": "ds1",
        "image_preview_url": "http://supervise.ly/app/images/65/99/1219/1476#image-368151",
        "image_url": "http://supervise.ly/abcd.jpg",
        "UPC": "123",
        "bbox": [
          100,
          249,
          286,
          421
        ]
      }
    ],
    "777": [
      {
        "image_id": 368150,
        "image_name": "IMG_0748.jpeg",
        "dataset_name": "ds1",
        "image_preview_url": "http://supervise.ly/app/images/65/99/1219/1476#image-368150",
        "image_url": "http://supervise.ly/abcd.jpg",
        "UPC": "777",
        "bbox": [
          120,
          531,
          380,
          811
        ],
        "geometry": {
            "points": {
                "exterior": [
                    [
                        151,
                        211
                    ],
                    [
                        296,
                        390
                    ]
                ],
                "interior": []
            },
            "labelerLogin": "max",
            "updatedAt": "2020-11-24T15:16:26.618Z",
            "createdAt": "2020-11-24T15:15:31.892Z",
            "id": 6119695,
            "classId": 18318
        }
      }
    ]
  }
}
```

**Optional top level fields**, they are used for information puposes only (just in case):
- `project_id` (optional) - id of the original project
- `project_name` (optional) - name of the original project
- `project_url` (optional) - url to the original project
- `reference_tag_name` (optional) - this tag is used to find reference objects (in our example we used tag `ref`)

**Mandatory** fields:
- `key_tag_name` - tag that is on every reference object and is used to group them (in our example we used tag `UPC`)
- `all_keys` - list of all possible keys (names of the groups) - this array contains all used values of tag defined in `key_tag_name` field. In our example tag `UPC` has only two values: `123` and `777`    
- `references` - object (in python world it is also named as dictionary), object fields are from `all_keys` list, and value is the list of reference items

**Reference item** object (many optional fields are used only for information purposes):
- `image_id` (optional) - id of the image in Supervisely platform,
- `image_name` (optional)  - name of the image in Supervisely platform,
- `dataset_name` (optional) - name of the dataset where image is located
- `image_preview_url` (optional) URL to labeling the image in labeling interface
- `image_url` - direct url to the image (this url will be used to show and download image in other tagging/classification apps)
- `UPC` (on your custom case it may differ) - it is a value that is defined in field `key_tag_name` and the value of this fields is a name of group of reference objects
- `bbox` - object bounding box (can be an empty list or `null`) - [`top`, `left`, `bottom`, `right`] coordinates of the bounding box of the object. if the field is empty - then entire image is used as reference object
- `geometry` - object in Supervisely JSON format
