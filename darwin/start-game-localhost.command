cd $(dirname $0 )
cd ..
export DYLD_LIBRARY_PATH=`pwd`/Libraries.bundle
export DYLD_FRAMEWORK_PATH="Frameworks"

# Get the user input:
printf "Username: "
read -r ttiUsername

# Export the environment variables:
export ttiUsername=$ttiUsername
export ttiPassword="password"
export TTI_PLAYCOOKIE=$ttiUsername
export TTI_GAMESERVER="127.0.0.1:7198"

echo "==============================="
echo "Starting Toontown Infinite..."
echo "Username: $ttiUsername"
echo "Gameserver: $TTI_GAMESERVER"
echo "==============================="

python3 -m toontown.toonbase.ClientStart
