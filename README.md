Keep-away-from-covid-19
===========

動機與目的
-----------
因為疫情又開始嚴峻起來，因此想要在自家門口裝設自動檢測體溫的裝置，來分辨是否有發燒的人員進入該場所。


功能
-----------
* 是否戴口罩<br>
* 溫度偵測<br>
* 拍照<br>
* 破口通知<br>


使用資源：
-----------

|        設備名稱       | 數量 | 來源  |
|        :-----:       |:----:|:----:|
|     Raspberry pi 3   |  1   | moli |
|         攝影機        |  1   |何宏歷|
| MLX90614紅外測溫傳感器 |  1   |季昭儀|




python3.7.3<br>
tensorflow2.0.0<br>
detaset 來自 [prajnasb](https://github.com/prajnasb/observations/tree/master/experiements/data)<br>
主程式參考[這個](https://ithelp.ithome.com.tw/articles/10278344)做修改，增加溫度辨識、截圖、寄信與新增資料到資料庫的功能<br>

實作過程
-----------
從[這裡](https://github.com/prajnasb/observations/tree/master/experiements/data) 下載detaset，解壓縮<br>

* 先在電腦上使用tensorflow2.0.0訓練好model然後上傳到github<br>
  確認python環境中安裝好<br>
  * tensorflow2.0.0<br>
  * imutils<br>
  * matplotlib<br>
執行```train.py```
* 在 Putty 中設置 X11 
  * 下載並安裝 Putty
  * 下載並安裝 Xming
  * 啟動Xming服務器
  * 在保存的會話中保存你要連接的服務器在Putty中
  * 在putty中連到樹莓派
  * 在左側類別窗格中，單擊連接，然後單擊 SSH，然後單擊 X11。
    選中```Enable X11 forwarding```框
    在```X display location box```中輸入```localhost:0```<br>
    ![image](https://user-images.githubusercontent.com/74537568/149905950-16c17632-f164-4373-a730-2b0d89bc26c7.png)<br>
  * 左側轉到頂部並選擇sessions
  * 按save按鈕
  * 在樹莓派上輸入
    ```export DISPLAY=localhost:10.0```

<br><br>------------這是下面的事情都在樹莓派上做的分隔線------------<br><br>

* 在樹莓派上下把東西載下來
  ```
  git clone https://github.com/sabrinajih/Keep-away-from-covid-19.git<br>
  ```

* 攝影機直接使用usb接上
  ![](https://www.logitech.com/content/dam/logitech/en/products/webcams/c922/gallery/c922-gallery-1.png)<br>

* 設置啟用 I2C
  ```
  sudo raspi-config
  ```
  ![](https://circuitdigest.com/sites/default/files/inlineimages/u2/Enabling-I2C-from-Raspberry.jpg)<br>
  ![](https://circuitdigest.com/sites/default/files/inlineimages/u2/Raspberry-Pi-Configuration-.jpg)<br>

* 下載感測器要用的庫
  ```
  wget https://files.pythonhosted.org/packages/67/8a/443af31ff99cca1e30304dba28a60d3f07d247c8d410822411054e170c9c/PyMLX90614-0.0.3.tar.gz
  ```
  解壓縮
  ```
  tar -xf PyMLX90614-0.0.3.tar.gz
  ```
  下載其他東西跟安裝
  ```
  sudo apt-get install python-setuptools 
  sudo apt-get install -y i2c-tools
  sudo python3 setup.py install
  ```

* 接上MLX90614紅外測溫傳感器
  ![](https://circuitdigest.com/sites/default/files/circuitdiagram_mic/Raspberry-Pi-contactless-body-temperature-monitoring-with-MLX90614-Circuit-diagram.png)<br>
  輸入```i2cdetect -y 1```看看有沒有接成功，一切正常的話會像這個樣子
  ![](https://circuitdigest.com/sites/default/files/inlineimages/u2/Raspberry-Pi-Output.jpg)<br>
  
* 安裝mysql
  ```
  sudo apt-get install mariadb-serve
  ```
  登入
  ```
  sudo mysql -u root -p
  ```
  新增資料庫
  ```
  CREATE DATABASE `covid19`;
  ```
  設定新使用者與密碼
  ```
  CREATE USER 'lsa'@'localhost' IDENTIFIED BY 'lsa';
  ```
  設定使用者權限
  ```
  GRANT ALL PRIVILEGES ON covid19.* TO 'lsa'@'localhost';
  ```
  退出
  ```
  exit
  ```
  
* 修改```detect_webcam.py```
  * 讓它讀取感測到的溫度並記錄 
    先引入需要的東西
    ```
    from smbus2 import SMBus
    from mlx90614 import MLX90614
    ```
    ```
    bus = SMBus(1)
    time.sleep(1)
    sensor = MLX90614(bus, address=0x5A)
    ```
    ```
    if key == ord("p"):
      temp = sensor.get_object_1()
      print ("Temperature : ", temp)
    ```
  * 讓它在指定情況下截圖
    ```
     t = time.localtime(time.time()) 
     img_file = "./save_img/"
     img_name = time.strftime("%Y-%m-%d_%H-%M-%S",t)+".jpg" #檔名為截圖當下的時間
     cv2.imwrite(img_file+img_name, frame) #存到save_img/底下
    ```
  * 讓它將資料新增到資料庫
    ```
     try:
        connection = mysql.connector.connect(
                host='localhost',
                database='covid19',
                user='lsa',
                password='lsa')
        ifmask = 0
        if label == "Mask":
            ifmask = 1

        sql = "INSERT INTO wearmask(time, temperature, ifmask, image, image_name) VALUES (%s, %s, %s, %s, %s)"
        new_data = (time.strftime("%Y-%m-%d %H:%M:%S"), temp, ifmask, "image.jpg", img_name)
        cursor = connection.cursor()
        cursor.execute(sql, new_data)

        connection.commit()

    except Error as e:
        print("connect SQL fail", e)

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    ```
  * 寄信
    ```
    to = 's110321515@mail1.ncnu.edu.tw'
    gmail_user = 'rox873626@gmail.com'
    gmail_password = 'Axlaxl123'
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(gmail_user, gmail_password)
    today = datetime.datetime.now()
    my_temp = 'Temperature is %s' % temp
    msg = EmailMessage()
    msg['Subject'] = 'Epidemic privention breach detcted on %s' %today.strftime('%b %d %Y')
    msg['From'] = gmail_user
    msg['TO'] = to
    msg.set_content(my_temp)

    with open(img_file+img_name, 'rb') as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        file_name = img_name

    msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)

    smtpserver.sendmail(gmail_user, [to], msg.as_string())
    smtpserver.quit()
    ```
* 然後安裝php的相關東西
  ```
  sudo apt install php -y
  sudo apt install php-mysql -y
  sudo apt install phpmyadmin -y
  sudo apt install php-fpm
  ```
  這裡選Apache2<br>
  ![image](https://user-images.githubusercontent.com/74537568/149938917-d781e045-4d1d-4539-abb9-a1fabcb64daf.png)<br>
  Configuring phpmyadmin<br>
  ![image](https://user-images.githubusercontent.com/74537568/149939376-e2b631bb-36fd-4f07-9fcc-ef285e3bc346.png)<br>
  設密碼<br>
  ![image](https://user-images.githubusercontent.com/74537568/149939597-17c6a32c-20b5-466a-8896-f08ecfc9dd75.png)<br>

  
  在使用phpadmin的時候出了點問題一直不能打開資料<br>
  參考[這個](https://www.linuxquestions.org/questions/linux-software-2/phpmyadmin-error-warnings-what-should-i-do-4175680433/)做了改動
  ```
  sudo vim +614  /usr/share/phpmyadmin/libraries/sql.lib.php
  ```
  ```
  {
    返回 $GLOBALS['cfg']['RememberSorting']
        && ！($analyzed_sql_results['is_count']
            || $analyzed_sql_results['is_export']
            || $analyzed_sql_results['is_func']
            || $analyzed_sql_results['is_analysis'])
        && $analyzed_sql_results['select_from']
        && ((空($analyzed_sql_results['select_expr']))
            || (count($analyzed_sql_results['select_expr']) == 1) /**我改了這個*/            
                                                          ^補上這個右括號
                && ($analyzed_sql_results['select_expr'][0] == '*')) /** 這裡刪掉最後一個右括號 */
        && count($analyzed_sql_results['select_tables']) == 1; 
  }
  ```
  成功打開後長這樣<br>
  ![image](https://user-images.githubusercontent.com/74537568/149954888-aaf9cca5-e5a7-4792-919d-dab5e87733e2.png)<br>


  
使用方法
-----------
```
git clone https://github.com/sabrinajih/Keep-away-from-covid-19.git<br>
```
```
cd ./Keep-away-from-covid-19/mask_dector<br>
```
```
python3 detect_webcam.py <br>
```

* Demo<br>
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/PW2AmEfY65w/0.jpg)](https://www.youtube.com/watch?v=PW2AmEfY65w)

課堂應用
-----------
* 使用ssh連線到樹梅派
* 使用樹梅派寄信

分工表
-----------
季昭儀 實作其他、報告<br>
何宏歷 實作寄信、報告<br>
張光霖 實作寄信<br>
陳冠鈞 ppt撰寫、報告<br>

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
    * 但是 **pip install opencv-python  不香嗎**
* 攝影機顯示<br>
    * 解決方法：使用X11 <br>
    How to setup X11 forwarding in Putty using Xming<br>
    (1) Download and Install Putty on your PC<br>
    (2) Download and Install Xming on your PC<br>
    (3) Start Xming server<br>
    (4) Save the server you want to connect to in Putty in saved sessions<br>
    (5) Load the server you want to connect in putty<br>
    (6) In the left category pane, click on connections then SSH and then X11.<br>
    Check “Enable X11 forwarding” box<br>
    Enter “localhost:0” in “X display location box”<br>
    (7) In the left category pane go to top and select sessions<br>
    (8) Press save button<br>
    (9) Set following environment variable on the server<br>
    export DISPLAY=localhost:10.0<br>
    (10) Type xclock on the server and see if it appears<br>
    (11) If you get following error then execute the resolution steps.<br>
    [來源是這裡](https://tekyblog.wordpress.com/2012/02/02/how-to-setup-x11-forwarding-in-putty-using-xming/)[3]<br>

* 不小心裝了多個版本的python<br>
    * 注意安裝的lib到底裝到哪個版本去了<br>
    * 解決方法：<br>
    位置 -m pip install 要裝的東東(例： /usr/bin/python2.7 -m pip install dlib)<br>
* tensorflow版本問題<br>
    * 錯誤訊息：<br>
    E tensorflow/core/platform/hadoop/hadoop_file_system.cc:132] HadoopFileSystem load error: libhdfs.so: cannot open shared object file: No such file or directory<br>
    * 解決方法：<br>
    wget https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.0.0/tensorflow-2.0.0-cp37-none-linux_armv7l.whl<br>
    python3 -m pip uninstall tensorflow<br>
    python3 -m pip install tensorflow-2.0.0-cp37-none-linux_armv7l.whl<br>
    [來源是這裡](https://stackoverflow.com/questions/59505609/hadoopfilesystem-load-error-during-tensorflow-installation-on-raspberry-pi3)[4]
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
  [6] [MySQL/MariaDB 新增資料庫、建立使用者帳號與資料表指令教學](https://blog.gtwang.org/linux/mysql-create-database-add-user-table-tutorial/)
  [7] [[SOLVED] phpmyadmin error warnings What should I do?](https://www.linuxquestions.org/questions/linux-software-2/phpmyadmin-error-warnings-what-should-i-do-4175680433/)
 
