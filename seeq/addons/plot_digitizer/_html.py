instructions = ["""
    <div style="border:8px; border-style:solid; border-color:blue; padding: 1em;">
    <h3>1. Instructions: Upload an image.</h3>
    <p>Use the file upload to upload an image.</p>
    </div>
    """,
    """
    <div style="border:8px; border-style:solid; border-color:blue; padding: 1em;">
    <h3>2. Instructions: Calibrate the x-axis.</h3>
    <p>Click "Select" by X1 in the calibration section below. Next, click a point on the x-axis of the plot image. Then, manually enter the x-coordinate in the X1 text entry box and click "Approve". You will be able to edit these selections later.</p>
    </div>
    """,

    """
    <div style="border:8px; border-style:solid; border-color:yellow; padding: 1em;">
    <h3>3. Instructions: Calibrate the x-axis. (Point 2)</h3>
    <p>Select a second point (far from the first) on the x-axis of the plot image and manually enter the x-coordinate in X2. Click "Approve" when done.</p>
    </div>
    """,

    """
    <div style="border:8px; border-style:solid; border-color:purple; padding: 1em;">
    <h3>4. Instructions: Calibrate the y-axis.</h3>
    <p>Select a point on the y-axis of the plot image and manually enter the y-coordinate in Y1. Click "Approve" when done.</p>
    </div>
    """,

    """
    <div style="border:8px; border-style:solid; border-color:green; padding: 1em;">
    <h3>5. Instructions: Calibrate the y-axis.</h3>
    <p>Select a second point (far from the first) on the y-axis of the plot image and manually enter the y-coordinate in Y2. Click "Approve" when done.</p>
    </div>
    """,

][::-1]

curve_select_instructions = """
    <div style="border:8px; border-style:solid; border-color:orange; padding: 1em;">
    <h3>6. Instructions: Digitize the curve</h3>
    <p>Select points along the curve you wish to digitize. When done, click "Push To Seeq".</p>
    </div>
"""

done_instructions = """
    <div style="border:8px; border-style:solid; border-color:black; padding: 1em;">
    <h3>Done.</h3>
    <p>Done. You may digitize another curve / add a new region of interest (click "New Curve/ROI"), or, if done, close this window.</p>
    </div>
"""

region_of_interest_instructions = """
    <div style="border:8px; border-style:solid; border-color:red; padding: 1em;">
    <h3>6. Instructions: Define the region of interest</h3>
    <p>Select points defining the region of interest you are interested in. <b>The red dashed line is auto filled.</b>
    When done, click "Push To Seeq".</p>
    </div>
"""

calibration_table_template = """<html>
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 1px;
}

tr:nth-child(odd) {
  background-color: #dddddd;
}
</style>
</head>
<body>

<h2>Calibration Table</h2>

<table>
  <tr>
    <th>Point</th>
    <th>Selection</th>
  </tr>
  <tr>
    <td style="color:blue"><b>X1</b></td>
    <td style="color:blue">x1point</td>
  </tr>
  <tr>
    <td style="color:yellow"><b>X2</b></td>
    <td style="color:yellow">x2point</td>
  </tr>
  <tr>
    <td style="color:purple"><b>Y1</b></td>
    <td style="color:purple">y1point</td>
  </tr>
  <tr>
    <td style="color:green"><b>Y2</b></td>
    <td style="color:green">y2point</td>
  </tr>
</table>

</body>
</html>"""