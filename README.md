# Cardiovision
A Hardware 2 course Project. (08/05/2023)
    
## Description

Heart rate detection is an important area of study that involves the measurement and analysis of a person's heart rate. The heart rate is a critical indicator of the health and fitness level of a person and can provide valuable information about their physical condition.
Heart rate variability (HRV) accurately assesses the autonomic nervous system (ANS) function. HRV is widely used by health and wellbeing professionals to objectively measure physiological and mental stress and recovery. In addition, HRV is a commonly used tool in the research of different cardiovascular and metabolic diseases and their risk factors.

The aim was to build a working concept of an HRV device. The Cardiovision module is intended to be used in home or office environments either by the end users themselves or together with health and wellbeing professionals such as physiotherapists, nurses and medical doctors. 

The system consists of an Optical Sensor, Raspberry Pi Pico W, and an SSD1306 OLED display connected to a custom PCB framework board. The module could read sensor data and process it accordingly using a heart rate monitoring algorithm. The module could also communicate and process HRV data using the Kubios API software.

## Tools and Services

This project framework is supported by:
- [Pico W](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico)
- [Thonny IDE](https://thonny.org/)
- [Micropython](https://micropython.org/)
- [Kubios API](https://www.kubios.com/kubios-cloud/)


## Installation Support
Here's a quick and easy video on how to download and use Micropython in thonny
- [Link to the video](https://www.youtube.com/watch?v=_ouzuI_ZPLs)

Installing packages with [mpremote](https://docs.micropython.org/en/latest/reference/packages.html)

Check out the repository
Run webserver.cmd
Start a terminal and run:
```bash
mpremote  mip install --target / http://localhost:8000/
```
or if your pico is not found automatically:
```bash
mpremote connect <device> mip install --target / http://localhost:8000/
```
For more information and materials on the mip installation in Pico W process
-https://gitlab.metropolia.fi/lansk/picow-mip-example

## Authors and acknowledgement
- Project member & leader: Siddarth Singotam - Siddarth.Singotam@metropolia.fi
- Project member: Fatemeh Ramezan Nasab Shomia - Fatemeh.RamezanNasabShomia@metropolia.fi


The team members of the project appreciate lecturer Keijo Lansikkunnas, Metropolia UAS for teaching insights and conducting this project which is a part of 15 credits Hardware 2 course.


## Project status
The Project status is completed with all the fundamental requiremets. There is always room for development! be it in measurement methods, enhancement in accuracy, better user experience and etc... Feel free to fork the repository!
