echo "Removing existing alpha link ..."
sudo rm /usr/local/bin/alpha
echo "Complete!"
echo "Creating new alpha link to $1 ..."
sudo ln -s $1 /usr/local/bin/alpha
echo "Complete!"
ls -la /usr/local/bin/alpha
