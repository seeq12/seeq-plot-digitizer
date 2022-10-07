# Introduction to Plot Digitizer

Here is a short overview video of **Plot Digitzer in Seeq**
<details open="" class="details-reset border rounded-2">
  <summary class="px-3 py-2 border-bottom">
    <svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-device-camera-video">
    <path fill-rule="evenodd" d="M16 3.75a.75.75 0 00-1.136-.643L11 5.425V4.75A1.75 1.75 0 009.25 3h-7.5A1.75 1.75 0 000 4.75v6.5C0 12.216.784 13 1.75 13h7.5A1.75 1.75 0 0011 11.25v-.675l3.864 2.318A.75.75 0 0016 12.25v-8.5zm-5 5.075l3.5 2.1v-5.85l-3.5 2.1v1.65zM9.5 6.75v-2a.25.25 0 00-.25-.25h-7.5a.25.25 0 00-.25.25v6.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-4.5z"></path>
    </svg>
    <span aria-label="Video description _static/intro.mov" class="m-1">Plot Digitizer in Seeq</span>
    <span class="dropdown-caret"></span>
  </summary>

<video src="_static/intro.mov"
poster="_static/introduction.png"
controls="controls" muted="muted" class="d-block rounded-bottom-2 width-fit" style="max-width:700px; background:
transparent url('_static/introduction.png') no-repeat 0 0; -webkit-background-size:cover; -moz-background-size:cover;
-o-background-size:cover; background-size:cover;"
webboost_found_paused="true" webboost_processed="true">
</video>

**Plot Digitizer** helps to steamline analysis of data as it compares to theoretical or expected behavior, which is documented in paper or pdf form, by allowing the user to directly digitize curves from such design documents.  

<img src="_static/digitize.png" alt="image" width="100%">

Plot digitizer also allows the user to define "regions of interest" (ROIs), by selecting a region on the plot. Doing so will create a condition in [Seeq Workbench](https://www.seeq.com/product/workbench), selecting for data points that fall within the region. Plot digitizer seemlessly integrates with Seeq, creating sets of curves (formulas) and regions of interest (conditions) scoped to a parent asset. 

<img src="_static/roi.png" alt="image" width="100%">


Customer facilities contain many pieces of equipment with Original Equipment Manufacturer (OEM) design data documented in paper or pdf form.  One common type of data are design curves, which guarantee the performance of one or more parameters as they relate to another.

A common example are pump and compressor curves.  They usually compare a rotating equipment’s throughput to the expected head (pressure), efficiency, and power.  It is in the interest of the operating facility to keep equipment running within a certain region of the curve, as this can directly impact equipment reliability and power consumption.  Comparing equipment operation against design curves also allows engineers to assess losses in efficiency to justify either design changes or equipment overhaul.  This drives business decisions ranging from optimizing facilities to justifying capital investment. By obtaining a digital version of a design curve and overlaying it with data both in trend and XY plot, users can perform such analyses directly in Seeq.  Furthermore, by using conditions to identify periods of poor performance, one can easily help quantify the impact of off-design performance.

Once design curve data data are in Seeq, the actual opportunity to extract value begins.  Some examples of analyses that could be leveraged in the rotating equipment space:

1. Identify operation off design

    a. Is it worth considering an equipment redesign

    b. Quantify losses due to losses off-design to justify capital

    c. Exception based monitoring for fleet of assets

2. Compare actual efficiency to OEM efficiency for each operating point

    a. Drive maintenance planning and prioritization

3. Overlay curves with operating data to compare performance/efficiency gains of a new design curve to existing operation

    a. Helps justify investment into design tweaks or changes

4. Use tools like clustering to identify regions of operation that require investigation and auto-generate capsules for those periods of interest


The Plot Digitizer tool allows users to first calibrate axes and then pick points along an image to create a digital copy of a design curve (or region of interest).  The result is then pushed to a Seeq asset for use in monitoring and analysis.

## Plot Digitizer Terminology

- **Digitized Curve**: The formula in Seeq resulting from  digitization of a curve using the Plot Digitizer addon.
- **Region of Interest**: The condition in Seeq resulting from a region of interest definition using the Plot Digitzer tool.
- **Plot Image**: A `.png` file of the plot that the user wishes to digitize.
- **Curve Set (Region Set)**: A name given to a family of curves (or regions of interest). See {ref}`asset-hierarchy`
- **Curve Name (Region Name)**: A name give to a single digitized curve (or region or interest). See {ref}`asset-hierarchy`

(asset-hierarchy)=
### Asset hierarchy

```
Parent Asset
│   Signal 1 (x-axis)
│   Signal 2 (y-axis)
│
└───Curve Set 1
│   │   My Curve 1
│   │   My Curve 2
│   
└───Region Set 1
    │   My Region 1
```
  
