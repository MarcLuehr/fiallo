This is just a little project for experimenting. Target is to find IPv6 devices with zeroconf, allow an upload to a service and send TCP commands. Maybe I want to try saving the command to file, index them and allow to use them in a lua scirpter.  

Steps to build and run using docker:

# Build docker image "docker build -t local/pyqt5 ."
# edit "run.sh" - change volumes to your needs
# execute "run.sh" to start the container with infinite loop
# run "docker exec -it pyqt5 bash" to get a shell into the container

* "python3 fiallo.py" starts the program
* "designer fialloui.ui" starts the qt designer
* "pyuic5 -o fialloui.py fialloui.ui" regenerates the ui code
