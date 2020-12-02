<div align="center" markdown>
<img src="https://i.imgur.com/PW7XvLv.png"/>

# Create catalog with reference items

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Use</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/create-json-with-reference-items)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/create-json-with-reference-items)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/create-json-with-reference-items&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/create-json-with-reference-items&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/create-json-with-reference-items&counter=runs&label=runs&123)](https://supervise.ly)

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

YOu can go to Team Files -> `/reference_items` directory. All JSONs are saved there.

**Step 5:** All warnings and errors can be found in task log
