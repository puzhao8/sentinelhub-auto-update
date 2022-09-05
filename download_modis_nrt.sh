#!/bin/bash

GREP_OPTIONS=''

cookiejar=$(mktemp cookies.XXXXXXXXXX)
netrc=$(mktemp netrc.XXXXXXXXXX)
chmod 0600 "$cookiejar" "$netrc"
function finish {
  rm -rf "$cookiejar" "$netrc"
}

trap finish EXIT
WGETRC="$wgetrc"

prompt_credentials() {
    echo "Enter your Earthdata Login or other provider supplied credentials"
    read -p "Username (puzhao_agb): "
    username=${username:-puzhao_agb}
    read -s -p "Password: " 
    echo "machine urs.earthdata.nasa.gov login $username password $password" >> $netrc
    echo
}

exit_with_error() {
    echo
    echo "Unable to Retrieve Data"
    echo
    echo $1
    echo
    echo "https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1430.061.2022242155122.NRT.hdf"
    echo
    exit 1
}

prompt_credentials
  detect_app_approval() {
    approved=`curl -s -b "$cookiejar" -c "$cookiejar" -L --max-redirs 5 --netrc-file "$netrc" https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1430.061.2022242155122.NRT.hdf -w %{http_code} | tail  -1`
    if [ "$approved" -ne "302" ]; then
        # User didn't approve the app. Direct users to approve the app in URS
        exit_with_error "Please ensure that you have authorized the remote application by visiting the link below "
    fi
}

setup_auth_curl() {
    # Firstly, check if it require URS authentication
    status=$(curl -s -z "$(date)" -w %{http_code} https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1430.061.2022242155122.NRT.hdf | tail -1)
    if [[ "$status" -ne "200" && "$status" -ne "304" ]]; then
        # URS authentication is required. Now further check if the application/remote service is approved.
        detect_app_approval
    fi
}

setup_auth_wget() {
    # The safest way to auth via curl is netrc. Note: there's no checking or feedback
    # if login is unsuccessful
    touch ~/.netrc
    chmod 0600 ~/.netrc
    credentials=$(grep 'machine urs.earthdata.nasa.gov' ~/.netrc)
    if [ -z "$credentials" ]; then
        cat "$netrc" >> ~/.netrc
    fi
}

fetch_urls() {
  if command -v curl >/dev/null 2>&1; then
      setup_auth_curl
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        curl -f -b "$cookiejar" -c "$cookiejar" -L --netrc-file "$netrc" -g -o $stripped_query_params -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  elif command -v wget >/dev/null 2>&1; then
      # We can't use wget to poke provider server to get info whether or not URS was integrated without download at least one of the files.
      echo
      echo "WARNING: Can't find curl, use wget instead."
      echo "WARNING: Script may not correctly identify Earthdata Login integrations."
      echo
      setup_auth_wget
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        wget --load-cookies "$cookiejar" --save-cookies "$cookiejar" --output-document $stripped_query_params --keep-session-cookies -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  else
      exit_with_error "Error: Could not find a command-line downloader.  Please install curl or wget"
  fi
}

fetch_urls <<'EDSCEOF'
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1430.061.2022242155122.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1425.061.2022242155210.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1420.061.2022242154722.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1415.061.2022242150618.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1410.061.2022242150734.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1405.061.2022242150813.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1400.061.2022242150836.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1355.061.2022242150727.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1350.061.2022242151217.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1345.061.2022242151224.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1340.061.2022242151122.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1250.061.2022242141149.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1245.061.2022242141127.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1240.061.2022242140622.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1235.061.2022242132612.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1230.061.2022242132612.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1225.061.2022242132611.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1220.061.2022242132612.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1215.061.2022242132555.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1210.061.2022242133048.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1205.061.2022242133059.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1200.061.2022242132940.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1110.061.2022242123154.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1105.061.2022242122712.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1100.061.2022242114324.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1055.061.2022242114205.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1050.061.2022242114205.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1045.061.2022242114208.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1040.061.2022242114206.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1035.061.2022242114247.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1030.061.2022242114720.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1025.061.2022242114717.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.1020.061.2022242114659.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0930.061.2022242110049.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0925.061.2022242105429.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0920.061.2022242105146.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0915.061.2022242105134.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0910.061.2022242105132.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0905.061.2022242105050.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0900.061.2022242094456.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0855.061.2022242094508.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0850.061.2022242095007.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0845.061.2022242095050.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0840.061.2022242094938.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0755.061.2022242090104.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0750.061.2022242090126.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0745.061.2022242085404.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0740.061.2022242085105.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0735.061.2022242085049.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0730.061.2022242085056.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0725.061.2022242081134.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0720.061.2022242081135.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0715.061.2022242081325.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0710.061.2022242081621.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0705.061.2022242081616.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0615.061.2022242071532.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0610.061.2022242071443.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0605.061.2022242070930.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0600.061.2022242070743.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0555.061.2022242070745.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0550.061.2022242070734.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0545.061.2022242070739.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0540.061.2022242062446.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0535.061.2022242062845.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0530.061.2022242062832.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0525.061.2022242062759.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0435.061.2022242053308.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0430.061.2022242052924.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0425.061.2022242052508.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0420.061.2022242052418.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0415.061.2022242050506.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0410.061.2022242050349.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0405.061.2022242050451.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0400.061.2022242050439.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0355.061.2022242050942.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0350.061.2022242051008.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0345.061.2022242050852.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0255.061.2022242040033.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0250.061.2022242035623.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0245.061.2022242033932.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0240.061.2022242033836.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0235.061.2022242033851.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0230.061.2022242033927.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0225.061.2022242033830.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0220.061.2022242033908.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0215.061.2022242034610.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0210.061.2022242034525.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0205.061.2022242034441.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0115.061.2022242023018.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0110.061.2022242022216.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0105.061.2022242022026.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0100.061.2022242021935.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0055.061.2022242021953.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0050.061.2022242022033.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0045.061.2022242022050.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0040.061.2022242022049.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0035.061.2022242021947.NRT.hdf
https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/allData/61/MOD02QKM/2022/242/MOD02QKM.A2022242.0030.061.2022242011643.NRT.hdf
EDSCEOF