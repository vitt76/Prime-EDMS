#!/bin/bash

echo "Building app..."
npm run build

echo "Starting preview server..."
npm run preview &
SERVER_PID=$!

sleep 5

echo "Running Lighthouse audit..."
npx @lhci/cli@latest autorun --config=./lighthouserc.json

kill $SERVER_PID

echo "Lighthouse report generated!"
