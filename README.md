
This project was undertaken as a part of the esteemed National Level Hackathon. It addressed a critical challenge focusing on the need for a solution to recommend safe speed limits to drivers in school and hospital areas.

**Objective/Problem Statement**</br>
The objective was to develop a robust system capable of providing real-time recommendations for safe speed limits, thereby enhancing road safety and reducing the risk of accidents in these areas.

**Solution Proposed**</br>
We propose a feasible solution in the form of a hardware module that works on the principle of edge computing. The module estimates an ideal speed limit considering different factors. The estimated speed limit will then be notified to the vehicle driver. 
This will help in reducing the fatalities caused by over-speeding.

**How will it work?**</br>
- Raspberry Pi / Jetson Nano + Camera + Accelerometer Module to identify different road signs, density of people and to get the location of nearby schools and hospitals we have used GPS-GSM.
- Recommend a speed limit to the driver in real time
  + The system will work on two different computer paradigms: Edge Computing (Video Recognition)
  + Client-Server Computing (Nearby places, vehicles, accident zones)
- How speed is calculated
  + Video Recognition
    - Pedestrian + Vehicle Density and Traffic Sign Detection
  + Nearby Places
    - Schools + Hospitals
  + Accident Prone Areas
    - Check for accident prone areas
  + Nearby Vehicles
    - Check speed of nearby vehicles
- Created a web platform exclusively for traffic police administrators
- Offering comprehensive oversight of traffic violations by location, timestamp, and vehicle specifics.
- It includes multiple filters for data refinement.
- A dynamic dashboard presents detailed violation reports through heatmaps and bar graphs. Additionally, users have the option to download a PDF version of the violation list directly from the website.

**Flow Diagram**

<img width="1029" alt="Screen Shot 2023-10-09 at 11 33 45 AM" src="https://github.com/pruthajoshi99/SpeedCop/assets/122393647/ce585733-0301-4568-a953-b1741b17dc2a">
</br>
</br>

**Website**

</br>
1.Main Dashboard Page
</br>
</br>
<img width="945" alt="Screen Shot 2023-10-15 at 10 42 04 AM" src="https://github.com/pruthajoshi99/SpeedCop/assets/122393647/42a132fd-e183-4ba8-92ca-e5237c62b267">
</br>
</br>
2.Report Page
</br>
</br>
<img width="896" alt="Screen Shot 2023-10-15 at 10 42 25 AM" src="https://github.com/pruthajoshi99/SpeedCop/assets/122393647/3318b16c-e40a-4026-ac16-a1c1e9320596">
</br>
</br>
3. PDF Page
</br>
</br>
<img width="606" alt="Screen Shot 2023-10-15 at 10 42 34 AM" src="https://github.com/pruthajoshi99/SpeedCop/assets/122393647/76b1bf31-76fb-4a16-be2f-5bd7e6176c86">




