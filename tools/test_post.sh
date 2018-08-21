curl -i -v \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -X POST \
    --data '{"url": "test"}' \
    http://localhost:5000/shorten_url