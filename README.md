# ADC/UART data capturing using xWR1843/AWR2243 with DCA1000

* for xWR1843: capture both raw ADC IQ data and processed UART point cloud data simultaneously in Python and C(pybind11) without mmwaveStudio
* for AWR2243: capture raw ADC IQ data in Python and C(pybind11) without mmwaveStudio


## Introduction

* The module is mainly divided into two parts, mmwave and fpga_udp:
  * mmwave is modified from [OpenRadar](https://github.com/PreSenseRadar/OpenRadar) and is used for configuration file reading, serial port data sending and receiving, raw data parsing, etc.
  * fpga_udp is modified from [pybind11 example](https://github.com/pybind/python_example) and [mmWave-DFP-2G](https://www.ti.com/tool/MMWAVE-DFP) and is used to receive high-speed raw data sent back by DCA1000 from the network port through the socket code written in C language. For the AWR2243, which has no on-chip DSP and ARM core, it also uses FTDI to send commands through USB to control the firmware writing and parameter configuration of AWR2243 using SPI.
* TI's millimeter-wave radars are mainly divided into two categories, those with only RF front-end and those with on-chip ARM and DSP/HWA. The former models include [AWR1243](https://www.ti.com/product/AWR1243), [AWR2243](https://www.ti.com/product/AWR2243), etc., and the latter models include [xWR1443](https://www.ti.com/product/IWR1443), [xWR6443](https://www.ti.com/product/IWR6443), [xWR1843](https://www.ti.com/product/IWR1843), [xWR6843](https://www.ti.com/product/IWR6843), [AWR2944](https://www.ti.com/product/AWR2944), etc.
  * For radar sensors with only RF front-end, control and configuration instructions are usually sent to them through the SPI/I2C interface, and raw data is output through the CSI2/LVDS interface. The SPI interface can be converted to USB protocol using the FTDI chip on the DCA1000 board and directly controlled by a computer. The data of the LVDS interface can also be collected by the FPGA on the DCA1000 board and converted to UDP packets for transmission over Ethernet. This warehouse implements all of the above operations.
  * For radar sensors with on-chip ARM and DSP, you can burn the control program, configure the radar sensor with on-chip ARM, process the raw data with on-chip DSP and obtain point cloud and other data, and transmit them through UART. In addition to being sent to the on-chip DSP, the raw data can also be configured to be output through the LVDS interface and collected using the FPGA on the DCA1000 board. This warehouse implements all the above operations. Of course, radar sensors with on-chip ARM and DSP also have SPI/I2C and other interfaces, which can also be used to configure the radar sensor, and convert SPI to USB through the FTDI on the DCA1000 board for computer control. [mmwaveStudio](https://www.ti.com/tool/MMWAVE-STUDIO) does this, but this warehouse has not yet implemented this method. You can refer to [mmWave-DFP](https://www.ti.com/tool/MMWAVE-DFP) to implement it yourself.


## Prerequisites

### Hardware
#### for xWR1843
* Connect the micro-USB port (UART) on the xWR1843 to your system
* Connect the xWR1843 to a 5V barrel jack
* Set power connector on the DCA1000 to RADAR_5V_IN
* boot in Functional Mode: SOP[2:0]=001
  * either place jumpers on pins marked as SOP0 or toggle SOP0 switches to ON, all others remain OFF
* Connect the RJ45 to your system
* Set a fixed IP to the local interface: 192.168.33.30
#### for AWR2243
* Connect the micro-USB port (FTDI) on the DCA1000 to your system
* Connect the AWR2243 to a 5V barrel jack
* Set power connector on the DCA1000 to RADAR_5V_IN
* Put the device in SOP0
  * Jumper on SOP0, all others disconnected
* Connect the RJ45 to your system
* Set a fixed IP to the local interface: 192.168.33.30

### Software
#### Windows
 - Microsoft Visual C++ 14.0 or greater is required.
   - Get it with "[Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)"(Standalone MSVC compiler) or "[Visual Studio](https://visualstudio.microsoft.com/downloads/)"(IDE) and choose "Desktop development with C++"
 - FTDI D2XX driver and DLL is needed. 
   - Download version [2.12.36.4](https://www.ftdichip.com/Drivers/CDM/CDM%20v2.12.36.4%20WHQL%20Certified.zip) or newer from [official website](https://ftdichip.com/drivers/d2xx-drivers/).
   - Unzip it and install `.\ftdibus.inf` by right-clicking this file.
   - Copy `.\amd64\ftd2xx64.dll` to `C:\Windows\System32\` and rename it to `ftd2xx.dll`. For 32-bit system, just copy `.\i386\ftd2xx.dll` to that directory.
#### Linux
 - `sudo apt install python3-dev`
 - FTDI D2XX driver and .so lib is needed. Download version 1.4.27 or newer from [official website](https://ftdichip.com/drivers/d2xx-drivers/) based on your architecture, e.g. [X86](https://ftdichip.com/wp-content/uploads/2022/07/libftd2xx-x86_32-1.4.27.tgz), [X64](https://ftdichip.com/wp-content/uploads/2022/07/libftd2xx-x86_64-1.4.27.tgz), [armv7](https://ftdichip.com/wp-content/uploads/2022/07/libftd2xx-arm-v7-hf-1.4.27.tgz), [aarch64](https://ftdichip.com/wp-content/uploads/2022/07/libftd2xx-arm-v8-1.4.27.tgz), etc.
 - Then you'll need to install the library:
   - ```
     tar -xzvf libftd2xx-arm-v8-1.4.27.tgz
     cd release
     sudo cp ftd2xx.h /usr/local/include
     sudo cp WinTypes.h /usr/local/include
     cd build
     sudo cp libftd2xx.so.1.4.27 /usr/local/lib
     sudo chmod 0755 /usr/local/lib/libftd2xx.so.1.4.27
     sudo ln -sf /usr/local/lib/libftd2xx.so.1.4.27 /usr/local/lib/libftd2xx.so
     sudo ldconfig -v
     ```


## Installation

 - clone this repository
 - for Windows:
   - `python3 -m pip install --upgrade pip`
   - `python3 -m pip install --upgrade setuptools`
   - `python3 -m pip install ./fpga_udp`
 - for Linux:
   - `sudo python3 -m pip install --upgrade pip`
   - `sudo python3 -m pip install --upgrade setuptools`
   - `sudo python3 -m pip install ./fpga_udp`


## Instructions for Use

#### General
1. First follow [Prerequisites](#prerequisites) to build the operating environment
2. Then follow [Installation](#installation) to install the library
3. If an error is reported during the operation of the module not mentioned, please check and add it yourself
#### For xWR1843
1. Burn the xwr18xx_mmw_demo program according to the instructions of [mmwave SDK](https://www.ti.com/tool/MMWAVE-SDK)
2. Use [mmWave_Demo_Visualizer](https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/ver/3.6.0/) to adjust the parameters and save the cfg configuration file
3. Open [captureAll.py](#captureallpy) and modify and fill in the cfg configuration file address and port number as required, then run and start collecting data
4. Open [testDecode.ipynb](#testdecodeipynb) or [testDecodeADCdata.mlx](#testdecodeadcdatamlx) to analyze the data just collected
5. If you are not satisfied with the parameters, you can continue to use [mmWave_Demo_Visualizer](https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/ver/3.6.0/) to adjust or use [testParam.ipynb](#testparamipynb) to modify and verify the rationality of the parameters
#### For AWR2243
1. Burn the firmware patch to the external flash (this operation only needs to be performed once, and the firmware will not be lost when restarting)
- for Windows: `python3 -c "import fpga_udp;fpga_udp.AWR2243_firmwareDownload()"`
- for Linux: `sudo python3 -c "import fpga_udp;fpga_udp.AWR2243_firmwareDownload()"`
- If you see "MSS Patch version [2. 2. 2. 0]", the burning is successful
2. Open [captureADC_AWR2243.py](#captureadc_awr2243py) and modify as needed and fill in the address of the txt configuration file and start collecting data
3. Open [testDecode_AWR2243.ipynb](#testdecode_awr2243ipynb) to parse the data just collected
4. If you are not satisfied with the parameters, you can use [testParam_AWR2243.ipynb](#testparam_awr2243ipynb) to modify and verify the rationality of the parameters


## Example

### ***captureAll.py***
Sample code for simultaneously collecting the IQ data sampled by the original ADC and the serial port data such as the point cloud pre-processed by the on-chip DSP (xWR1843 only).
#### 1. General process of collecting raw data
1. Reset radar and DCA1000 (reset_radar, reset_fpga)
2. Initialize radar through UART and configure corresponding parameters (TI, setFrameCfg)
3. (optional) Create a process to receive data processed by DSP on chip from serial port (create_read_process)
4. Send configuration fpga command through network port udp (config_fpga)
5. Send configuration record data packet command through network port udp (config_record)
6. (optional) Start serial port receiving process (only clear cache) (start_read_process)
7. Send start acquisition command through network port udp (stream_start)
8. Start UDP data packet receiving thread (fastRead_in_Cpp_async_start)
9. Start radar through serial port (theoretically, it can also be controlled through FTDI (USB to SPI), currently only implemented on AWR2243) (startSensor)
10. Wait for the UDP data packet receiving thread to end + parse the raw data (fastRead_in_Cpp_async_wait)
11. Save the raw data to a file for offline processing (tofile)
12. (optional) Send a stop acquisition command through the network port udp (stream_stop)
13. Turn off the radar through the serial port (stopSensor) or send a reset radar command through the network port (reset_radar)
14. (optional) Stop receiving serial port data (stop_read_process)
15. (optional) Parse the point cloud and other data processed by the on-chip DSP received from the serial port (post_process_data_buf)
#### 2. "*.cfg" millimeter wave radar configuration file requirements
- Default profile in Visualizer disables the LVDS streaming.
- To enable it, please export the chosen profile and set the appropriate enable bits.
- adcbufCfg needs to be set as follows, and the third parameter of lvdsStreamCfg needs to be set to 1. For details, see mmwave_sdk_user_guide.pdf
    - adcbufCfg -1 0 1 1 1
    - lvdsStreamCfg -1 0 1 0 
#### 3. "cf.json" data acquisition card configuration file requirements
- For specific information, please refer to TI_DCA1000EVM_CLI_Software_UserGuide.pdf
 - lvds Mode:
    - LVDS mode specifies the lane config for LVDS. This field is valid only when dataTransferMode is "LVDSCapture".
    - The valid options are
    - • 1 (4lane)
    - • 2 (2lane)
 - packet delay:
    - In default conditions, Ethernet throughput varies up to 325 Mbps speed in a 25-µs Ethernet packet delay. 
    - The user can change the Ethernet packet delay from 5 µs to 500 µs to achieve different throughputs.
       - "packetDelay_us":  5 (us)   ~   706 (Mbps)
       - "packetDelay_us": 10 (us)   ~   545 (Mbps)
       - "packetDelay_us": 25 (us)   ~   325 (Mbps)
       - "packetDelay_us": 50 (us)   ~   193 (Mbps)

### ***captureADC_AWR2243.py***
Example code for acquiring raw ADC sampled IQ data (AWR2243 only).
#### 1. General process of AWR2243 collecting raw data
1. Reset radar and DCA1000 (reset_radar, reset_fpga)
2. Initialize radar and configure corresponding parameters through SPI (AWR2243_init, AWR2243_setFrameCfg) (root permission is required under Linux)
3. Send configuration fpga command (config_fpga) through network port udp
4. Send configuration record data packet command (config_record) through network port udp
5. Send start acquisition command (stream_start) through network port udp
6. Start UDP data packet receiving thread (fastRead_in_Cpp_async_start)
7. Start radar through SPI (AWR2243_sensorStart)
8. 1. (optional, if numFrame==0, it must be there) Stop radar through SPI (AWR2243_sensorStop)
2. (optional, If numFrame==0, it cannot be present) Wait for the radar acquisition to end (AWR2243_waitSensorStop)
9. (optional, if numFrame==0, it must be present) Send the stop acquisition command through the network port udp (stream_stop)
10. Wait for the UDP data packet receiving thread to end + parse the original data (fastRead_in_Cpp_async_wait)
11. Save the original data to a file for offline processing (tofile)
12. Turn off the radar power and configuration file through SPI (AWR2243_poweroff)
#### 2. "mmwaveconfig.txt" millimeter wave radar configuration file requirements
- TBD
#### 3. "cf.json" data acquisition card configuration file requirements
- Same as above

### ***realTimeProc.py***
Sample code for real-time loop acquisition of raw ADC sampled IQ data and online processing (xWR1843 only).
#### 1. General process of acquiring raw data
1. Reset radar and DCA1000 (reset_radar, reset_fpga)
2. Initialize radar through UART and configure corresponding parameters (TI, setFrameCfg)
3. Send configuration fpga command through network port udp (config_fpga)
4. Send configuration record data packet command through network port udp (config_record)
5. Send start acquisition command through network port udp (stream_start)
6. Start radar through UART (theoretically, it can also be controlled through FTDI (USB to SPI), currently only implemented on AWR2243) (startSensor)
7. UDP **loop** receive data packets + parse raw data + real-time data processing (fastRead_in_Cpp, postProc)
8. Stop radar through UART (stopSensor)
9. Send stop acquisition command (fastRead_in_Cpp_thread_stop, stream_stop) through network port udp
#### 2. "mmwaveconfig.txt" millimeter wave radar configuration file requirements
- omitted
#### 3. "cf.json" data acquisition card configuration file requirements
- omitted

### ***realTimeProc_AWR2243.py***
Sample code for real-time loop acquisition of raw ADC sampled IQ data and online processing (AWR2243 only).
#### 1. General process of AWR2243 acquisition of raw data
- Omitted
#### 2. "mmwaveconfig.txt" millimeter wave radar configuration file requirements
- TBD
#### 3. "cf.json" data acquisition card configuration file requirements
- Omitted

### ***testDecode.ipynb***
The sample code for parsing raw ADC sampling data and serial port data (IWR1843 only) needs to be opened with Jupyter (it is recommended to install the Jupyter plug-in in VS Code).
#### 1. Parse the raw IQ data of the ADC received by LVDS
##### Use numpy to parse the raw IQ data of the ADC received by LVDS
- Load related libraries
- Set corresponding parameters
- Load the saved bin data and parse it
- Draw the time domain IQ waveform
- Calculate Range-FFT
- Calculate Doppler-FFT
- Calculate Azimuth-FFT
##### Use the functions provided by mmwave.dsp to parse the raw IQ data of the ADC received by LVDS
#### 2. Parse the point cloud, doppler and other data processed by the on-chip DSP received by UART
- Load related libraries
- Load the saved serial port parsing data
- Display the data set by the cfg file
- Display the on-chip processing time (can be used to determine whether the frame rate needs to be adjusted)
- Display the temperature of each antenna
- Display the data packet information
- Display the point cloud data
- Calculate the distance label and Doppler velocity label
- Display the range profile and noise floor profile
- Display the Doppler graph Doppler Bins
- Displays the Azimuth (Angle) Bins

### ***testDecode_AWR2243.ipynb***
The sample code for parsing raw ADC sampling data (AWR2243 only) needs to be opened with Jupyter (it is recommended to install the Jupyter plugin in VS Code).
#### 1. Parse the raw IQ data of the ADC received by LVDS
##### Parse the raw IQ data of the ADC received by LVDS using numpy
- Load the relevant library
- Set the corresponding parameters
- Load the saved bin data and parse it
- Draw the time domain IQ waveform
- Calculate Range-FFT
- Calculate Doppler-FFT
- Calculate Azimuth-FFT
 
### ***testParam.ipynb***
IWR1843 millimeter-wave radar configuration parameter rationality check needs to be opened with Jupyter (it is recommended to install the Jupyter plug-in in VS Code).
- Mainly check whether the parameter configuration of the cfg file required by the millimeter-wave radar and the cf.json file required by the DCA acquisition board is correct.
- The parameter constraints come from the device characteristics of IWR1843 itself. For details, please refer to the IWR1843 data sheet, mmwave SDK user manual, and chirp programming manual.
- If the parameters meet the constraints, the debugging information will be output in cyan, and if not, it will be output in purple or yellow.
- It should be noted that the constraints of this program are not completely accurate, so in special cases, even if all the parameters meet the constraints, there is a probability that it will not run normally.

### ***testParam_AWR2243.ipynb***
Same as above, rationality check of AWR2243 millimeter-wave radar configuration parameters.

### ***testDecodeADCdata.mlx***
MATLAB example code for parsing raw ADC sampling data
- Set corresponding parameters
- Load saved bin raw ADC data
- Reconstruct data format according to parameter parsing
- Draw time domain IQ waveform
- Calculate Range-FFT (1D FFT + static clutter filtering)
- Calculate Doppler-FFT
- 1D-CA-CFAR Detector on Range-FFT
- Calculate Azimuth-FFT

### ***testGtrack.py***
Use cppyy to test the gTrack algorithm written in C language. This algorithm is TI's group target tracking algorithm, which inputs point cloud and outputs trajectory.

The algorithm is designed to track multiple targets, where each target is represented by a set of measurement points.
Each measurement point carries detection informations, for example, range, azimuth, elevation (for 3D option), and radial velocity.

Instead of tracking individual reflections, the algorithm predicts and updates the location and dispersion properties of the group.

The group is defined as the set of measurements (typically, few tens; sometimes few hundreds) associated with a real life target.

Algorithm supports tracking targets in two or three dimensional spaces as a build time option:
 - When built with 2D option, algorithm inputs range/azimuth/doppler information and tracks targets in 2D cartesian space.
 - When built with 3D option, algorithm inputs range/azimuth/elevation/doppler information and tracks targets in 3D cartesian space.
#### Input/output
 - Algorithm inputs the Point Cloud. For example, few hundreds of individual measurements (reflection points).
 - Algorithm outputs a Target List. For example, an array of few tens of target descriptors. Each descriptor carries a set of properties for a given target.
 - Algorithm optionally outputs a Target Index. If requested, this is an array of target IDs associated with each measurement.
#### Features
 - Algorithm uses extended Kalman Filter to model target motion in Cartesian coordinates.
 - Algorithm supports constant velocity and constant acceleartion models.
 - Algorithm uses 3D/4D Mahalanobis distances as gating function and Max-likelihood criterias as scoring function to associate points with an existing track.


## Software Architecture

### TBD.py
TBD
