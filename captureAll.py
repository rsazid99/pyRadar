import traceback
import time
from mmwave.dataloader import DCA1000
from mmwave.dataloader.radars import TI
import numpy as np
import datetime
'''
# General process of collecting raw data
1. Reset radar and DCA1000 (reset_radar, reset_fpga)
2. Initialize radar through UART and configure corresponding parameters (TI, setFrameCfg)
3. (optional) Create a process to receive data processed by DSP on chip from serial port (create_read_process)
4. Send configuration fpga command through network port udp (config_fpga)
5. Send configuration record data packet command through network port udp (config_record)
6. (optional) Start serial port receiving process (only clear cache) (start_read_process)
7. Send start acquisition command through network port udp (stream_start)
8. (optional) Start UDP data packet receiving thread (fastRead_in_Cpp_async_start)
9. Start radar through serial port (theoretically, it can also be controlled through FTDI (USB to SPI), currently only implemented on AWR2243) (startSensor)
10. Wait for the UDP data packet receiving thread to end + parse the original data (fastRead_in_Cpp_async_wait/fastRead_in_Cpp)
11. Save the original data to a file for offline processing (tofile)
12. (optional) Send a stop acquisition command (stream_stop) through the network port udp
13. Turn off the radar through the serial port (stopSensor) or send a reset radar command (reset_radar) through the network port
14. (optional) Stop receiving serial port data (stop_read_process)
15. (optional) Analyze the point cloud and other data received from the serial port that has been processed by the on-chip DSP (post_process_data_buf)

# "*.cfg" millimeter wave radar configuration file requirements
Default profile in Visualizer disables the LVDS streaming.
To enable it, please export the chosen profile and set the appropriate enable bits.
adcbufCfg needs to be set as follows, and the third parameter of lvdsStreamCfg needs to be set to 1. For details, see mmwave_sdk_user_guide.pdf
1. adcbufCfg -1 0 1 1 1
2. lvdsStreamCfg -1 0 1 0 

# "cf.json" Data acquisition card configuration file requirements
When using xWR1843, lvdsMode must be set to 2. xWR1843 only supports 2 LVDS lanes
For more information, please refer to TI_DCA1000EVM_CLI_Software_UserGuide.pdf
lvds Mode:
LVDS mode specifies the lane config for LVDS. This field is valid only when dataTransferMode is "LVDSCapture".
The valid options are
• 1 (4lane)
• 2 (2lane)
packet delay:
In default conditions, Ethernet throughput varies up to 325 Mbps speed in a 25-µs Ethernet packet delay. 
The user can change the Ethernet packet delay from 5 µs to 500 µs to achieve different throughputs.
"packetDelay_us":  5 (us)   ~   706 (Mbps)
"packetDelay_us": 10 (us)   ~   545 (Mbps)
"packetDelay_us": 25 (us)   ~   325 (Mbps)
"packetDelay_us": 50 (us)   ~   193 (Mbps)
'''
dca = None
radar = None

try:
    dca = DCA1000()

    # 1. Reset radar and DCA1000
    dca.reset_radar()
    dca.reset_fpga()
    print("wait for reset")
    time.sleep(1)

    # 2. Initialize the radar through UART and configure the corresponding parameters
    dca_config_file = "configFiles/cf.json" # Remember to set lvdsMode in cf.json to 2. xWR1843 only supports 2 LVDS lanes.
    radar_config_file = "configFiles/xWR1843_profile_3D.cfg" # Remember to set the third parameter of lvdsStreamCfg to 1 to enable LVDS data transmission
    numframes=10
    # Remember to change the port number. verbose=True will display all serial port commands and responses sent to the millimeter wave radar board.
    # radar = TI(cli_loc='COM4', data_loc='COM5',data_baud=921600,config_file=radar_config_file,verbose=True)     # for Windows
    radar = TI(cli_loc='/dev/ttyACM0', cli_baud=115200, data_loc='/dev/ttyACM1', data_baud=921600, config_file=radar_config_file, verbose=True)
    # After setting the number of frames, the radar will stop automatically. There is no need to send a stop command to the FPGA, but you still need to send a stop command to the radar.
    radar.setFrameCfg(numframes)

    # 3. Create a process to receive data processed by the on-chip DSP from the serial port
    radar.create_read_process(numframes)

    # 4. Send FPGA configuration instructions through the network port UDP
    # 5. Send configuration record data packet instructions through the network port UDP
    '''
    dca.sys_alive_check()             # Check whether the FPGA is connected and working properly
    dca.config_fpga(dca_config_file)  # Configuring FPGA Parameters
    dca.config_record(dca_config_file)# Configuring record parameters
    '''
    dca.configure(dca_config_file,radar_config_file)  # This function completes all the above operations
    # Press Enter to start collecting
    input("press ENTER to start capture...")

    # 6. Start the serial port receiving process (only clear the cache, only required when looping multiple acquisitions without running stop)
    radar.start_read_process()
    # 7. Send the start acquisition command via the network port UDP
    dca.stream_start()
    # 8. Start the UDP packet receiving thread
    # numframes_out,sortInC_out = dca.fastRead_in_Cpp_async_start(numframes,sortInC=True) # [Collection method 1] 1. Asynchronous call (requires C++17 and above compiler support)

    # 9. Start the radar via the serial port
    startTime = datetime.datetime.now()
    start = time.time()
    radar.startSensor()

    # 10. Wait for the UDP data packet receiving thread to end + parse the original data
    # data_buf = dca.fastRead_in_Cpp_async_wait(numframes_out,sortInC_out) # [Collection method 1] 2. Wait for the asynchronous thread to end
    data_buf = dca.fastRead_in_Cpp(numframes,sortInC=True) # [Collection method 2] Synchronous call (the package before the start of collection will be lost, but the compatibility is better)
    end = time.time()
    print("time elapsed(s):",end-start)

    # 11. Save the original data to a file
    filename="raw_data_"+startTime.strftime('%Y-%m-%d-%H-%M-%S')+".bin"
    data_buf.tofile(filename)
    print("file saved to",filename)
    
    # 12. DCA stops acquisition and automatically stops after setting the number of frames, without sending a stop command to the FPGA
    # dca.stream_stop()
    # 13. Turn off the radar via the serial port
    radar.stopSensor()
    # 14. Stop receiving serial port data
    radar.stop_read_process()

    # 15. Parse the point cloud and other data processed by the on-chip DSP received from the serial port. verbose=True will display detailed information of each frame during the processing.
    DSP_Processed_data=radar.post_process_data_buf(verbose=False)

    # The parsed point cloud data is in the variable DSP_Processed_data
    # print(DSP_Processed_data)

    # The unparsed serial port raw data is in the radar.byteBuffer variable
    # print(radar.byteBuffer)
    
    # Save the parsed serial port data to a file and load it using np.load('xxx.npy', allow_pickle=True)
    dspFileName = "DSP_data_"+startTime.strftime('%Y-%m-%d-%H-%M-%S')
    np.save(dspFileName, DSP_Processed_data)
    print(f'file saved to {dspFileName}.npy')

except Exception as e:
    traceback.print_exc()
finally:
    if dca is not None:
        dca.close()
    if radar is not None:
        radar.cli_port.close()
        # radar.data_port.close() # Stop receiving serial port data and automatically close when radar.stop_read_process() is used