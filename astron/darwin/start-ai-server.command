cd $(dirname $0 )
cd ../..
export DYLD_LIBRARY_PATH=`pwd`/Libraries.bundle
export DYLD_FRAMEWORK_PATH="Frameworks"

# Define some constants for our AI server:
MAX_CHANNELS=999999
STATESERVER=4002
ASTRON_IP="127.0.0.1:7010"
EVENTLOGGER_IP="127.0.0.1:7020"

# Get the user input:
printf "District name (DEFAULT: Nuttyboro): "
read -r DISTRICT_NAME
DISTRICT_NAME=${DISTRICT_NAME:-Nuttyboro}
printf "Base channel (DEFAULT: 401000000): "
read -r BASE_CHANNEL
BASE_CHANNEL=${BASE_CHANNEL:-401000000}

echo "==============================="
echo "Starting Toontown Infinite AI server..."
echo "District name: $DISTRICT_NAME"
echo "Base channel: $BASE_CHANNEL"
echo "Max channels: $MAX_CHANNELS"
echo "State Server: $STATESERVER"
echo "Astron IP: $ASTRON_IP"
echo "Event Logger IP: $EVENTLOGGER_IP"
echo "==============================="

while [ true ]
do
    python3 -m toontown.ai.ServiceStart --base-channel $BASE_CHANNEL \
                     --max-channels $MAX_CHANNELS --stateserver $STATESERVER \
                     --astron-ip $ASTRON_IP --eventlogger-ip $EVENTLOGGER_IP \
                     --district-name $DISTRICT_NAME
    sleep 5
done
