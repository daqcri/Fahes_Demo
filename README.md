# FAHES: A Robust Disguised Missing Values Detector
Missing values are common in real-world data and may seriously affect data analytics such as simple statistics and hypothesis testing. Generally speaking, there are two types of missing values:  explicitly missing values (i.e. NULL values), and implicitly missing values (a.k.a. disguised missing values (DMVs)) such as "11111111" for a phone number and "Some college" for education. While detecting explicitly missing values is trivial, detecting DMVs is not; the essential challenge is the lack of standardization about how DMVs are generated. 

FAHES is a system for detecting DMVs from two angles: DMVs as detectable outliers and as detectable inliers.  For DMVs as outliers, we propose a syntactic outlier detection module for categorical data, and a density-based outlier detection module for numerical values. For DMVs as inliers, we propose a method that detects DMVs which follow either missing-completely-at-random or missing-at-random models. 


## Docker Installation
You need to install [Docker](https://www.docker.com/community-edition)
first, then proceed to the following instructions.

Get the code

    # clone using https
    git clone https://github.com/daqcri/Fahes_GUI.git
    
    cd Fahes_GUI
    
Build and run:

    docker build -t fahes_demo .
    docker run -it -p 8056:8056 fahes_demo

Run the demo:
    Open a web browser and write http://0.0.0.0:8056/ in the address bar.
