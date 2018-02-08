#!/usr/bin/env bash

echo "-----------------------------------------"
echo "This script will do the following:"
echo "    - pull the specified tag from GitHub"
echo "    - clean and build the repo"
echo "    - copy the binary to the bin directory"
echo "    - fix up the symbolic link"
echo "------------------------------------------"

echo ""
echo ""
echo -n "Do you wish to continue (y/n): "
read n

if [ "$n" != "y" ];
then
   exit 1
fi

# Input
#   $1 - the tag to be pulled
#   $2 - key, lock or all


if [ "$1" == "" ];
then
    echo "You must specify a tag, e.g., pullbuild.sh v1.26"
    exit 1
fi

if [ "$2" == "" ] || [ "$2" == "key" ];
then 
    echo "Building default 'key'"
elif [ "$2" == "lock" ];
then
    echo "Building 'lock'"
elif [ "$2" == "all" ];
then
    echo "Building 'all'"
else
    echo "No valid build target specified"
    exit 1
fi


repo_name="kcb-$1"

cd ~/dev

echo "Pulling repository from github to /dev/$repo_name ..."
git clone https://github.com/BuzzSiler/keycodebox-key.git $repo_name
echo "Pull complete!"
echo "Changing to $repo_name directory"
cd $repo_name/Key

echo "Checking out tag $1 into branch 'localbuild' ..."
git checkout tags/$1 -b localbuild
echo "Checkout complete!"

echo "Cleaning build ..."
make clean
echo "Building ..."
qmake && make
echo "Build complete!"

alpha_tag="alpha-$1"

echo "Copying 'Alpha' binary to bin directory with tag appended ..."
cp Alpha ~/bin/$alpha_tag
echo "Copy complete!"
echo "Removing existing 'alpha' link ..."
sudo rm /usr/local/bin/alpha
echo "Link removed!"

echo "Creating new 'alpha' link to $alpha_tag ..."
sudo ln -s ~/bin/$alpha_tag /usr/local/bin/alpha
echo "Link created!"

ls -la /usr/local/bin/alpha

rm -rf ~/dev/$repo_name

echo "Done!"

cd ~/.
