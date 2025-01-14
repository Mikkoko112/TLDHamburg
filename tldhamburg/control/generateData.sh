
cd scripts

if [ -e "../data/thingsLoc.json" ]; then
    echo "The thing data is present."
else
    echo "You need to retrieve the thing data." 
fi


if [ -e "../data/cleanedCoorsAverage.json" ]; then
    echo "The mean data is present."
else
    echo "Generating mean data"
    python3 makeMeadeanJsonData.py 
fi


if [ -e "../data/conjunctionsMean.json" ]; then
    echo "The vector data is present."
else

    echo "Generating vector data"
    echo "This can take a while"
    python3 vectorGenerator.py "1" "conjunctionsMean"
fi

if [ -e "../data/fetchAreasFullData.json" ]; then
    echo "The fetch area data is present."
else
    echo "Generating fetch area data"
    python3 vectorGenerator.py "0" "conjunctionsMean"
fi

if [ -e "../data/conjunctionsJoint.json" ]; then
    echo "The combined conjunction data is present."
else
    echo "Combining conjunction data"
    python3 makeBoxcombination.py
fi

if [ -e "../data/conjunctionDict.json" ]; then
    echo "The conjunction dict data is present."
else
    echo "Generating conjunction dict data."
    python3 trafficClass.py
fi

if [ -e "../data/vectorizationOnMeanPointInvert.json" ]; then
    echo "The vector data is present."
else
    echo "Generating vector data"
    python3 vectorGenerator.py 
fi
