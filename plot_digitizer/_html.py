instructions = ["""
    <div style="border:8px; border-style:solid; border-color:blue; padding: 1em;">
    <h3>1. Instructions: Upload an image.</h3>
    <p>Use the file upload to upload an image.</p>
    </div>
    """,
    """
    <div style="border:8px; border-style:solid; border-color:blue; padding: 1em;">
    <h3>2. Instructions: Calibrate the x-axis.</h3>
    <p>Select (click) a point on the x-axis of the plot image and manually enter the x-coordinate below.</p>
    </div>
    """,

    """
    <div style="border:8px; border-style:solid; border-color:yellow; padding: 1em;">
    <h3>3. Instructions: Calibrate the x-axis. (Point 2)</h3>
    <p>Select a second point (far from the first) on the x-axis of the plot image and manually enter the x-coordinate below.</p>
    </div>
    """,

    """
    <div style="border:8px; border-style:solid; border-color:purple; padding: 1em;">
    <h3>4. Instructions: Calibrate the y-axis.</h3>
    <p>Select a point on the y-axis of the plot image and manually enter the y-coordinate below.</p>
    </div>
    """,

    """
    <div style="border:8px; border-style:solid; border-color:green; padding: 1em;">
    <h3>5. Instructions: Calibrate the y-axis.</h3>
    <p>Select a second point (far from the first) on the y-axis of the plot image and manually enter the y-coordinate below.</p>
    </div>
    """,

][::-1]

curve_select_instructions = """
    <div style="border:8px; border-style:solid; border-color:orange; padding: 1em;">
    <h3>6. Instructions: Digitize the curve</h3>
    <p>Select points along the curve you wish to digitize. When done, click "Push To Seeq".</p>
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

tr:nth-child(even) {
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
    <td>X1</td>
    <td>x1point</td>
  </tr>
  <tr>
    <td>X2</td>
    <td>x2point</td>
  </tr>
  <tr>
    <td>Y1</td>
    <td>y1point</td>
  </tr>
  <tr>
    <td>Y2</td>
    <td>y2point</td>
  </tr>
</table>

</body>
</html>"""