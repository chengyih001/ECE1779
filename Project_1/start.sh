echo "Start our AWS"
python3 /home/ubuntu/ECE1779-Project/front_end/run.py &
python3 /home/ubuntu/ECE1779-Project/memcache/run.py &
echo "The Server is Running2"
wait
