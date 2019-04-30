gsutil cp -r gs://nyt-project/NYT_Stream .
cd NYT_Stream
mkdir data 
cd data
wget http://resources.mpi-inf.mpg.de/yago-naga/yago3.1/yagoFacts.tsv.7z .
sudo apt-get -y install p7zip-full
7z x yagoFacts.tsv.7z
gsutil cp yagoFacts.tsv gs://nyt-project/
cd ..
rm -r data
