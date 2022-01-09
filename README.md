Keep-away-from-covid-19
===========

動機與目的
-----------



功能
-----------
* 是否戴口罩<br>
* 溫度偵測<br>
* 拍照<br>
* 建資料庫 (照片、體溫、是否戴口罩(T or F) 、照片檔名、時間)<br>
* 破口通知<br>


使用資源：
-----------

|        設備名稱       | 數量 | 來源  |
|        :-----:       |:----:|:----:|
|     Raspberry pi 3   |  1   | moli |
|         攝影機        |  1   |何宏歷|
| MLX90614紅外測溫傳感器 |  1   |季昭儀|

![](https://circuitdigest.com/sites/default/files/circuitdiagram_mic/Raspberry-Pi-contactless-body-temperature-monitoring-with-MLX90614-Circuit-diagram.png)<br>
電路圖來自[這裡](https://circuitdigest.com/microcontroller-projects/iot-based-contactless-body-temperature-monitoring-using-raspberry-pi-with-camera-and-email-alert)<br>

python3.7.3<br>
tensorflow2.0.0<br>
detaset 來自 [prajnasb](https://github.com/prajnasb/observations/tree/master/experiements/data)[1]<br>


Implementation Process
-----------
Knowledge from Lecture
-----------
Installation
-----------
Usage
-----------
Job Assignment
-----------

遇到的問題
-----------
* opencv安裝<br>
   * 錯誤訊息類似於(來自於網路，原錯誤訊息未保存)<br>
   modules/viz/CMakeFiles/pch_Generate_opencv_viz.dir/build.make:62: recipe for target 'modules/viz/precomp.hpp.gch/opencv_viz_Release.gch' failed<br>
   make[2]: *** [modules/viz/precomp.hpp.gch/opencv_viz_Release.gch] Error 1<br>
   CMakeFiles/Makefile2:3186: recipe for target 'modules/viz/CMakeFiles/pch_Generate_opencv_viz.dir/all' failed<br>
   make[1]: *** [modules/viz/CMakeFiles/pch_Generate_opencv_viz.dir/all] Error 2<br>
   * 解決方法：<br>
   可能問題1：版本衝突
   可能問題2：有其他需要的東西沒有先安裝好
   最終使用[這個](https://robu.in/installing-opencv-using-cmake-in-raspberry-pi/)[2]安裝成功<br>
   * 建議：<br>
        * 如果曾經執行make指令然後失敗，在不確定問題的前提下建議直接將整個build資料夾刪掉然後重新cmake (略) 再重新make <br>
        * 如果執行 make -j4 (使用多核心) 然後卡再99% **好幾個小時** 建議還是ctrl+c 中斷後使用其他方法(例如make -j1 (單核心))來make <br>
        * 但半小時到一小時左右為正常時間<br>
    * pip install 
* 攝影機顯示<br>
    * 解決方法：<br>
    根據[這個步驟](https://tekyblog.wordpress.com/2012/02/02/how-to-setup-x11-forwarding-in-putty-using-xming/)[3]使用X11<br>

* 不小心裝了多個版本的python<br>
    * 注意安裝的lib到底裝到哪個版本去了<br>
    * 解決方法：<br>
    sudo 位置 -m pip install 要裝的東東(例：sudo /usr/bin/python2.7 -m pip install dlib)<br>
* tensorflow版本問題<br>
    * 錯誤訊息：<br>
    E tensorflow/core/platform/hadoop/hadoop_file_system.cc:132] HadoopFileSystem load error: libhdfs.so: cannot open shared object file: No such file or directory<br>
    * 解決方法：<br>
    [這裡](https://stackoverflow.com/questions/59505609/hadoopfilesystem-load-error-during-tensorflow-installation-on-raspberry-pi3)[4]
* hdf5 版本問題<br>
    * 錯誤訊息<br>
    File "/home/pi/.local/lib/python3.7/site-packages/tensorflow_core/python/keras/saving/hdf5_format.py", line 166, in load_model_from_hdf5<br>
    model_config =json.loads(model_config.decode('utf-8'))<br>
    AttributeError: 'str' object has no attribute 'decode'<br>
    * 解決方法：<br>
    pip3 install h5py==2.10 -i https://pypi.doubanio.com/simple

References
-----------
  [1] [[Day 27] 應用二：口罩下的人臉](https://ithelp.ithome.com.tw/articles/10278344)<br>
  [2] [Installing OpenCV using CMake in Raspberry Pi](https://robu.in/installing-opencv-using-cmake-in-raspberry-pi/)<br>
  [3] [How to setup X11 forwarding in Putty using Xming](https://tekyblog.wordpress.com/2012/02/02/how-to-setup-x11-forwarding-in-putty-using-xming/)<br>
  [4] [HadoopFileSystem load error during TensorFlow installation on raspberry pi3](https://stackoverflow.com/questions/59505609/hadoopfilesystem-load-error-during-tensorflow-installation-on-raspberry-pi3)<br>
  [5] [IoT Based Contactless Body Temperature Monitoring using Raspberry Pi with Camera and Email Alert](https://circuitdigest.com/microcontroller-projects/iot-based-contactless-body-temperature-monitoring-using-raspberry-pi-with-camera-and-email-alert)<br>
 
