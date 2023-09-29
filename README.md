PYTHON
1. Install the python (https://www.python.org/downloads/). Don't forget to set a tik on "Add python.exe to the path"
2. Create new virtual environment with: python -m venv /path/to/new/virtual/environment
3. Activate the venv with /path/to/new/virtual/environment + /Scripts/Activate
4. Install all the needed libraries:
- pip install Appium-Python-Client
- pip install opencv-python
5. clone my repository via "git clone https://github.com/H0cok/Rummy_play"
or just download all files from mine repo to yours






ENVIRONMENT SETTINGS
1. First of all install appium with this npm command: (npm i --location=global appium). If you dont have nodejs/npm download it from here(https://nodejs.org/en/download). Also if npm command still doesn't go, restart the PC.

2. Follow the instructions on Appium website (https://appium.io/docs/en/2.1/quickstart/uiauto2-driver/)
Notes:
- To set new environment variable follow the commands (https://www.alphr.com/set-environment-variables-windows-11/)
- If Your pc doesn't see the adb commands, just add the root to adb directly to the Path. adb is located in "platform-tools" foulder. Sometimes it still doesn't help, then you can reboot PC or just run the abd directly, so in cmd go to platform-tools foulder and run adb 
- Tutorial recommends to run the emulator in android studio but if you want to save the memory you can use any other emulator or even your own android phone. Just make sure that options "usb debuggin"/"usb debuggin(Security settigs)", "Instull via USB"
 are all "on". You can find this options in "developer options" settings. This is how to turn on developer options:
    1. Go to Settings > System
    2. Touch About phone
    3. Touch the Build number field 7 times
    4. You will begin seeing a message as you approach the 7 touches
    5. Touch the back arrow once complete, and Developer options will now appear under Settings
3. After running "appium driver install uiautomator2" command, run this one to isntall image recognition plugin  "appium plugin install images"




Program running:
1. Go to cmd and run "appium --use-plugins=images" command to launch the server.

2. Open Android studio and connect your virtual device(or connect your phone or any other emulator)

3. Device should have the indian rummy game installed and launched. Also sturt the rummy game, so you can see cards and table on the screen
If you use emulator you can download apk here: https://www.apkmonk.com/app/com.eastudios.indianrummy/ 

4. Open another cmd tab and write "adb devices". Copy the name of the virtual device connected to your PC. If you cant run adb command run it directly from "platform-tools" foulder

5. Paste the name as python string into the deviceName variable in this part of code:
capabilities = dict(
    platformName="Android",
    automationName="uiautomator2",
    deviceName="d3e64cf2"
)



6. Run the  "main.py" file

