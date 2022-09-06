# seeq-plot-digitizer
Digitization tools for Seeq

1. [Installation](#user-installation-seeq-data-lab)


## User Installation (Seeq Data Lab)

The latest build of the project can be found [here](https://github.com/eparsonnet93/seeq-plot-digitizer/dist) as a wheel file. The
file is published as a courtesy to the user, and it does not imply any obligation for support from the publisher.

1. Install the required external calculation scripts. 

    a. Manually download the [Plot Digitizer repository](https://github.com/eparsonnet93/seeq-plot-digitizer). To do so, click the green `Code` button, then Download ZIP

	<img src="imgs/zip_download.png" style="width:50%;">

    b. **Unzip** repository after downloading
    c. Open the `external_calculation` (*i.e.*, `seeq-plot-digitizer/external_calculation`) folder from the repository you just downloaded.
    d. **Move** (or copy and paste) the `PlotDigitizer` folder **and its contents** to the `python/user` external calculation folder on the machine where Seeq server is running, (this is typically `C:/Seeq/plugins/external-calculation/python/user/` or similar).

	<img src="imgs/external_calc_upload.png" style="width:40%;">


2. Create a **new** Seeq Data Lab project and open the **Terminal** window
3. Download the most recent wheel file and run `pip install seeq_plot_digitizer-<version>-py3-none-any.whl` replacing `<version>` with the version matching the `.whl` file you downloaded.
4. Run `python -m seeq.addons.plot_digitizer [--users <users_list> --groups <groups_list>]`
