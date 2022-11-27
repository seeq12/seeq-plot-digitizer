(install)=
# Installing Plot Digitizer

The latest build of the project can be found [here](https://pypi.org/project/seeq-plot-digitizer/) as a wheel file. The
file is published as a courtesy to the user, and it does not imply any obligation for support from the publisher.

**Requires 58 > Seeq >= R56** (updated versions are in the works.)


## Installation Instructions

Here is a short overview video explaining the installation of **Plot Digitzer in Seeq**
<details open="" class="details-reset border rounded-2">
  <summary class="px-3 py-2 border-bottom">
    <svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-device-camera-video">
    <path fill-rule="evenodd" d="M16 3.75a.75.75 0 00-1.136-.643L11 5.425V4.75A1.75 1.75 0 009.25 3h-7.5A1.75 1.75 0 000 4.75v6.5C0 12.216.784 13 1.75 13h7.5A1.75 1.75 0 0011 11.25v-.675l3.864 2.318A.75.75 0 0016 12.25v-8.5zm-5 5.075l3.5 2.1v-5.85l-3.5 2.1v1.65zM9.5 6.75v-2a.25.25 0 00-.25-.25h-7.5a.25.25 0 00-.25.25v6.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-4.5z"></path>
    </svg>
    <span aria-label="Video description _static/installation.mp4" class="m-1">Plot Digitizer in Seeq</span>
    <span class="dropdown-caret"></span>
  </summary>

<video src="_static/installation.mp4"
poster="_static/installation.png"
controls="controls" muted="muted" class="d-block rounded-bottom-2 width-fit" style="max-width:700px; background:
transparent url('_static/installation.png') no-repeat 0 0; -webkit-background-size:cover; -moz-background-size:cover;
-o-background-size:cover; background-size:cover;"
webboost_found_paused="true" webboost_processed="true">
</video>


1. Install the required external calculation scripts. 

    a. Manually download the [Plot Digitizer repository](https://github.com/seeq12/seeq-plot-digitizer). To do so, click the green `Code` button, then Download ZIP

	<img src="_static/zip_download.png" style="width:50%;">

    b. **Unzip** repository after downloading

    c. Open the `external_calculation` (*i.e.*, `seeq-plot-digitizer/external_calculation`) folder from the repository you just downloaded.

    d. **Move** (copy and paste) the `PltDgz` folder **and its contents** to the `python/user` external calculation folder on the remote agent or local machine where Seeq server is running (the external calculation folder is typically `C:/Seeq/plugins/external-calculation/python/user/` or similar).

	<img src="_static/external_calc_upload.png" style="width:40%;">

    **Very Important!** Once the `PltDgz` folder is created, be sure to never delete it. If you wish to make changes to the scripts contained therein, be sure to change the scripts themselves, never deleting, nor changing the name of the `PltDgz` folder!  

2. Create a **new** Seeq Data Lab project and open the **Terminal** window

3. (In SDL Terminal) Run `pip install seeq-plot-digitizer`

4. (In SDL Terminal) Run `python -m seeq.addons.plot_digitizer [--users <users_list> --groups <groups_list>]`. Then follow the prompt.
