# Release Notes

Version: 0.1.3
---

Version: 0.1.4
---

Renamed `external_calculation/PlotDigitizer/` to `external_calculation/PltDgz/`.

It is **very important** that once the `PltDgz` folder is created in the `users/` directory on the Seeq server, the folder is never deleted nor modified (*i.e.* no name changes allowed). One *can* modify the scripts contained therein, but **should never** modify the folder itself. This will cause problems with Seeq's ability to perform the external calc functions. 
