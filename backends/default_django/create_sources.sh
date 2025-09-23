max_jobs=10

for i in $(seq 1 170); do
  python manage.py seed_sources --count=1000 &
  sleep 5

  # If we already have $max_jobs running, wait for one to finish
  if (( $(jobs -r | wc -l) >= max_jobs )); then
    wait -n
  fi
done

# Wait for all remaining jobs to complete
wait
