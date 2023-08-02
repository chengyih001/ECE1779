echo "Start our AWS"
python3 /home/ubuntu/ECE1779-project2/front_end/run.py &
python3 /home/ubuntu/ECE1779-project2/manager_app/run.py &
python3 /home/ubuntu/ECE1779-project2/auto_scaler/run.py &
echo "The Server is Running"
wait